"""
Input Validation and Sanitization Module
"""
import re
import html
import unicodedata
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
from production_config import config

class InputValidator:
    """Validates and sanitizes user inputs"""
    
    @staticmethod
    def validate_property_inputs(city: str, district: str, area_sqft: float, 
                               bhk: int, property_type: str, furnishing: str) -> Tuple[bool, str]:
        """Validate property prediction inputs"""
        
        # City validation
        valid_cities = ['Mumbai', 'Delhi', 'Bangalore', 'Gurugram', 'Noida']
        if city not in valid_cities:
            return False, f"Invalid city. Must be one of: {', '.join(valid_cities)}"
        
        # Area validation
        if not (config.DATA_CONFIG['min_area'] <= area_sqft <= config.DATA_CONFIG['max_area']):
            return False, f"Area must be between {config.DATA_CONFIG['min_area']} and {config.DATA_CONFIG['max_area']} sqft"
        
        # BHK validation
        if not (config.DATA_CONFIG['min_bhk'] <= bhk <= config.DATA_CONFIG['max_bhk']):
            return False, f"BHK must be between {config.DATA_CONFIG['min_bhk']} and {config.DATA_CONFIG['max_bhk']}"
        
        # Property type validation
        valid_property_types = ['Apartment', 'Villa', 'House', 'Studio']
        if property_type not in valid_property_types:
            return False, f"Invalid property type. Must be one of: {', '.join(valid_property_types)}"
        
        # Furnishing validation
        valid_furnishing = ['Fully Furnished', 'Semi Furnished', 'Unfurnished']
        if furnishing not in valid_furnishing:
            return False, f"Invalid furnishing. Must be one of: {', '.join(valid_furnishing)}"
        
        # District validation (basic sanitization)
        if not district or len(district.strip()) < 2:
            return False, "District name must be at least 2 characters"
        
        if not re.match(r'^[a-zA-Z\s\-]+$', district):
            return False, "District name contains invalid characters"
        
        return True, "Valid inputs"
    
    @staticmethod
    def validate_emi_inputs(principal: float, rate: float, tenure: int) -> Tuple[bool, str]:
        """Validate EMI calculation inputs"""
        
        # Principal validation
        if not (100000 <= principal <= 100000000):  # 1 lakh to 10 crores
            return False, "Loan amount must be between ₹1 lakh and ₹10 crores"
        
        # Interest rate validation
        if not (1.0 <= rate <= 25.0):
            return False, "Interest rate must be between 1% and 25%"
        
        # Tenure validation
        if not (1 <= tenure <= 30):
            return False, "Loan tenure must be between 1 and 30 years"
        
        return True, "Valid inputs"
    
    @staticmethod
    def sanitize_text_input(text: str, max_length: int = 100) -> str:
        """Sanitize text input to prevent XSS and other attacks"""
        if not text:
            return ""
        
        # Unescape HTML entities first to prevent double-encoded XSS
        text = html.unescape(text)
        
        # Remove HTML tags and special characters
        text = re.sub(r'<[^>]*>', '', text)
        text = re.sub(r'[<>"\']', '', text)
        
        # Limit length
        text = text[:max_length]
        
        # Strip whitespace
        return text.strip()
    
    @staticmethod
    def validate_chat_input(message: str) -> Tuple[bool, str]:
        """Validate chatbot input"""
        
        if not message or len(message.strip()) == 0:
            return False, "Message cannot be empty"
        
        if len(message) > 500:
            return False, "Message too long. Maximum 500 characters allowed"
        
        # Normalize Unicode before pattern matching to catch homoglyph attacks
        normalized = unicodedata.normalize('NFKC', message)
        
        # Check for potential malicious content (Fixed: Avoid polynomial regex)
        suspicious_patterns = [
            r'<script[^>]*>[^<]*</script>',  # Fixed: More specific pattern
            r'javascript:',
            r'on\w+\s*=',
            r'eval\s*\(',
            r'document\.',
            r'window\.'
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, normalized, re.IGNORECASE):
                return False, "Message contains potentially unsafe content"
        
        return True, "Valid message"

class DataValidator:
    """Validates data integrity and quality"""
    
    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Validate property dataframe without mutating the input"""
        errors = []
        # Work on a copy so the caller's DataFrame is not mutated
        df = df.copy()
        
        # Check required columns
        required_columns = ['city', 'district', 'area_sqft', 'bhk', 'property_type', 'furnishing', 'price']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            errors.append(f"Missing required columns: {missing_columns}")
        
        if not errors:  # Only proceed if we have all columns
            # Check data types
            try:
                df['area_sqft'] = pd.to_numeric(df['area_sqft'], errors='coerce')
                df['bhk'] = pd.to_numeric(df['bhk'], errors='coerce')
                df['price'] = pd.to_numeric(df['price'], errors='coerce')
            except Exception as e:
                errors.append(f"Data type conversion error: {e}")
            
            # Check for null values in critical columns
            null_counts = df[required_columns].isnull().sum()
            if null_counts.any():
                errors.append(f"Null values found: {null_counts[null_counts > 0].to_dict()}")
            
            # Check value ranges
            if (df['area_sqft'] <= 0).any():
                errors.append("Invalid area values (must be positive)")
            
            if (df['bhk'] <= 0).any():
                errors.append("Invalid BHK values (must be positive)")
            
            if (df['price'] <= 0).any():
                errors.append("Invalid price values (must be positive)")
        
        return len(errors) == 0, errors
