"""
Production Logging System
Advanced logging configuration for production environment.
"""
import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import json

class ProductionLogger:
    """Production-grade logging system with enhanced features"""
    
    def __init__(self, name: str = "RealEstateAI", config: Optional[Dict] = None):
        self.name = name
        self.logger = logging.getLogger(name)
        self.config = config or self._get_default_config()
        self._setup_logger()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default logging configuration"""
        return {
            'level': 'INFO',
            'file_path': 'logs/production.log',
            'max_file_size_mb': 10,
            'backup_count': 5,
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            'date_format': '%Y-%m-%d %H:%M:%S',
            'enable_console': True,
            'enable_file': True,
            'enable_json_logs': False
        }
    
    def _setup_logger(self):
        """Setup comprehensive logging configuration"""
        # Clear existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Set logging level
        log_level = getattr(logging, self.config['level'].upper(), logging.INFO)
        self.logger.setLevel(log_level)
        
        # Create logs directory
        log_path = Path(self.config['file_path'])
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create formatter
        formatter = logging.Formatter(
            fmt=self.config['format'],
            datefmt=self.config['date_format']
        )
        
        # Console handler
        if self.config['enable_console']:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(log_level)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # Pre-compute max_bytes for any file handlers
        max_bytes = self.config['max_file_size_mb'] * 1024 * 1024
        
        # File handler with rotation
        if self.config['enable_file']:
            file_handler = logging.handlers.RotatingFileHandler(
                filename=self.config['file_path'],
                maxBytes=max_bytes,
                backupCount=self.config['backup_count'],
                encoding='utf-8'
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        
        # JSON handler for structured logs (optional)
        if self.config['enable_json_logs']:
            json_formatter = JsonFormatter()
            json_file_path = str(log_path.with_suffix('.json'))
            json_handler = logging.handlers.RotatingFileHandler(
                filename=json_file_path,
                maxBytes=max_bytes,
                backupCount=self.config['backup_count'],
                encoding='utf-8'
            )
            json_handler.setLevel(log_level)
            json_handler.setFormatter(json_formatter)
            self.logger.addHandler(json_handler)
    
    def info(self, message: str, extra: Optional[Dict] = None):
        """Log info message with optional extra data"""
        self.logger.info(message, extra=extra or {})
    
    def debug(self, message: str, extra: Optional[Dict] = None):
        """Log debug message with optional extra data"""
        self.logger.debug(message, extra=extra or {})
    
    def warning(self, message: str, extra: Optional[Dict] = None):
        """Log warning message with optional extra data"""
        self.logger.warning(message, extra=extra or {})
    
    def error(self, message: str, extra: Optional[Dict] = None, exc_info: bool = False):
        """Log error message with optional extra data and exception info"""
        self.logger.error(message, extra=extra or {}, exc_info=exc_info)
    
    def critical(self, message: str, extra: Optional[Dict] = None, exc_info: bool = False):
        """Log critical message with optional extra data and exception info"""
        self.logger.critical(message, extra=extra or {}, exc_info=exc_info)
    
    def log_performance(self, operation: str, duration: float, success: bool = True, **kwargs):
        """Log performance metrics"""
        perf_data = {
            'operation': operation,
            'duration_ms': round(duration * 1000, 2),
            'success': success,
            'timestamp': datetime.now().isoformat(),
            **kwargs
        }
        self.info(f"Performance: {operation}", extra={'performance': perf_data})
    
    def log_user_action(self, action: str, user_id: str = None, **kwargs):
        """Log user actions for analytics"""
        action_data = {
            'action': action,
            'user_id': user_id or 'anonymous',
            'timestamp': datetime.now().isoformat(),
            **kwargs
        }
        self.info(f"User Action: {action}", extra={'user_action': action_data})
    
    def log_security_event(self, event_type: str, severity: str = 'INFO', **kwargs):
        """Log security-related events at the appropriate level"""
        security_data = {
            'event_type': event_type,
            'severity': severity,
            'timestamp': datetime.now().isoformat(),
            **kwargs
        }
        severity_upper = severity.upper()
        extra = {'security': security_data}
        msg = f"Security Event: {event_type}"
        if severity_upper == 'CRITICAL':
            self.critical(msg, extra=extra)
        elif severity_upper == 'ERROR':
            self.error(msg, extra=extra)
        elif severity_upper == 'WARNING':
            self.warning(msg, extra=extra)
        else:
            self.info(msg, extra=extra)

class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record):
        """Format log record as JSON"""
        log_entry = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'logger': record.name,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage(),
        }
        
        # Add extra fields if present
        if hasattr(record, 'performance'):
            log_entry['performance'] = record.performance
        if hasattr(record, 'user_action'):
            log_entry['user_action'] = record.user_action
        if hasattr(record, 'security'):
            log_entry['security'] = record.security
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, ensure_ascii=False)

class LoggerManager:
    """Centralized logger management"""
    
    _loggers: Dict[str, ProductionLogger] = {}
    
    @classmethod
    def get_logger(cls, name: str, config: Optional[Dict] = None) -> ProductionLogger:
        """Get or create a logger instance"""
        if name not in cls._loggers:
            cls._loggers[name] = ProductionLogger(name, config)
        return cls._loggers[name]
    
    @classmethod
    def configure_root_logger(cls, config: Optional[Dict] = None):
        """Configure the root application logger"""
        return cls.get_logger("RealEstateAI", config)

# Global logger instance for backwards compatibility
logger = LoggerManager.configure_root_logger()

# Export commonly used functions
def get_logger(name: str = "RealEstateAI") -> ProductionLogger:
    """Get a logger instance"""
    return LoggerManager.get_logger(name)

def log_performance(operation: str, duration: float, success: bool = True, **kwargs):
    """Log performance metrics using default logger"""
    logger.log_performance(operation, duration, success, **kwargs)

def log_user_action(action: str, user_id: str = None, **kwargs):
    """Log user actions using default logger"""
    logger.log_user_action(action, user_id, **kwargs)

def log_security_event(event_type: str, severity: str = 'INFO', **kwargs):
    """Log security events using default logger"""
    logger.log_security_event(event_type, severity, **kwargs)
