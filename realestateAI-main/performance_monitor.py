"""
Performance Monitoring and Analytics Module
"""
import time
import psutil
import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Any
from collections import defaultdict, deque
import json
from pathlib import Path

class PerformanceMonitor:
    """Monitor application performance and usage"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.response_times = deque(maxlen=100)  # Keep last 100 response times
        self.error_counts = defaultdict(int)
        self.user_sessions = defaultdict(dict)
        
    def start_timer(self, operation: str) -> str:
        """Start timing an operation"""
        timer_id = f"{operation}_{int(time.time() * 1000)}"
        if 'active_timers' not in st.session_state:
            st.session_state.active_timers = {}
        st.session_state.active_timers[timer_id] = time.time()
        return timer_id
    
    def end_timer(self, timer_id: str, operation: str = ""):
        """End timing an operation and record metrics"""
        if 'active_timers' not in st.session_state or timer_id not in st.session_state.active_timers:
            return None
        
        start_time = st.session_state.active_timers.pop(timer_id)
        duration = time.time() - start_time
        
        self.response_times.append(duration)
        self.metrics[operation].append({
            'duration': duration,
            'timestamp': datetime.now().isoformat()
        })
        
        return duration
    
    def record_prediction(self, city: str, prediction_time: float, success: bool):
        """Record prediction metrics"""
        session_id = st.session_state.get('session_id', 'unknown')
        
        prediction_data = {
            'city': city,
            'prediction_time': prediction_time,
            'success': success,
            'timestamp': datetime.now().isoformat(),
            'session_id': session_id
        }
        
        self.metrics['predictions'].append(prediction_data)
        
        if not success:
            self.error_counts['prediction_errors'] += 1
    
    def record_user_action(self, action: str, details: Dict = None):
        """Record user interaction"""
        session_id = st.session_state.get('session_id', 'unknown')
        
        action_data = {
            'action': action,
            'details': details or {},
            'timestamp': datetime.now().isoformat(),
            'session_id': session_id
        }
        
        self.metrics['user_actions'].append(action_data)
        
        # Update session info
        if session_id not in self.user_sessions:
            self.user_sessions[session_id] = {
                'start_time': datetime.now().isoformat(),
                'actions': 0,
                'predictions': 0
            }
        
        self.user_sessions[session_id]['actions'] += 1
        if action == 'prediction':
            self.user_sessions[session_id]['predictions'] += 1
    
    def get_system_metrics(self) -> Dict:
        """Get current system metrics"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_performance_summary(self) -> Dict:
        """Get performance summary"""
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        
        return {
            'average_response_time': avg_response_time,
            'total_predictions': len(self.metrics['predictions']),
            'error_rate': self.error_counts['prediction_errors'] / max(len(self.metrics['predictions']), 1),
            'active_sessions': len(self.user_sessions),
            'system_metrics': self.get_system_metrics()
        }
    
    def export_metrics(self, filepath: str = None):
        """Export metrics to JSON file"""
        if filepath is None:
            filepath = f"logs/metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        Path(filepath).parent.mkdir(exist_ok=True)
        
        export_data = {
            'metrics': dict(self.metrics),
            'error_counts': dict(self.error_counts),
            'user_sessions': dict(self.user_sessions),
            'performance_summary': self.get_performance_summary(),
            'export_timestamp': datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return filepath

class CacheManager:
    """Manage application caching for better performance"""
    
    @staticmethod
    @st.cache_data
    def load_data():
        """Cached data loading"""
        from data_loader import DataLoader
        data_loader = DataLoader()
        return data_loader.load_all_data()
    
    @staticmethod
    @st.cache_resource
    def load_model():
        """Cached model loading"""
        from ml_model import RealEstatePricePredictor
        predictor = RealEstatePricePredictor()
        return predictor
    
    @staticmethod
    def clear_cache():
        """Clear all caches"""
        st.cache_data.clear()
        st.cache_resource.clear()

class RateLimiter:
    """Simple rate limiting for API protection"""
    
    def __init__(self):
        self.requests = defaultdict(deque)
    
    def is_allowed(self, session_id: str, action: str, limit: int, window_minutes: int = 60) -> bool:
        """Check if action is allowed within rate limit"""
        now = datetime.now()
        cutoff = now - timedelta(minutes=window_minutes)
        
        # Clean old requests
        key = f"{session_id}_{action}"
        self.requests[key] = deque([
            req_time for req_time in self.requests[key]
            if req_time > cutoff
        ])
        
        # Check if under limit
        if len(self.requests[key]) >= limit:
            return False
        
        # Add current request
        self.requests[key].append(now)
        return True

# Global instances
performance_monitor = PerformanceMonitor()
rate_limiter = RateLimiter()
