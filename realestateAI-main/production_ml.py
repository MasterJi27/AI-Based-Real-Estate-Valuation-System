"""
Production Machine Learning Module
Enhanced ML model management for production environment.
"""
import pandas as pd
import numpy as np
import pickle
from typing import Dict, List, Tuple, Optional, Any
import logging
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
import joblib
from datetime import datetime
import os
from production_config import config

class ProductionMLManager:
    """Production-grade ML model management with enhanced features"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.model_scores = {}
        self.is_trained = False
        
        # Initialize production models
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize all ML models with production settings"""
        try:
            self.models = {
                'random_forest': RandomForestRegressor(
                    n_estimators=200,
                    max_depth=15,
                    min_samples_split=5,
                    min_samples_leaf=2,
                    random_state=42,
                    n_jobs=-1
                ),
                'xgboost': xgb.XGBRegressor(
                    n_estimators=200,
                    max_depth=10,
                    learning_rate=0.1,
                    subsample=0.8,
                    colsample_bytree=0.8,
                    random_state=42,
                    n_jobs=-1
                ),
                'gradient_boosting': GradientBoostingRegressor(
                    n_estimators=150,
                    max_depth=8,
                    learning_rate=0.1,
                    subsample=0.8,
                    random_state=42
                ),
                'decision_tree': DecisionTreeRegressor(
                    max_depth=15,
                    min_samples_split=5,
                    min_samples_leaf=2,
                    random_state=42
                ),
                'linear_regression': LinearRegression()
            }
            
            # Initialize preprocessing tools
            self.scalers = {
                'standard_scaler': StandardScaler(),
                'feature_scaler': StandardScaler()
            }
            
            self.encoders = {
                'city_encoder': LabelEncoder(),
                'district_encoder': LabelEncoder(),
                'sub_district_encoder': LabelEncoder(),
                'property_type_encoder': LabelEncoder(),
                'furnishing_encoder': LabelEncoder()
            }
            
            self.logger.info("Production ML models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize ML models: {str(e)}")
            raise
    
    def preprocess_data(self, df: pd.DataFrame, training: bool = True) -> pd.DataFrame:
        """Enhanced data preprocessing for production environment"""
        try:
            df_processed = df.copy()
            
            # Handle missing values
            numeric_columns = df_processed.select_dtypes(include=[np.number]).columns
            categorical_columns = df_processed.select_dtypes(include=['object']).columns
            
            # Fill numeric missing values with median
            for col in numeric_columns:
                if df_processed[col].isnull().any():
                    df_processed[col].fillna(df_processed[col].median(), inplace=True)
            
            # Fill categorical missing values with mode
            for col in categorical_columns:
                if df_processed[col].isnull().any():
                    df_processed[col].fillna(df_processed[col].mode()[0], inplace=True)
            
            # Encode categorical variables
            categorical_features = ['city', 'district', 'sub_district', 'property_type', 'furnishing']
            
            for feature in categorical_features:
                if feature in df_processed.columns:
                    if training:
                        # Fit encoder during training
                        df_processed[f'{feature}_encoded'] = self.encoders[f'{feature}_encoder'].fit_transform(
                            df_processed[feature].astype(str)
                        )
                    else:
                        # Transform using fitted encoder during prediction
                        try:
                            df_processed[f'{feature}_encoded'] = self.encoders[f'{feature}_encoder'].transform(
                                df_processed[feature].astype(str)
                            )
                        except ValueError:
                            # Handle unseen categories
                            known_categories = set(self.encoders[f'{feature}_encoder'].classes_)
                            df_processed[feature] = df_processed[feature].apply(
                                lambda x: x if x in known_categories else self.encoders[f'{feature}_encoder'].classes_[0]
                            )
                            df_processed[f'{feature}_encoded'] = self.encoders[f'{feature}_encoder'].transform(
                                df_processed[feature].astype(str)
                            )
            
            # Feature engineering
            if 'area_sqft' in df_processed.columns and 'price' in df_processed.columns:
                df_processed['price_per_sqft'] = df_processed['price'] / (df_processed['area_sqft'] + 1)
            
            if 'bhk' in df_processed.columns and 'area_sqft' in df_processed.columns:
                df_processed['area_per_room'] = df_processed['area_sqft'] / (df_processed['bhk'] + 1)
            
            # Log transformation for skewed features
            if 'price' in df_processed.columns:
                df_processed['log_price'] = np.log1p(df_processed['price'])
            
            if 'area_sqft' in df_processed.columns:
                df_processed['log_area'] = np.log1p(df_processed['area_sqft'])
            
            self.logger.info(f"Data preprocessing completed. Shape: {df_processed.shape}")
            return df_processed
            
        except Exception as e:
            self.logger.error(f"Data preprocessing failed: {str(e)}")
            raise
    
    def prepare_features(self, df: pd.DataFrame, target_column: str = 'price') -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare features and target for ML models"""
        try:
            # Select features for training
            feature_columns = [
                'area_sqft', 'bhk', 'city_encoded', 'district_encoded',
                'sub_district_encoded', 'property_type_encoded', 'furnishing_encoded',
                'price_per_sqft', 'area_per_room', 'log_area'
            ]
            
            # Filter existing columns
            available_features = [col for col in feature_columns if col in df.columns]
            
            X = df[available_features]
            y = df[target_column] if target_column in df.columns else None
            
            self.logger.info(f"Features prepared. Shape: {X.shape}")
            return X, y
            
        except Exception as e:
            self.logger.error(f"Feature preparation failed: {str(e)}")
            raise
    
    def train_models(self, df: pd.DataFrame) -> Dict[str, float]:
        """Train all ML models with cross-validation"""
        try:
            # Preprocess data
            df_processed = self.preprocess_data(df, training=True)
            X, y = self.prepare_features(df_processed)
            
            if X.empty or y is None:
                raise ValueError("No valid features or target variable found")
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Scale features
            X_train_scaled = self.scalers['standard_scaler'].fit_transform(X_train)
            X_test_scaled = self.scalers['standard_scaler'].transform(X_test)
            
            # Train each model
            model_scores = {}
            
            for model_name, model in self.models.items():
                try:
                    # Train model
                    if model_name == 'linear_regression':
                        model.fit(X_train_scaled, y_train)
                        y_pred = model.predict(X_test_scaled)
                    else:
                        model.fit(X_train, y_train)
                        y_pred = model.predict(X_test)
                    
                    # Calculate scores
                    mae = mean_absolute_error(y_test, y_pred)
                    mse = mean_squared_error(y_test, y_pred)
                    r2 = r2_score(y_test, y_pred)
                    
                    # Cross-validation score
                    if model_name == 'linear_regression':
                        cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='r2')
                    else:
                        cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='r2')
                    
                    model_scores[model_name] = {
                        'mae': mae,
                        'mse': mse,
                        'rmse': np.sqrt(mse),
                        'r2': r2,
                        'cv_mean': cv_scores.mean(),
                        'cv_std': cv_scores.std()
                    }
                    
                    self.logger.info(f"{model_name} - R²: {r2:.4f}, MAE: {mae:.2f}")
                    
                except Exception as model_error:
                    self.logger.error(f"Training failed for {model_name}: {str(model_error)}")
                    model_scores[model_name] = {'error': str(model_error)}
            
            self.model_scores = model_scores
            self.is_trained = True
            
            # Save best model
            best_model_name = max(
                [name for name, scores in model_scores.items() if 'error' not in scores],
                key=lambda x: model_scores[x]['r2']
            )
            
            self.best_model_name = best_model_name
            self.logger.info(f"Training completed. Best model: {best_model_name}")
            
            return model_scores
            
        except Exception as e:
            self.logger.error(f"Model training failed: {str(e)}")
            raise
    
    def predict_price(self, property_data: Dict) -> Dict[str, Any]:
        """Make price predictions using all models"""
        try:
            if not self.is_trained:
                raise ValueError("Models are not trained yet")
            
            # Convert to DataFrame
            df = pd.DataFrame([property_data])
            
            # Preprocess
            df_processed = self.preprocess_data(df, training=False)
            X, _ = self.prepare_features(df_processed)
            
            # Make predictions with all models
            predictions = {}
            
            for model_name, model in self.models.items():
                try:
                    if model_name == 'linear_regression':
                        X_scaled = self.scalers['standard_scaler'].transform(X)
                        prediction = model.predict(X_scaled)[0]
                    else:
                        prediction = model.predict(X)[0]
                    
                    predictions[model_name] = max(0, prediction)  # Ensure non-negative prices
                    
                except Exception as model_error:
                    self.logger.error(f"Prediction failed for {model_name}: {str(model_error)}")
                    predictions[model_name] = None
            
            # Calculate ensemble prediction
            valid_predictions = [p for p in predictions.values() if p is not None]
            if valid_predictions:
                ensemble_prediction = np.mean(valid_predictions)
            else:
                ensemble_prediction = None
            
            # Calculate confidence interval
            if len(valid_predictions) > 1:
                std = np.std(valid_predictions)
                confidence_interval = {
                    'lower': max(0, ensemble_prediction - 1.96 * std),
                    'upper': ensemble_prediction + 1.96 * std
                }
            else:
                confidence_interval = None
            
            result = {
                'individual_predictions': predictions,
                'ensemble_prediction': ensemble_prediction,
                'confidence_interval': confidence_interval,
                'model_scores': self.model_scores if hasattr(self, 'model_scores') else {},
                'best_model': getattr(self, 'best_model_name', None)
            }
            
            self.logger.info(f"Prediction completed. Ensemble: ₹{ensemble_prediction:,.2f}")
            return result
            
        except Exception as e:
            self.logger.error(f"Price prediction failed: {str(e)}")
            raise
    
    def save_models(self, model_dir: str = "models"):
        """Save trained models and preprocessors"""
        try:
            os.makedirs(model_dir, exist_ok=True)
            
            # Save models
            for model_name, model in self.models.items():
                model_path = os.path.join(model_dir, f"{model_name}.pkl")
                joblib.dump(model, model_path)
            
            # Save preprocessors
            for scaler_name, scaler in self.scalers.items():
                scaler_path = os.path.join(model_dir, f"{scaler_name}.pkl")
                joblib.dump(scaler, scaler_path)
            
            for encoder_name, encoder in self.encoders.items():
                encoder_path = os.path.join(model_dir, f"{encoder_name}.pkl")
                joblib.dump(encoder, encoder_path)
            
            # Save metadata
            metadata = {
                'model_scores': self.model_scores,
                'best_model': getattr(self, 'best_model_name', None),
                'training_timestamp': datetime.now().isoformat(),
                'is_trained': self.is_trained
            }
            
            metadata_path = os.path.join(model_dir, "model_metadata.pkl")
            joblib.dump(metadata, metadata_path)
            
            self.logger.info(f"Models saved to {model_dir}")
            
        except Exception as e:
            self.logger.error(f"Failed to save models: {str(e)}")
            raise
    
    def load_models(self, model_dir: str = "models"):
        """Load trained models and preprocessors"""
        try:
            if not os.path.exists(model_dir):
                self.logger.warning(f"Model directory {model_dir} not found")
                return False
            
            # Load models
            for model_name in self.models.keys():
                model_path = os.path.join(model_dir, f"{model_name}.pkl")
                if os.path.exists(model_path):
                    self.models[model_name] = joblib.load(model_path)
            
            # Load preprocessors
            for scaler_name in self.scalers.keys():
                scaler_path = os.path.join(model_dir, f"{scaler_name}.pkl")
                if os.path.exists(scaler_path):
                    self.scalers[scaler_name] = joblib.load(scaler_path)
            
            for encoder_name in self.encoders.keys():
                encoder_path = os.path.join(model_dir, f"{encoder_name}.pkl")
                if os.path.exists(encoder_path):
                    self.encoders[encoder_name] = joblib.load(encoder_path)
            
            # Load metadata
            metadata_path = os.path.join(model_dir, "model_metadata.pkl")
            if os.path.exists(metadata_path):
                metadata = joblib.load(metadata_path)
                self.model_scores = metadata.get('model_scores', {})
                self.best_model_name = metadata.get('best_model', None)
                self.is_trained = metadata.get('is_trained', False)
            
            self.logger.info(f"Models loaded from {model_dir}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load models: {str(e)}")
            return False
    
    def get_feature_importance(self, model_name: str = None) -> Dict[str, float]:
        """Get feature importance from tree-based models"""
        try:
            if not self.is_trained:
                return {}
            
            if model_name is None:
                model_name = getattr(self, 'best_model_name', 'random_forest')
            
            if model_name not in self.models:
                return {}
            
            model = self.models[model_name]
            
            # Get feature importance for tree-based models
            if hasattr(model, 'feature_importances_'):
                feature_names = [
                    'area_sqft', 'bhk', 'city_encoded', 'district_encoded',
                    'sub_district_encoded', 'property_type_encoded', 'furnishing_encoded',
                    'price_per_sqft', 'area_per_room', 'log_area'
                ]
                
                importance_dict = dict(zip(feature_names, model.feature_importances_))
                return dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
            
            return {}
            
        except Exception as e:
            self.logger.error(f"Failed to get feature importance: {str(e)}")
            return {}

# Global instance
ml_manager = ProductionMLManager()
