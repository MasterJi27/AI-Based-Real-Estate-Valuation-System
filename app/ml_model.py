import logging
logger = logging.getLogger(__name__)
import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
import xgboost as xgb
import joblib
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns

class RealEstatePricePredictor:
    def __init__(self):
        # Initialize multiple models for ensemble
        self.models = {
            'decision_tree': DecisionTreeRegressor(
                max_depth=15,
                min_samples_split=10,
                min_samples_leaf=5,
                random_state=42
            ),
            'random_forest': RandomForestRegressor(
                n_estimators=100,
                max_depth=12,
                min_samples_split=8,
                min_samples_leaf=4,
                random_state=42,
                n_jobs=-1
            ),
            'xgboost': xgb.XGBRegressor(
                n_estimators=100,
                max_depth=8,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                n_jobs=-1
            )
        }
        self.ensemble_model = None
        self.label_encoders = {}
        self.feature_columns = [
            'city', 'district', 'sub_district', 'area_sqft', 
            'bhk', 'property_type', 'furnishing'
        ]
        self.is_trained = False
        self.model_metrics = {}
        self.training_data = None
        
    def preprocess_data(self, data):
        """Preprocess the data for training or prediction"""
        df = data.copy()
        
        logger.debug(f"Preprocessing input shape: {df.shape}")
        logger.debug(f"Preprocessing columns: {df.columns.tolist()}")
        
        # Encode categorical variables
        categorical_cols = ['city', 'district', 'sub_district', 'property_type', 'furnishing']
        
        for col in categorical_cols:
            if col in df.columns:
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                    df[col] = self.label_encoders[col].fit_transform(df[col].astype(str))
                    logger.debug(f"Created new encoder for {col}")
                else:
                    # Handle unseen categories using vectorized operations
                    unique_values = self.label_encoders[col].classes_
                    df[col] = df[col].astype(str)
                    # Use np.where instead of apply(lambda) for better performance
                    df[col] = np.where(df[col].isin(unique_values), df[col], unique_values[0])
                    df[col] = self.label_encoders[col].transform(df[col])
                    logger.debug(f"Used existing encoder for {col}")
        
        logger.debug(f"Preprocessing output shape: {df.shape}")
        logger.debug(f"Preprocessing output columns: {df.columns.tolist()}")
        
        return df
    
    def train_model(self, data):
        """Train ensemble models (Decision Tree, Random Forest, XGBoost)"""
        try:
            # Store training data for historical analysis
            self.training_data = data.copy()
            
            # Preprocess data
            processed_data = self.preprocess_data(data)
            
            # Prepare features and target
            X = processed_data[self.feature_columns]
            y = processed_data['price']
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Train all models and collect metrics
            model_performances = {}
            predictions = {}
            
            for name, model in self.models.items():
                # Train model
                model.fit(X_train, y_train)
                
                # Make predictions
                y_pred = model.predict(X_test)
                predictions[name] = y_pred
                
                # Calculate metrics
                mae = mean_absolute_error(y_test, y_pred)
                rmse = np.sqrt(mean_squared_error(y_test, y_pred))
                r2 = r2_score(y_test, y_pred)
                
                model_performances[name] = {
                    'mae': mae,
                    'rmse': rmse,
                    'r2_score': r2
                }
            
            # Create ensemble prediction (weighted average based on R2 score)
            weights = {}
            # Clamp R2 to 0 before summing so negative scores don't invert weights
            clamped_r2 = {name: max(0.0, perf['r2_score']) for name, perf in model_performances.items()}
            total_r2 = sum(clamped_r2.values())
            
            for name, perf in model_performances.items():
                weights[name] = float(clamped_r2[name] / total_r2 if total_r2 > 0 else 1/3)
            
            # Ensemble prediction
            ensemble_pred = np.zeros_like(y_test, dtype=np.float64)
            for name, pred in predictions.items():
                ensemble_pred += weights[name] * pred.astype(np.float64)
            
            # Ensemble metrics
            ensemble_mae = mean_absolute_error(y_test, ensemble_pred)
            ensemble_rmse = np.sqrt(mean_squared_error(y_test, ensemble_pred))
            ensemble_r2 = r2_score(y_test, ensemble_pred)
            
            model_performances['ensemble'] = {
                'mae': ensemble_mae,
                'rmse': ensemble_rmse,
                'r2_score': ensemble_r2
            }
            
            self.is_trained = True
            self.model_metrics = model_performances
            self.ensemble_weights = weights
            
            # Store test data for analysis
            self.X_test = X_test
            self.y_test = y_test
            
            return True
            
        except Exception as e:
            logger.exception(f"Error training models: {str(e)}")
            return False
    
    def predict(self, property_data):
        """Make ensemble price prediction for a single property"""
        if not self.is_trained:
            raise ValueError("Models not trained yet!")
        
        try:
            # Avoid logging raw property data to protect potential PII
            logger.debug(f"Starting prediction, input type: {type(property_data)}")
            
            # Handle both DataFrame and dictionary inputs
            if isinstance(property_data, pd.DataFrame):
                logger.debug("Input is DataFrame - converting to dictionary")
                if len(property_data) != 1:
                    logger.error(f"DataFrame should have exactly 1 row, got {len(property_data)}")
                    return 0, "Invalid DataFrame input", {}
                property_dict = property_data.iloc[0].to_dict()
                logger.debug("Converted DataFrame to dict")
            elif isinstance(property_data, dict):
                logger.debug("Input is dictionary - using directly")
                property_dict = property_data.copy()
            else:
                logger.error(f"Invalid input type: {type(property_data)}")
                return 0, "Invalid input type", {}
            
            # Convert to DataFrame with proper structure
            df = pd.DataFrame([property_dict])
            logger.debug(f"Created DataFrame with shape: {df.shape}, columns: {df.columns.tolist()}")
            
            # Ensure all required columns are present with default values
            for col in self.feature_columns:
                if col not in df.columns:
                    if col == 'area_sqft':
                        df[col] = 1000  # default area
                    elif col == 'bhk':
                        df[col] = 2  # default BHK
                    else:
                        df[col] = 'Unknown'
                    logger.debug(f"Added missing column {col} with default value")
            
            # Preprocess the data
            logger.debug("Starting preprocessing...")
            processed_df = self.preprocess_data(df)
            logger.debug(f"Preprocessing complete. Shape: {processed_df.shape}")
            
            # Extract features in the correct order and ensure proper shape
            logger.debug(f"Extracting features: {self.feature_columns}")
            X_pred = processed_df[self.feature_columns]
            logger.debug(f"Feature extraction shape: {X_pred.shape}")
            
            # Convert to numpy array safely
            try:
                if hasattr(X_pred, 'values'):
                    X_pred_array = X_pred.values
                    logger.debug(f"Converted to numpy array: {X_pred_array.shape}")
                else:
                    X_pred_array = np.array(X_pred)
                    logger.debug(f"Created numpy array: {X_pred_array.shape}")
                
                # Ensure proper 2D shape
                if X_pred_array.ndim == 1:
                    X_pred_array = X_pred_array.reshape(1, -1)
                    logger.debug(f"Reshaped 1D to 2D: {X_pred_array.shape}")
                elif X_pred_array.ndim > 2:
                    X_pred_array = X_pred_array.reshape(1, -1)
                    logger.debug(f"Reshaped >2D to 2D: {X_pred_array.shape}")
                
                # Final validation
                if X_pred_array.shape[0] != 1:
                    logger.error(f"Wrong number of samples: {X_pred_array.shape[0]}, expected 1")
                    return 0, "Invalid input shape - wrong sample count", {}
                    
                if X_pred_array.shape[1] != len(self.feature_columns):
                    logger.error(f"Feature mismatch: got {X_pred_array.shape[1]}, expected {len(self.feature_columns)}")
                    return 0, "Feature dimension mismatch", {}
                
                logger.debug(f"Final validation passed. Shape: {X_pred_array.shape}")
                
            except Exception as array_error:
                logger.error(f"Error converting to array: {array_error}")
                return 0, f"Array conversion failed: {str(array_error)}", {}
            
            # Make predictions with all models
            predictions = {}
            for name, model in self.models.items():
                try:
                    logger.debug(f"Making prediction with {name} model...")
                    pred_result = model.predict(X_pred_array)
                    predictions[name] = pred_result[0] if len(pred_result) > 0 else 0
                except Exception as model_error:
                    logger.error(f"Error with {name} model prediction: {str(model_error)}", exc_info=False)
                    predictions[name] = 0
            
            # Check if we have valid predictions
            if not predictions or all(pred == 0 for pred in predictions.values()):
                logger.error("All model predictions failed or returned zero")
                return 0, "Prediction models failed", {}
            
            # Ensemble prediction using weights
            ensemble_prediction = sum(
                self.ensemble_weights[name] * pred 
                for name, pred in predictions.items()
            )
            
            # Generate investment advice
            investment_advice = self._generate_investment_advice(property_dict, ensemble_prediction)
            
            # Return ensemble prediction and individual model predictions for transparency
            return ensemble_prediction, investment_advice, predictions
            
        except Exception as e:
            logger.error(f"Error making prediction: {str(e)}")
            return 0, "Unable to determine", {}
    
    def _generate_investment_advice(self, property_data, predicted_price):
        """Generate investment advice based on property characteristics"""
        try:
            # Price per sqft analysis
            area_sqft = property_data.get('area_sqft') if isinstance(property_data, dict) else getattr(property_data, 'area_sqft', None)
            if not area_sqft or float(area_sqft) <= 0:
                return "Unable to Determine"
            price_per_sqft = predicted_price / float(area_sqft)
            
            # City-based thresholds (approximate market rates)
            city_thresholds = {
                'Mumbai': 15000,
                'Delhi': 12000,
                'Gurugram': 8000,
                'Noida': 6000,
                'Bangalore': 7000
            }
            
            city = property_data.get('city') if isinstance(property_data, dict) else getattr(property_data, 'city', None)
            threshold = city_thresholds.get(city, 8000)
            
            # Investment factors
            good_factors = 0
            total_factors = 5
            
            # Factor 1: Price per sqft reasonable
            if price_per_sqft <= threshold * 1.2:  # Within 20% of market rate
                good_factors += 1
            
            # Factor 2: Property size
            area = property_data.get('area_sqft') if isinstance(property_data, dict) else getattr(property_data, 'area_sqft', 0)
            area = float(area) if area else 0
            if 800 <= area <= 2000:  # Optimal size range
                good_factors += 1
            
            # Factor 3: BHK configuration
            bhk = property_data.get('bhk') if isinstance(property_data, dict) else getattr(property_data, 'bhk', None)
            bhk = int(bhk) if bhk else 0
            if 2 <= bhk <= 3:  # Most marketable
                good_factors += 1
            
            # Factor 4: Property type
            prop_type = property_data.get('property_type') if isinstance(property_data, dict) else getattr(property_data, 'property_type', '')
            if prop_type in ['Apartment', 'Villa']:
                good_factors += 1
            
            # Factor 5: Furnishing
            furnishing = property_data.get('furnishing') if isinstance(property_data, dict) else getattr(property_data, 'furnishing', '')
            if furnishing in ['Semi-Furnished', 'Fully Furnished']:
                good_factors += 1
            
            # Make recommendation
            investment_score = good_factors / total_factors
            
            if investment_score >= 0.6:
                return "Good Investment"
            else:
                return "Moderate Investment"
                
        except Exception as e:
            return "Unable to Determine"
    
    def get_model_metrics(self):
        """Get model performance metrics"""
        if hasattr(self, 'model_metrics'):
            return self.model_metrics
        else:
            return None
    
    def get_feature_importance(self):
        """Get feature importance from ensemble models"""
        if not self.is_trained:
            return None
        
        try:
            feature_importance = {}
            
            # Get feature importance from models that support it
            if hasattr(self.models['random_forest'], 'feature_importances_'):
                rf_importance = dict(zip(self.feature_columns, self.models['random_forest'].feature_importances_))
                feature_importance['random_forest'] = sorted(rf_importance.items(), key=lambda x: x[1], reverse=True)
            
            if hasattr(self.models['xgboost'], 'feature_importances_'):
                xgb_importance = dict(zip(self.feature_columns, self.models['xgboost'].feature_importances_))
                feature_importance['xgboost'] = sorted(xgb_importance.items(), key=lambda x: x[1], reverse=True)
            
            return feature_importance
        except Exception as e:
            logger.exception(f"Error getting feature importance: {str(e)}")
            return None
    
    def get_price_trend_analysis(self, city, property_type=None):
        """Analyze price trends for a specific city and property type"""
        if self.training_data is None:
            return None
        
        try:
            # Filter data
            filtered_data = self.training_data[self.training_data['city'] == city].copy()
            if property_type:
                filtered_data = filtered_data[filtered_data['property_type'] == property_type]
            
            if filtered_data.empty:
                return None
            
            # Calculate statistics
            stats = {
                'avg_price': filtered_data['price'].mean(),
                'median_price': filtered_data['price'].median(),
                'price_per_sqft': (filtered_data['price'] / filtered_data['area_sqft']).mean(),
                'total_properties': len(filtered_data),
                'price_range': {
                    'min': filtered_data['price'].min(),
                    'max': filtered_data['price'].max(),
                    'q25': filtered_data['price'].quantile(0.25),
                    'q75': filtered_data['price'].quantile(0.75)
                }
            }
            
            return stats
        except Exception as e:
            logger.exception(f"Error in price trend analysis: {str(e)}")
            return None
    
    def calculate_property_appreciation(self, initial_price, years, appreciation_rate=8.0):
        """Calculate property appreciation over time"""
        try:
            # Annual appreciation calculation
            future_value = initial_price * ((1 + appreciation_rate/100) ** years)
            total_appreciation = future_value - initial_price
            
            # Year-wise breakdown
            yearly_values = []
            for year in range(1, years + 1):
                value = initial_price * ((1 + appreciation_rate/100) ** year)
                yearly_values.append({
                    'year': year,
                    'value': value,
                    'appreciation': value - initial_price
                })
            
            return {
                'initial_price': initial_price,
                'future_value': future_value,
                'total_appreciation': total_appreciation,
                'appreciation_percentage': (total_appreciation / initial_price) * 100,
                'yearly_breakdown': yearly_values,
                'appreciation_rate': appreciation_rate
            }
        except Exception as e:
            logger.exception(f"Error calculating appreciation: {str(e)}")
            return None
    
    def calculate_roi_analysis(self, property_price, monthly_rent, investment_years=10, 
                              maintenance_cost_percent=2, property_tax_percent=1.2):
        """Calculate ROI analysis for rental investment"""
        try:
            # Annual calculations
            annual_rent = monthly_rent * 12
            annual_maintenance = property_price * (maintenance_cost_percent / 100)
            annual_property_tax = property_price * (property_tax_percent / 100)
            annual_net_income = annual_rent - annual_maintenance - annual_property_tax
            
            # Property appreciation
            appreciation_data = self.calculate_property_appreciation(property_price, investment_years)
            
            # Total returns
            total_rental_income = annual_net_income * investment_years
            total_appreciation = appreciation_data['total_appreciation'] if appreciation_data else 0
            total_returns = total_rental_income + total_appreciation
            
            # ROI calculations
            initial_investment = property_price
            roi_percentage = (total_returns / initial_investment) * 100
            annual_roi = roi_percentage / investment_years
            
            # Break-even analysis
            if annual_net_income > 0:
                payback_period = property_price / annual_net_income
            else:
                payback_period = float('inf')
            
            return {
                'property_price': property_price,
                'monthly_rent': monthly_rent,
                'annual_rent': annual_rent,
                'annual_net_income': annual_net_income,
                'total_rental_income': total_rental_income,
                'total_appreciation': total_appreciation,
                'total_returns': total_returns,
                'roi_percentage': roi_percentage,
                'annual_roi': annual_roi,
                'payback_period': payback_period,
                'investment_years': investment_years,
                'rental_yield': (annual_rent / property_price) * 100,
                'net_rental_yield': (annual_net_income / property_price) * 100
            }
        except Exception as e:
            logger.exception(f"Error calculating ROI: {str(e)}")
            return None
    
    def predict_market_trends(self, city, years_ahead=5):
        """Predict market trends for a city"""
        if self.training_data is None:
            return None
        
        try:
            city_data = self.training_data[self.training_data['city'] == city]
            if city_data.empty:
                return None
            
            current_avg_price = city_data['price'].mean()
            current_price_per_sqft = (city_data['price'] / city_data['area_sqft']).mean()
            
            # Market trend predictions based on historical data patterns
            # Conservative growth rates by city
            growth_rates = {
                'Mumbai': 7.5,
                'Delhi': 8.0,
                'Bangalore': 9.0,
                'Gurugram': 8.5,
                'Noida': 7.0
            }
            
            growth_rate = growth_rates.get(city, 7.5)
            
            predictions = []
            for year in range(1, years_ahead + 1):
                predicted_price = current_avg_price * ((1 + growth_rate/100) ** year)
                predicted_price_per_sqft = current_price_per_sqft * ((1 + growth_rate/100) ** year)
                
                predictions.append({
                    'year': year,
                    'predicted_avg_price': predicted_price,
                    'predicted_price_per_sqft': predicted_price_per_sqft,
                    'growth_rate': growth_rate
                })
            
            return {
                'city': city,
                'current_avg_price': current_avg_price,
                'current_price_per_sqft': current_price_per_sqft,
                'predictions': predictions,
                'growth_rate_used': growth_rate
            }
        except Exception as e:
            logger.exception(f"Error predicting market trends: {str(e)}")
            return None
