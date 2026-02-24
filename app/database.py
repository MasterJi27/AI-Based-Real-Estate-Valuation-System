import psycopg2
import psycopg2.extras
import pandas as pd
import os
import logging
from urllib.parse import quote_plus
from typing import Optional, Dict, List, Any
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Setup logging
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.connection_params = {
            'host': os.getenv('PGHOST', 'localhost'),
            'database': os.getenv('PGDATABASE', 'realestate'),
            'user': os.getenv('PGUSER', 'postgres'),
            'password': os.getenv('PGPASSWORD') or '',
            'port': os.getenv('PGPORT', '5432'),
            'sslmode': os.getenv('PGSSLMODE', 'prefer')
        }
        _user = quote_plus(self.connection_params['user'])
        _pw = quote_plus(self.connection_params['password'])
        _host = self.connection_params['host']
        _port = self.connection_params['port']
        _db = self.connection_params['database']
        self._engine = create_engine(
            f"postgresql+psycopg2://{_user}:{_pw}@{_host}:{_port}/{_db}",
            connect_args={'sslmode': self.connection_params['sslmode'], 'connect_timeout': 30}
        )
        self.connection_available = False
        self.init_database()
    
    def get_connection(self):
        """Get database connection with automatic retry"""
        try:
            # Try to establish connection
            conn = psycopg2.connect(**self.connection_params)
            self.connection_available = True
            return conn
        except Exception as e:
            logger.warning(f"Database connection failed: {str(e)}")
            self.connection_available = False
            return None
    
    def init_database(self):
        """Initialize database tables"""
        conn = None
        try:
            conn = self.get_connection()
            if conn is None:
                logger.info("Database connection not available. Running without database.")
                return
            
            cursor = conn.cursor()
            
            # Create properties table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS properties (
                    id SERIAL PRIMARY KEY,
                    city VARCHAR(50) NOT NULL,
                    district VARCHAR(100) NOT NULL,
                    sub_district VARCHAR(100) NOT NULL,
                    area_sqft FLOAT NOT NULL,
                    bhk INTEGER NOT NULL,
                    property_type VARCHAR(50) NOT NULL,
                    furnishing VARCHAR(50) NOT NULL,
                    price FLOAT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Create predictions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(100),
                    city VARCHAR(50) NOT NULL,
                    district VARCHAR(100) NOT NULL,
                    sub_district VARCHAR(100) NOT NULL,
                    area_sqft FLOAT NOT NULL,
                    bhk INTEGER NOT NULL,
                    property_type VARCHAR(50) NOT NULL,
                    furnishing VARCHAR(50) NOT NULL,
                    predicted_price FLOAT NOT NULL,
                    ensemble_prediction FLOAT NOT NULL,
                    decision_tree_prediction FLOAT,
                    random_forest_prediction FLOAT,
                    xgboost_prediction FLOAT,
                    investment_advice VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Create user analytics table with UNIQUE session_id
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_analytics (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(100) UNIQUE,
                    page_views INTEGER DEFAULT 1,
                    predictions_made INTEGER DEFAULT 0,
                    favorite_city VARCHAR(50),
                    avg_property_price FLOAT,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            # Back-fill UNIQUE constraint if the table already existed without it
            cursor.execute("""
                DO $$ BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_constraint
                        WHERE conname = 'user_analytics_session_id_key'
                    ) THEN
                        ALTER TABLE user_analytics ADD CONSTRAINT user_analytics_session_id_key UNIQUE (session_id);
                    END IF;
                END $$;
            """)
            
            # Create market trends table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS market_trends (
                    id SERIAL PRIMARY KEY,
                    city VARCHAR(50) NOT NULL,
                    month INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    avg_price FLOAT NOT NULL,
                    median_price FLOAT NOT NULL,
                    price_per_sqft FLOAT NOT NULL,
                    total_properties INTEGER NOT NULL,
                    growth_rate FLOAT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(city, month, year)
                );
            """)
            
            # Create saved searches table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS saved_searches (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(100) NOT NULL,
                    search_name VARCHAR(100),
                    city VARCHAR(50) NOT NULL,
                    district VARCHAR(100),
                    sub_district VARCHAR(100),
                    min_area INTEGER,
                    max_area INTEGER,
                    min_bhk INTEGER,
                    max_bhk INTEGER,
                    property_type VARCHAR(50),
                    furnishing VARCHAR(50),
                    min_price FLOAT,
                    max_price FLOAT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            conn.commit()
            cursor.close()
            self.connection_available = True
            
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            self.connection_available = False
        finally:
            if conn:
                conn.close()
    
    def load_properties_to_db(self, df: pd.DataFrame):
        """Load property data from DataFrame to database"""
        try:
            conn = self.get_connection()
            if conn is None:
                logger.info("Database connection not available. Skipping data loading.")
                return False
            cursor = conn.cursor()
            
            # Clear existing data
            cursor.execute("DELETE FROM properties")
            
            # Insert new data using execute_batch for better performance
            data_tuples = [
                (row['city'], row['district'], row['sub_district'],
                 row['area_sqft'], row['bhk'], row['property_type'],
                 row['furnishing'], row['price'])
                for _, row in df.iterrows()
            ]
            
            psycopg2.extras.execute_batch(cursor, """
                INSERT INTO properties (city, district, sub_district, area_sqft, bhk, property_type, furnishing, price)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, data_tuples)
            
            conn.commit()
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error loading properties to database: {str(e)}")
            return False
    
    def save_prediction(self, session_id: str, property_data: Dict, predictions: Dict, 
                       ensemble_prediction: float, investment_advice: str):
        """Save prediction results to database"""
        try:
            conn = self.get_connection()
            if conn is None:
                return False
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO predictions (
                    session_id, city, district, sub_district, area_sqft, bhk, 
                    property_type, furnishing, predicted_price, ensemble_prediction,
                    decision_tree_prediction, random_forest_prediction, xgboost_prediction,
                    investment_advice
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                session_id, property_data['city'], property_data['district'],
                property_data['sub_district'], float(property_data['area_sqft']),
                int(property_data['bhk']), property_data['property_type'],
                property_data['furnishing'],
                float(predictions.get('predicted_price', ensemble_prediction)),
                float(ensemble_prediction),
                float(predictions.get('decision_tree', 0)), float(predictions.get('random_forest', 0)),
                float(predictions.get('xgboost', 0)), investment_advice
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error saving prediction: {str(e)}")
            return False
    
    def get_user_analytics(self, session_id: str) -> Dict:
        """Get user analytics data"""
        try:
            conn = self.get_connection()
            if conn is None:
                return {}
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT page_views, predictions_made, favorite_city, avg_property_price, last_activity
                FROM user_analytics WHERE session_id = %s
            """, (session_id,))
            
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if result:
                return {
                    'page_views': result[0],
                    'predictions_made': result[1],
                    'favorite_city': result[2],
                    'avg_property_price': result[3],
                    'last_activity': result[4]
                }
            else:
                return self.create_user_analytics(session_id)
                
        except Exception as e:
            logger.error(f"Error getting user analytics: {str(e)}")
            return {}
    
    def create_user_analytics(self, session_id: str) -> Dict:
        """Create new user analytics record"""
        conn = None
        try:
            conn = self.get_connection()
            if conn is None:
                return {}
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO user_analytics (session_id, page_views, predictions_made)
                VALUES (%s, 1, 0)
                ON CONFLICT (session_id) DO UPDATE
                    SET page_views = user_analytics.page_views + 1,
                        last_activity = CURRENT_TIMESTAMP
                RETURNING page_views, predictions_made, favorite_city, avg_property_price, last_activity
            """, (session_id,))
            
            result = cursor.fetchone()
            conn.commit()
            cursor.close()
            
            return {
                'page_views': result[0],
                'predictions_made': result[1],
                'favorite_city': result[2],
                'avg_property_price': result[3],
                'last_activity': result[4]
            }
            
        except Exception as e:
            logger.error(f"Error creating user analytics: {str(e)}")
            return {}
        finally:
            if conn:
                conn.close()
    
    def update_user_analytics(self, session_id: str, increment_predictions: bool = False,
                            favorite_city: str = None, avg_price: float = None):
        """Update user analytics — all changes in a single UPDATE to avoid race conditions"""
        conn = None
        try:
            conn = self.get_connection()
            if conn is None:
                return False
            cursor = conn.cursor()
            
            # Build a single UPDATE with all requested changes
            set_parts = [
                "page_views = page_views + 1",
                "last_activity = CURRENT_TIMESTAMP",
            ]
            params: list = []
            if increment_predictions:
                set_parts.append("predictions_made = predictions_made + 1")
            if favorite_city is not None:
                set_parts.append("favorite_city = %s")
                params.append(favorite_city)
            if avg_price is not None:
                set_parts.append("avg_property_price = %s")
                params.append(float(avg_price))
            params.append(session_id)
            
            cursor.execute(
                f"UPDATE user_analytics SET {', '.join(set_parts)} WHERE session_id = %s",
                params
            )
            conn.commit()
            cursor.close()
            return True
            
        except Exception as e:
            logger.error(f"Error updating user analytics: {str(e)}")
            return False
        finally:
            if conn:
                conn.close()
    
    def get_prediction_history(self, session_id: str, limit: int = 10) -> List[Dict]:
        """Get user's prediction history"""
        try:
            conn = self.get_connection()
            if conn is None:
                return []
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT city, district, sub_district, area_sqft, bhk, property_type, 
                       furnishing, predicted_price, investment_advice, created_at
                FROM predictions 
                WHERE session_id = %s 
                ORDER BY created_at DESC 
                LIMIT %s
            """, (session_id, limit))
            
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            
            history = []
            for row in results:
                history.append({
                    'city': row[0],
                    'district': row[1],
                    'sub_district': row[2],
                    'area_sqft': row[3],
                    'bhk': row[4],
                    'property_type': row[5],
                    'furnishing': row[6],
                    'predicted_price': row[7],
                    'investment_advice': row[8],
                    'created_at': row[9]
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting prediction history: {str(e)}")
            return []
    
    def get_market_statistics(self) -> Dict:
        """Get overall market statistics"""
        try:
            conn = self.get_connection()
            if conn is None:
                return {}
            cursor = conn.cursor()
            
            # Total properties by city
            cursor.execute("""
                SELECT city, COUNT(*) as count, AVG(price) as avg_price, 
                       AVG(price/area_sqft) as avg_price_per_sqft
                FROM properties 
                GROUP BY city
                ORDER BY avg_price DESC
            """)
            
            city_stats = cursor.fetchall()
            
            # Overall statistics
            cursor.execute("""
                SELECT COUNT(*) as total_properties, 
                       AVG(price) as avg_price,
                       MIN(price) as min_price,
                       MAX(price) as max_price,
                       AVG(area_sqft) as avg_area
                FROM properties
            """)
            
            overall_stats = cursor.fetchone()
            
            # Popular property types
            cursor.execute("""
                SELECT property_type, COUNT(*) as count, AVG(price) as avg_price
                FROM properties 
                GROUP BY property_type
                ORDER BY count DESC
            """)
            
            property_types = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return {
                'city_statistics': [
                    {
                        'city': row[0],
                        'total_properties': row[1],
                        'avg_price': row[2],
                        'avg_price_per_sqft': row[3]
                    } for row in city_stats
                ],
                'overall_statistics': {
                    'total_properties': overall_stats[0],
                    'avg_price': overall_stats[1],
                    'min_price': overall_stats[2],
                    'max_price': overall_stats[3],
                    'avg_area': overall_stats[4]
                },
                'property_types': [
                    {
                        'type': row[0],
                        'count': row[1],
                        'avg_price': row[2]
                    } for row in property_types
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting market statistics: {str(e)}")
            return {}
    
    def save_search(self, session_id: str, search_name: str, filters: Dict):
        """Save user search preferences"""
        if not filters.get('city'):
            logger.warning("save_search called without a city filter — skipping.")
            return False
        conn = None
        try:
            conn = self.get_connection()
            if conn is None:
                return False
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO saved_searches (
                    session_id, search_name, city, district, sub_district,
                    min_area, max_area, min_bhk, max_bhk, property_type,
                    furnishing, min_price, max_price
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                session_id, search_name, filters.get('city'),
                filters.get('district'), filters.get('sub_district'),
                filters.get('min_area'), filters.get('max_area'),
                filters.get('min_bhk'), filters.get('max_bhk'),
                filters.get('property_type'), filters.get('furnishing'),
                filters.get('min_price'), filters.get('max_price')
            ))
            
            conn.commit()
            cursor.close()
            return True
            
        except Exception as e:
            logger.error(f"Error saving search: {str(e)}")
            return False
        finally:
            if conn:
                conn.close()
    
    def get_saved_searches(self, session_id: str) -> List[Dict]:
        """Get user's saved searches"""
        try:
            conn = self.get_connection()
            if conn is None:
                return []
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT search_name, city, district, sub_district, min_area, max_area,
                       min_bhk, max_bhk, property_type, furnishing, min_price, max_price, created_at
                FROM saved_searches 
                WHERE session_id = %s 
                ORDER BY created_at DESC
            """, (session_id,))
            
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            
            searches = []
            for row in results:
                searches.append({
                    'search_name': row[0],
                    'city': row[1],
                    'district': row[2],
                    'sub_district': row[3],
                    'min_area': row[4],
                    'max_area': row[5],
                    'min_bhk': row[6],
                    'max_bhk': row[7],
                    'property_type': row[8],
                    'furnishing': row[9],
                    'min_price': row[10],
                    'max_price': row[11],
                    'created_at': row[12]
                })
            
            return searches
            
        except Exception as e:
            logger.error(f"Error getting saved searches: {str(e)}")
            return []
    
    def get_properties_by_filters(self, filters: Dict) -> pd.DataFrame:
        """Get properties matching filters"""
        # If database is not available, fall back to CSV data
        if not self.connection_available:
            return self._get_properties_from_csv_with_filters(filters)
        
        try:
            conn = self.get_connection()
            if conn is None:
                return self._get_properties_from_csv_with_filters(filters)
                
            cursor = conn.cursor()
            
            # Build dynamic query
            where_conditions = []
            params = []
            
            if filters.get('city'):
                where_conditions.append("city = %s")
                params.append(filters['city'])
            
            if filters.get('district'):
                where_conditions.append("district = %s")
                params.append(filters['district'])
            
            if filters.get('min_area'):
                where_conditions.append("area_sqft >= %s")
                params.append(filters['min_area'])
            
            if filters.get('max_area'):
                where_conditions.append("area_sqft <= %s")
                params.append(filters['max_area'])
            
            if filters.get('min_bhk'):
                where_conditions.append("bhk >= %s")
                params.append(filters['min_bhk'])
            
            if filters.get('max_bhk'):
                where_conditions.append("bhk <= %s")
                params.append(filters['max_bhk'])
            
            if filters.get('property_type'):
                where_conditions.append("property_type = %s")
                params.append(filters['property_type'])
            
            if filters.get('furnishing'):
                where_conditions.append("furnishing = %s")
                params.append(filters['furnishing'])
            
            if filters.get('min_price'):
                where_conditions.append("price >= %s")
                params.append(filters['min_price'])
            
            if filters.get('max_price'):
                where_conditions.append("price <= %s")
                params.append(filters['max_price'])
            
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            
            query = f"""
                SELECT city, district, sub_district, area_sqft, bhk, property_type, furnishing, price
                FROM properties 
                WHERE {where_clause}
                ORDER BY price DESC
                LIMIT 100
            """
            
            df = pd.read_sql_query(query, self._engine, params=params)
            
            cursor.close()
            conn.close()
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting filtered properties: {str(e)}")
            # Fall back to CSV data on database error
            return self._get_properties_from_csv_with_filters(filters)
    
    def _get_properties_from_csv_with_filters(self, filters: Dict) -> pd.DataFrame:
        """Get properties from CSV files with filters applied"""
        try:
            from data_loader import DataLoader
            loader = DataLoader()
            data = loader.load_all_data()
            
            if data is None or data.empty:
                return pd.DataFrame()
            
            # Data already has the correct column names, just apply filters
            filtered_data = data.copy()
            
            if filters.get('city'):
                filtered_data = filtered_data[filtered_data['city'] == filters['city']]
            
            if filters.get('district'):
                filtered_data = filtered_data[filtered_data['district'] == filters['district']]
            
            if filters.get('min_area'):
                filtered_data = filtered_data[filtered_data['area_sqft'] >= filters['min_area']]
            
            if filters.get('max_area'):
                filtered_data = filtered_data[filtered_data['area_sqft'] <= filters['max_area']]
            
            if filters.get('min_bhk'):
                filtered_data = filtered_data[filtered_data['bhk'] >= filters['min_bhk']]
            
            if filters.get('max_bhk'):
                filtered_data = filtered_data[filtered_data['bhk'] <= filters['max_bhk']]
            
            if filters.get('property_type'):
                filtered_data = filtered_data[filtered_data['property_type'] == filters['property_type']]
            
            if filters.get('furnishing'):
                filtered_data = filtered_data[filtered_data['furnishing'] == filters['furnishing']]
            
            if filters.get('min_price'):
                filtered_data = filtered_data[filtered_data['price'] >= filters['min_price']]
            
            if filters.get('max_price'):
                filtered_data = filtered_data[filtered_data['price'] <= filters['max_price']]
            
            # Select relevant columns and sort by price
            result_columns = ['city', 'district', 'sub_district', 'area_sqft', 'bhk', 'property_type', 'furnishing', 'price']
            available_columns = [col for col in result_columns if col in filtered_data.columns]
            
            result = filtered_data[available_columns].sort_values('price', ascending=False).head(100)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting properties from CSV with filters: {str(e)}")
            return pd.DataFrame()