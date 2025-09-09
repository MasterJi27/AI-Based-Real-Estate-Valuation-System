"""
Production Security Management
Comprehensive security features for production environment.
"""
import hashlib
import hmac
import time
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict
import secrets
import ipaddress

class SecurityManager:
    """Production security management system"""
    
    def __init__(self, secret_key: Optional[str] = None):
        self.secret_key = secret_key or self._generate_secret_key()
        self.blocked_ips: Dict[str, datetime] = {}
        self.suspicious_patterns = self._load_suspicious_patterns()
    
    def _generate_secret_key(self) -> str:
        """Generate a secure secret key"""
        return secrets.token_urlsafe(32)
    
    def _load_suspicious_patterns(self) -> List[re.Pattern]:
        """Load patterns for detecting suspicious input"""
        patterns = [
            r'<script[^>]*>.*?</script>',  # Script tags
            r'javascript:',  # JavaScript protocol
            r'on\w+\s*=',  # Event handlers
            r'eval\s*\(',  # eval function
            r'document\.',  # DOM access
            r'window\.',  # Window object
            r'alert\s*\(',  # Alert function
            r'prompt\s*\(',  # Prompt function
            r'confirm\s*\(',  # Confirm function
            r'\.\./',  # Directory traversal
            r'union\s+select',  # SQL injection
            r'drop\s+table',  # SQL injection
            r'insert\s+into',  # SQL injection
            r'delete\s+from',  # SQL injection
        ]
        return [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    
    def validate_input(self, text: str, max_length: int = 1000) -> Tuple[bool, str]:
        """Validate and sanitize user input"""
        if not text:
            return True, ""
        
        # Check length
        if len(text) > max_length:
            return False, f"Input too long. Maximum {max_length} characters allowed."
        
        # Check for suspicious patterns
        for pattern in self.suspicious_patterns:
            if pattern.search(text):
                return False, "Input contains potentially unsafe content."
        
        # Additional checks for common attacks
        if self._check_xss_patterns(text):
            return False, "Input contains potential XSS patterns."
        
        if self._check_sql_injection(text):
            return False, "Input contains potential SQL injection patterns."
        
        return True, text
    
    def _check_xss_patterns(self, text: str) -> bool:
        """Check for XSS attack patterns"""
        xss_patterns = [
            r'<.*?on\w+.*?=',  # Event handlers in tags
            r'<.*?href\s*=\s*["\']?\s*javascript:',  # JavaScript in href
            r'<.*?src\s*=\s*["\']?\s*javascript:',  # JavaScript in src
            r'expression\s*\(',  # CSS expression
            r'vbscript:',  # VBScript protocol
        ]
        
        for pattern in xss_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _check_sql_injection(self, text: str) -> bool:
        """Check for SQL injection patterns"""
        sql_patterns = [
            r"'\s*or\s+'",  # OR injection
            r"'\s*and\s+'",  # AND injection
            r"'\s*;\s*drop\s+",  # Drop statement
            r"'\s*;\s*insert\s+",  # Insert statement
            r"'\s*;\s*update\s+",  # Update statement
            r"'\s*;\s*delete\s+",  # Delete statement
            r"union\s+all\s+select",  # Union select
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def sanitize_text(self, text: str) -> str:
        """Sanitize text input"""
        if not text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]*>', '', text)
        
        # Remove potentially dangerous characters
        text = re.sub(r'[<>"\']', '', text)
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        return text
    
    def generate_csrf_token(self, session_id: str) -> str:
        """Generate CSRF token for session"""
        timestamp = str(int(time.time()))
        message = f"{session_id}:{timestamp}"
        signature = hmac.new(
            self.secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"{timestamp}:{signature}"
    
    def validate_csrf_token(self, token: str, session_id: str, max_age: int = 3600) -> bool:
        """Validate CSRF token"""
        try:
            timestamp_str, signature = token.split(':', 1)
            timestamp = int(timestamp_str)
            
            # Check if token is not expired
            if time.time() - timestamp > max_age:
                return False
            
            # Regenerate expected signature
            message = f"{session_id}:{timestamp_str}"
            expected_signature = hmac.new(
                self.secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures securely
            return hmac.compare_digest(signature, expected_signature)
            
        except (ValueError, TypeError):
            return False
    
    def check_ip_reputation(self, ip_address: str) -> Tuple[bool, str]:
        """Check if IP address is blocked or suspicious"""
        try:
            # Parse IP address
            ip = ipaddress.ip_address(ip_address)
            
            # Check if IP is in blocked list
            if ip_address in self.blocked_ips:
                block_time = self.blocked_ips[ip_address]
                if datetime.now() - block_time < timedelta(hours=1):  # 1 hour block
                    return False, "IP address is temporarily blocked"
                else:
                    # Remove expired block
                    del self.blocked_ips[ip_address]
            
            # Check for private/localhost IPs (allow for development)
            if ip.is_private or ip.is_loopback:
                return True, "Private/localhost IP allowed"
            
            # Add more IP reputation checks here if needed
            return True, "IP address is clean"
            
        except ValueError:
            return False, "Invalid IP address format"
    
    def block_ip(self, ip_address: str, reason: str = "Security violation"):
        """Block an IP address"""
        self.blocked_ips[ip_address] = datetime.now()
        # Log the blocking event
        print(f"IP {ip_address} blocked: {reason}")

class RateLimiter:
    """Rate limiting for API endpoints and user actions"""
    
    def __init__(self):
        self.requests: Dict[str, List[datetime]] = defaultdict(list)
        self.limits = {
            'default': (60, 60),  # 60 requests per 60 seconds
            'prediction': (10, 60),  # 10 predictions per 60 seconds
            'chat': (30, 60),  # 30 chat messages per 60 seconds
            'login': (5, 300),  # 5 login attempts per 5 minutes
        }
    
    def is_allowed(self, identifier: str, action: str = 'default', 
                   custom_limit: Optional[int] = None, 
                   window_seconds: int = 60) -> bool:
        """Check if action is allowed for identifier"""
        now = datetime.now()
        
        # Get rate limits
        if custom_limit is not None:
            max_requests = custom_limit
        else:
            max_requests, window_seconds = self.limits.get(action, self.limits['default'])
        
        # Create key for this identifier and action
        key = f"{identifier}:{action}"
        
        # Clean old entries
        cutoff_time = now - timedelta(seconds=window_seconds)
        self.requests[key] = [req_time for req_time in self.requests[key] 
                             if req_time > cutoff_time]
        
        # Check if under limit
        if len(self.requests[key]) < max_requests:
            self.requests[key].append(now)
            return True
        
        return False
    
    def get_remaining_requests(self, identifier: str, action: str = 'default') -> int:
        """Get remaining requests for identifier and action"""
        max_requests, window_seconds = self.limits.get(action, self.limits['default'])
        key = f"{identifier}:{action}"
        
        # Clean old entries
        now = datetime.now()
        cutoff_time = now - timedelta(seconds=window_seconds)
        self.requests[key] = [req_time for req_time in self.requests[key] 
                             if req_time > cutoff_time]
        
        return max_requests - len(self.requests[key])
    
    def reset_user_limits(self, identifier: str):
        """Reset all limits for a user"""
        keys_to_remove = [key for key in self.requests.keys() 
                         if key.startswith(f"{identifier}:")]
        for key in keys_to_remove:
            del self.requests[key]

class ContentFilter:
    """Content filtering and moderation"""
    
    def __init__(self):
        self.blocked_words = self._load_blocked_words()
        self.suspicious_domains = self._load_suspicious_domains()
    
    def _load_blocked_words(self) -> List[str]:
        """Load list of blocked words"""
        # Basic list - in production, this would come from a configuration file
        return [
            'spam', 'scam', 'hack', 'malware', 'virus',
            'phishing', 'fraud', 'illegal', 'drugs'
        ]
    
    def _load_suspicious_domains(self) -> List[str]:
        """Load list of suspicious domains"""
        return [
            'bit.ly', 'tinyurl.com', 't.co',  # URL shorteners (can be suspicious)
        ]
    
    def filter_content(self, text: str) -> Tuple[bool, str, List[str]]:
        """Filter content for inappropriate material"""
        issues = []
        
        # Check for blocked words
        text_lower = text.lower()
        found_blocked = [word for word in self.blocked_words if word in text_lower]
        if found_blocked:
            issues.append(f"Contains blocked words: {', '.join(found_blocked)}")
        
        # Check for suspicious URLs
        url_pattern = r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?'
        urls = re.findall(url_pattern, text)
        
        suspicious_urls = []
        for url in urls:
            for domain in self.suspicious_domains:
                if domain in url:
                    suspicious_urls.append(url)
        
        if suspicious_urls:
            issues.append(f"Contains suspicious URLs: {', '.join(suspicious_urls)}")
        
        # Check for excessive capitalization (could be spam)
        if len(text) > 10:
            caps_ratio = sum(1 for c in text if c.isupper()) / len(text)
            if caps_ratio > 0.7:
                issues.append("Excessive use of capital letters")
        
        is_clean = len(issues) == 0
        filtered_text = self._apply_content_filters(text) if not is_clean else text
        
        return is_clean, filtered_text, issues
    
    def _apply_content_filters(self, text: str) -> str:
        """Apply content filters to clean up text"""
        # Replace blocked words with asterisks
        filtered_text = text
        for word in self.blocked_words:
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            filtered_text = pattern.sub('*' * len(word), filtered_text)
        
        return filtered_text

# Global instances
security_manager = SecurityManager()
rate_limiter = RateLimiter()
content_filter = ContentFilter()

# Export convenience functions
def validate_input(text: str, max_length: int = 1000) -> Tuple[bool, str]:
    """Validate user input using global security manager"""
    return security_manager.validate_input(text, max_length)

def sanitize_text(text: str) -> str:
    """Sanitize text using global security manager"""
    return security_manager.sanitize_text(text)

def is_rate_limited(identifier: str, action: str = 'default') -> bool:
    """Check if identifier is rate limited"""
    return not rate_limiter.is_allowed(identifier, action)

def filter_content(text: str) -> Tuple[bool, str, List[str]]:
    """Filter content using global content filter"""
    return content_filter.filter_content(text)
