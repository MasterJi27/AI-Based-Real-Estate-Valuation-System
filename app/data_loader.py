import pandas as pd
import numpy as np
import logging
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Setup logging
logger = logging.getLogger(__name__)

class DataLoader:
    def __init__(self):
        user = os.getenv('PGUSER')
        password = os.getenv('PGPASSWORD')
        host = os.getenv('PGHOST')
        port = os.getenv('PGPORT', '5432')
        database = os.getenv('PGDATABASE')
        self._engine = create_engine(
            f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}",
            connect_args={'sslmode': 'require', 'connect_timeout': 30}
        )

    def load_city_data(self, city):
        try:
            with self._engine.connect() as conn:
                df = pd.read_sql(
                    text("SELECT * FROM property_listings WHERE LOWER(city)=:city"),
                    conn, params={'city': city.lower()}
                )
            df['city'] = city
            df = self._clean_data(df)
            logger.info(f"{city}: Loaded {len(df)} rows from Neon.")
            return df
        except Exception as e:
            logger.error(f"Failed to load {city} from Neon: {e}")
            return pd.DataFrame()

    def load_all_data(self):
        try:
            with self._engine.connect() as conn:
                df = pd.read_sql(text("SELECT * FROM property_listings"), conn)
            df = self._clean_data(df)
            logger.info(f"Total rows loaded from Neon: {len(df)}")
            return df
        except Exception as e:
            logger.error(f"Failed to load data from Neon: {e}")
            return pd.DataFrame()

    def _clean_data(self, df):
        logger.info(f"Raw rows before cleaning: {len(df)}")
        # Remove rows with missing critical values
        df = df.dropna(subset=['price', 'area_sqft', 'bhk'])
        # Remove outliers (basic filtering)
        df = df[df['price'] > 0]
        df = df[df['area_sqft'] > 0]
        df = df[df['bhk'] > 0]
        # Ensure consistent data types for ML models
        for col in ['price', 'area_sqft', 'bhk']:
            df[col] = pd.to_numeric(df[col], errors='coerce').astype(np.float64)
        # Remove any rows that couldn't be converted
        df = df.dropna(subset=['price', 'area_sqft', 'bhk'])
        logger.info(f"Rows after cleaning: {len(df)}")
        return df

    def get_data_summary(self):
        combined_data = self.load_all_data()
        if combined_data.empty:
            logger.info("No valid data found for summary.")
            return None
        summary = combined_data.describe(include='all')
        logger.info(summary)
        return summary

    def get_districts_by_city(self, city, combined_data=None):
        if combined_data is not None:
            city_data = combined_data[combined_data['city'] == city]
        else:
            city_data = self.load_city_data(city)
        if city_data.empty:
            return []
        return sorted(city_data['district'].unique())

    def get_subdistricts_by_district(self, city, district, combined_data=None):
        if combined_data is not None:
            city_data = combined_data[combined_data['city'] == city]
        else:
            city_data = self.load_city_data(city)
        if city_data.empty:
            return []
        sub_df = city_data[city_data['district'] == district]
        return sorted(sub_df['sub_district'].unique())