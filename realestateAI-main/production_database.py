"""
Production Database Management
Enhanced database operations for production environment.
"""
import psycopg2
import pandas as pd
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from production_config import config

class ProductionDatabaseManager:
    """Production-grade database management with enhanced features"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.connection = None
        self.connection_pool = None
        self._connect()
    
    def _connect(self):
        """Establish database connection with production settings"""
        try:
            database_url = config.get_database_url()
            if database_url and database_url.startswith('postgresql://'):
                self.connection = psycopg2.connect(database_url)
                self.logger.info("Database connection established successfully")
            else:
                self.logger.info("Database connection not available. Running without database.")
        except Exception as e:
            self.logger.error(f"Database connection failed: {str(e)}")
            self.connection = None
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> Optional[List]:
        """Execute SQL query with error handling"""
        if not self.connection:
            self.logger.warning("No database connection available")
            return None
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                if query.strip().upper().startswith('SELECT'):
                    return cursor.fetchall()
                else:
                    self.connection.commit()
                    return cursor.rowcount
        except Exception as e:
            self.logger.error(f"Query execution failed: {str(e)}")
            self.connection.rollback()
            return None
    
    def insert_property_data(self, property_data: Dict) -> bool:
        """Insert property data into database"""
        if not self.connection:
            return False
        
        try:
            query = """
            INSERT INTO properties (city, district, sub_district, area_sqft, bhk, 
                                  property_type, furnishing, price, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                property_data.get('city'),
                property_data.get('district'),
                property_data.get('sub_district'),
                property_data.get('area_sqft'),
                property_data.get('bhk'),
                property_data.get('property_type'),
                property_data.get('furnishing'),
                property_data.get('price'),
                datetime.now()
            )
            
            result = self.execute_query(query, params)
            return result is not None and result > 0
            
        except Exception as e:
            self.logger.error(f"Failed to insert property data: {str(e)}")
            return False
    
    def get_properties_by_filters(self, filters: Dict) -> pd.DataFrame:
        """Get properties based on filters"""
        if not self.connection:
            self.logger.info("Database connection not available. Skipping data loading.")
            return pd.DataFrame()
        
        try:
            base_query = "SELECT * FROM properties WHERE 1=1"
            params = []
            
            if 'city' in filters:
                base_query += " AND city = %s"
                params.append(filters['city'])
            
            if 'min_price' in filters:
                base_query += " AND price >= %s"
                params.append(filters['min_price'])
            
            if 'max_price' in filters:
                base_query += " AND price <= %s"
                params.append(filters['max_price'])
            
            result = self.execute_query(base_query, tuple(params))
            if result:
                columns = ['id', 'city', 'district', 'sub_district', 'area_sqft', 
                          'bhk', 'property_type', 'furnishing', 'price', 'created_at']
                return pd.DataFrame(result, columns=columns)
            
        except Exception as e:
            self.logger.error(f"Failed to get properties: {str(e)}")
        
        return pd.DataFrame()
    
    def save_prediction(self, session_id: str, prediction_data: Dict, 
                       model_predictions: Dict, predicted_price: float, 
                       investment_advice: str) -> bool:
        """Save prediction results to database"""
        if not self.connection:
            return False
        
        try:
            query = """
            INSERT INTO predictions (session_id, prediction_data, model_predictions, 
                                   predicted_price, investment_advice, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            params = (
                session_id,
                json.dumps(prediction_data),
                json.dumps(model_predictions),
                predicted_price,
                investment_advice,
                datetime.now()
            )
            
            result = self.execute_query(query, params)
            return result is not None and result > 0
            
        except Exception as e:
            self.logger.error(f"Failed to save prediction: {str(e)}")
            return False
    
    def get_market_statistics(self) -> Optional[Dict]:
        """Get comprehensive market statistics"""
        if not self.connection:
            return None
        
        try:
            # Overall statistics
            overall_query = """
            SELECT 
                COUNT(*) as total_properties,
                AVG(price) as avg_price,
                MIN(price) as min_price,
                MAX(price) as max_price,
                AVG(area_sqft) as avg_area
            FROM properties
            """
            
            overall_result = self.execute_query(overall_query)
            if not overall_result:
                return None
            
            # City-wise statistics
            city_query = """
            SELECT 
                city,
                COUNT(*) as total_properties,
                AVG(price) as avg_price,
                AVG(price/area_sqft) as avg_price_per_sqft
            FROM properties
            GROUP BY city
            ORDER BY avg_price DESC
            """
            
            city_result = self.execute_query(city_query)
            
            return {
                'overall_statistics': {
                    'total_properties': overall_result[0][0],
                    'avg_price': float(overall_result[0][1]) if overall_result[0][1] else 0,
                    'min_price': float(overall_result[0][2]) if overall_result[0][2] else 0,
                    'max_price': float(overall_result[0][3]) if overall_result[0][3] else 0,
                    'avg_area': float(overall_result[0][4]) if overall_result[0][4] else 0
                },
                'city_statistics': [
                    {
                        'city': row[0],
                        'total_properties': row[1],
                        'avg_price': float(row[2]) if row[2] else 0,
                        'avg_price_per_sqft': float(row[3]) if row[3] else 0
                    }
                    for row in city_result
                ] if city_result else []
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get market statistics: {str(e)}")
            return None
    
    def close_connection(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.logger.info("Database connection closed")

# Global instance
database_manager = ProductionDatabaseManager()
