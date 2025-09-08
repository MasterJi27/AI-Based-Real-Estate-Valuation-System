"""
Security utilities for protecting against ReDoS and other regex-based attacks
"""
import re
import signal
from contextlib import contextmanager
from typing import Pattern, Optional, Any

class RegexTimeoutError(Exception):
    """Raised when regex operations timeout"""
    pass

@contextmanager
def timeout_protection(seconds: int = 1):
    """Context manager to protect against long-running regex operations"""
    def timeout_handler(signum, frame):
        raise RegexTimeoutError("Regex operation timed out")
    
    # Set the timeout handler
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    
    try:
        yield
    finally:
        # Restore the old handler
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)

class SecureRegex:
    """Secure regex utilities with timeout protection"""
    
    @staticmethod
    def safe_search(pattern: str, text: str, flags: int = 0, timeout: int = 1) -> Optional[re.Match]:
        """Perform regex search with timeout protection"""
        try:
            with timeout_protection(timeout):
                return re.search(pattern, text, flags)
        except RegexTimeoutError:
            return None
    
    @staticmethod
    def safe_findall(pattern: str, text: str, flags: int = 0, timeout: int = 1) -> list:
        """Perform regex findall with timeout protection"""
        try:
            with timeout_protection(timeout):
                return re.findall(pattern, text, flags)
        except RegexTimeoutError:
            return []
    
    @staticmethod
    def safe_sub(pattern: str, repl: str, text: str, flags: int = 0, timeout: int = 1) -> str:
        """Perform regex substitution with timeout protection"""
        try:
            with timeout_protection(timeout):
                return re.sub(pattern, repl, text, flags=flags)
        except RegexTimeoutError:
            return text  # Return original text if regex times out

# Pre-compiled safe regex patterns for common use cases
SAFE_PATTERNS = {
    'bhk': re.compile(r'(\d{1,2})\s*bhk', re.IGNORECASE),
    'area': re.compile(r'(\d{1,6})\s*(?:sqft|sq\.ft|square\s+feet)', re.IGNORECASE),
    'budget_lakh': re.compile(r'(\d{1,4})\s*lakh', re.IGNORECASE),
    'budget_crore': re.compile(r'(\d{1,3})\s*crore', re.IGNORECASE),
    'city': re.compile(r'\b(mumbai|delhi|bangalore|gurugram|noida)\b', re.IGNORECASE),
    'numbers': re.compile(r'\d{1,10}'),  # Limit number length
    'safe_text': re.compile(r'^[a-zA-Z0-9\s\-_.,!?]+$'),  # Safe characters only
}

def extract_safe_numbers(text: str, max_numbers: int = 10) -> list:
    """Safely extract numbers from text with limits"""
    matches = SAFE_PATTERNS['numbers'].findall(text[:500])  # Limit text length
    return matches[:max_numbers]  # Limit number of matches

def extract_safe_bhk(text: str) -> Optional[int]:
    """Safely extract BHK information"""
    match = SAFE_PATTERNS['bhk'].search(text[:100])  # Limit search text
    if match:
        bhk = int(match.group(1))
        return bhk if 1 <= bhk <= 10 else None  # Reasonable range
    return None

def extract_safe_area(text: str) -> Optional[int]:
    """Safely extract area information"""
    match = SAFE_PATTERNS['area'].search(text[:200])  # Limit search text
    if match:
        area = int(match.group(1))
        return area if 100 <= area <= 50000 else None  # Reasonable range
    return None

def extract_safe_budget(text: str) -> Optional[int]:
    """Safely extract budget information"""
    # Check for crore first
    crore_match = SAFE_PATTERNS['budget_crore'].search(text[:100])
    if crore_match:
        amount = int(crore_match.group(1))
        return amount * 10000000 if 1 <= amount <= 1000 else None
    
    # Check for lakh
    lakh_match = SAFE_PATTERNS['budget_lakh'].search(text[:100])
    if lakh_match:
        amount = int(lakh_match.group(1))
        return amount * 100000 if 1 <= amount <= 10000 else None
    
    return None

def extract_safe_city(text: str) -> Optional[str]:
    """Safely extract city information"""
    match = SAFE_PATTERNS['city'].search(text[:100])
    return match.group(1).title() if match else None

def is_safe_text(text: str, max_length: int = 500) -> bool:
    """Check if text contains only safe characters"""
    if len(text) > max_length:
        return False
    return bool(SAFE_PATTERNS['safe_text'].match(text))
