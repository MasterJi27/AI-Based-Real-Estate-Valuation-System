import pandas as pd
import numpy as np
import logging
from pathlib import Path

# Setup logging
logger = logging.getLogger(__name__)

class DataLoader:
    def __init__(self):
        # Get the current directory and construct the datasets path
        current_dir = Path(__file__).parent
        self.datasets_path = current_dir / 'datasets'

    def load_city_data(self, city):
        file_path = self.datasets_path / f"{city.lower()}_properties.csv"
        if not file_path.exists():
            logger.info(f"Data file not found for {city}: {file_path}")
            return pd.DataFrame()
        df = pd.read_csv(file_path)
        df['city'] = city  # Add city column for consistency
        df = self._clean_data(df)
        logger.info(f"{city}: Loaded {len(df)} valid rows.")
        return df

    def load_all_data(self):
        cities = ['Mumbai', 'Delhi', 'Gurugram', 'Noida', 'Bangalore']
        all_data = []
        for city in cities:
            df = self.load_city_data(city)
            if not df.empty:
                all_data.append(df)
        if all_data:
            combined_data = pd.concat(all_data, ignore_index=True)
            logger.info(f"Total valid rows loaded: {len(combined_data)}")
            return combined_data
        else:
            logger.info("No valid data found. Please ensure CSV files are properly formatted.")
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