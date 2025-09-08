"""
Enhanced Error Handling and Logging Module
"""
import logging
import traceback
import streamlit as st
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from config import config

class Logger:
    """Enhanced logging system"""
    
    def __init__(self, name: str = "RealEstateAI"):
        self.logger = logging.getLogger(name)
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration"""
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Set logging level
        log_level = getattr(logging, config.LOGGING_CONFIG['level'])
        self.logger.setLevel(log_level)
        
        # Remove existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # File handler
        file_handler = logging.FileHandler(config.LOGGING_CONFIG['file_path'])
        file_handler.setLevel(log_level)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        
        # Formatter
        formatter = logging.Formatter(config.LOGGING_CONFIG['format'])
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, error: Optional[Exception] = None, **kwargs):
        """Log error message with optional exception details"""
        if error:
            self.logger.error(f"{message}: {str(error)}", extra=kwargs)
            if config.DEBUG:
                self.logger.error(traceback.format_exc())
        else:
            self.logger.error(message, extra=kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(message, extra=kwargs)

class ErrorHandler:
    """Centralized error handling"""
    
    def __init__(self):
        self.logger = Logger("ErrorHandler")
    
    def handle_prediction_error(self, error: Exception, user_inputs: dict) -> str:
        """Handle ML prediction errors"""
        error_msg = "Unable to generate price prediction at this time."
        
        # Log the error with context
        self.logger.error(
            "Prediction error occurred",
            error=error,
            user_inputs=user_inputs,
            timestamp=datetime.now().isoformat()
        )
        
        # Show user-friendly error based on error type
        if "numpy" in str(error).lower() or "array" in str(error).lower():
            error_msg = "Data processing error. Please check your input values."
        elif "model" in str(error).lower():
            error_msg = "Model prediction error. Please try again later."
        elif "memory" in str(error).lower():
            error_msg = "System resources unavailable. Please try again."
        
        return error_msg
    
    def handle_data_error(self, error: Exception, context: str = "") -> str:
        """Handle data loading/processing errors"""
        error_msg = "Unable to process data at this time."
        
        self.logger.error(
            f"Data error in {context}",
            error=error,
            timestamp=datetime.now().isoformat()
        )
        
        if "file" in str(error).lower() or "csv" in str(error).lower():
            error_msg = "Data file error. Please ensure all required files are available."
        elif "database" in str(error).lower():
            error_msg = "Database connection error. Running in offline mode."
        elif "pandas" in str(error).lower():
            error_msg = "Data format error. Please check data integrity."
        
        return error_msg
    
    def handle_validation_error(self, error: Exception, field: str = "") -> str:
        """Handle input validation errors"""
        error_msg = f"Invalid input for {field}. Please check your values."
        
        self.logger.warning(
            f"Validation error for field: {field}",
            error=error,
            timestamp=datetime.now().isoformat()
        )
        
        return error_msg
    
    def handle_database_error(self, error: Exception, operation: str = "") -> str:
        """Handle database errors"""
        error_msg = "Database operation failed. Please try again."
        
        self.logger.error(
            f"Database error during {operation}",
            error=error,
            timestamp=datetime.now().isoformat()
        )
        
        return error_msg

def safe_execute(func: callable, error_handler: ErrorHandler = None, 
                 fallback_value: Any = None, context: str = ""):
    """Safely execute a function with error handling"""
    if error_handler is None:
        error_handler = ErrorHandler()
    
    try:
        return func()
    except Exception as e:
        error_msg = error_handler.handle_prediction_error(e, {"context": context})
        if config.DEBUG:
            st.error(f"Debug info: {str(e)}")
        else:
            st.error(error_msg)
        return fallback_value

def log_user_interaction(action: str, details: dict = None):
    """Log user interactions for analytics"""
    logger = Logger("UserInteraction")
    
    log_data = {
        "action": action,
        "timestamp": datetime.now().isoformat(),
        "session_id": st.session_state.get('session_id', 'unknown'),
        "details": details or {}
    }
    
    logger.info(f"User action: {action}", **log_data)
