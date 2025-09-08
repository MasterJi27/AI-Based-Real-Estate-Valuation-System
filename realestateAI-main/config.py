"""
Production Configuration for Real Estate AI System
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration"""
    
    # App Settings
    APP_NAME = "AI Real Estate Price Predictor"
    VERSION = "1.0.0"
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Security Settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file upload
    
    # Database Configuration
    DATABASE_CONFIG = {
        'host': os.getenv('PGHOST', 'localhost'),
        'database': os.getenv('PGDATABASE', 'realestate'),
        'user': os.getenv('PGUSER', 'postgres'),
        'password': os.getenv('PGPASSWORD', 'password'),
        'port': int(os.getenv('PGPORT', '5432')),
        'sslmode': os.getenv('PGSSLMODE', 'prefer')
    }
    
    # ML Model Configuration
    MODEL_CONFIG = {
        'random_state': 42,
        'test_size': 0.2,
        'max_features': 'sqrt',
        'n_estimators': 100,
        'enable_model_caching': True,
        'model_retrain_threshold_days': 7
    }
    
    # Data Configuration
    DATA_CONFIG = {
        'max_price': 100000000,  # 10 crores
        'min_price': 100000,     # 1 lakh
        'max_area': 10000,       # 10,000 sqft
        'min_area': 100,         # 100 sqft
        'max_bhk': 10,
        'min_bhk': 1
    }
    
    # Streamlit Configuration
    STREAMLIT_CONFIG = {
        'page_title': APP_NAME,
        'page_icon': '🏠',
        'layout': 'wide',
        'initial_sidebar_state': 'expanded'
    }
    
    # Rate Limiting
    RATE_LIMIT = {
        'predictions_per_hour': 100,
        'api_calls_per_minute': 60
    }
    
    # Logging Configuration
    LOGGING_CONFIG = {
        'level': os.getenv('LOG_LEVEL', 'INFO'),
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'file_path': 'logs/app.log'
    }
    
    # Chatbot Configuration
    CHATBOT_CONFIG = {
        'max_conversation_length': 50,
        'response_timeout_seconds': 30,
        'enable_conversation_history': True
    }
    
    # AI Integration Settings
    AI_CONFIG = {
        'gemini_api_key': os.getenv('GEMINI_API_KEY', ''),
        'enable_gemini_ai': True,
        'gemini_model': 'gemini-1.5-flash',  # Changed to flash for better rate limits
        'ai_response_timeout': 30,
        'max_conversation_history': 50,
        'enable_ai_caching': True,
        'ai_cache_ttl': 3600,  # 1 hour
        'rate_limit_retry_delay': 60,  # seconds
        'max_retries': 3
    }
    
    # Security Settings
    SECURITY_CONFIG = {
        'enable_rate_limiting': True,
        'max_requests_per_minute': 60,
        'enable_input_validation': True,
        'enable_xss_protection': True,
        'secure_headers': True,
        'session_timeout': 3600,  # 1 hour
    }

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    
    # Enhanced security for production
    DATABASE_CONFIG = Config.DATABASE_CONFIG.copy()
    DATABASE_CONFIG.update({
        'sslmode': 'require',
        'connect_timeout': 10
    })

# Configuration factory
def get_config():
    """Get configuration based on environment"""
    env = os.getenv('FLASK_ENV', 'development')
    
    if env == 'production':
        return ProductionConfig()
    else:
        return DevelopmentConfig()

# Default configuration
config = get_config()
