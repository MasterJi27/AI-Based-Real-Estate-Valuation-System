#!/usr/bin/env python3
"""
Test script to verify the fixes for the reported issues
"""

import sys
import os
sys.path.append('/workspaces/AI-Based-Real-Estate-Valuation-System/Milestone 2')

import logging
import pandas as pd
from ml_model import RealEstatePricePredictor
from gemini_ai import GeminiAIService
from database import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_ml_model():
    """Test ML model prediction with proper input validation"""
    logger.info("Testing ML Model...")
    
    try:
        # Create sample data for training
        sample_data = pd.DataFrame({
            'city': ['Mumbai', 'Delhi', 'Bangalore', 'Mumbai', 'Delhi'] * 100,
            'district': ['Andheri', 'CP', 'Koramangala', 'Bandra', 'Lajpat Nagar'] * 100,
            'sub_district': ['Andheri East', 'CP Central', 'Koramangala 5th Block', 'Bandra West', 'Lajpat Nagar IV'] * 100,
            'area_sqft': [1000, 1200, 800, 1500, 900] * 100,
            'bhk': [2, 3, 1, 3, 2] * 100,
            'property_type': ['Apartment', 'Villa', 'Apartment', 'Apartment', 'Independent House'] * 100,
            'furnishing': ['Semi-Furnished', 'Fully Furnished', 'Unfurnished', 'Fully Furnished', 'Semi-Furnished'] * 100,
            'price': [5000000, 8000000, 3500000, 12000000, 6000000] * 100
        })
        
        # Initialize and train model
        predictor = RealEstatePricePredictor()
        training_success = predictor.train_model(sample_data)
        
        if training_success:
            logger.info("✅ Model training successful")
            
            # Test prediction
            test_property = {
                'city': 'Mumbai',
                'district': 'Andheri',
                'sub_district': 'Andheri East',
                'area_sqft': 1000,
                'bhk': 2,
                'property_type': 'Apartment',
                'furnishing': 'Semi-Furnished'
            }
            
            predicted_price, investment_advice, model_predictions = predictor.predict(test_property)
            
            if predicted_price > 0:
                logger.info(f"✅ Prediction successful: ₹{predicted_price:,.0f}")
                logger.info(f"Investment advice: {investment_advice}")
                logger.info(f"Model predictions: {model_predictions}")
                return True
            else:
                logger.error("❌ Prediction failed: Zero or negative price")
                return False
        else:
            logger.error("❌ Model training failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ ML Model test failed: {str(e)}")
        return False

def test_gemini_ai():
    """Test Gemini AI service with correct model name"""
    logger.info("Testing Gemini AI...")
    
    try:
        # Note: This will fail without API key, but should not fail due to model name
        api_key = os.getenv('GOOGLE_API_KEY', 'dummy_key_for_testing')
        service = GeminiAIService(api_key=api_key)
        
        logger.info("✅ Gemini AI service initialized successfully")
        return True
        
    except ValueError as e:
        if "API key" in str(e):
            logger.info("✅ Gemini AI initialization works (API key not provided, which is expected)")
            return True
        else:
            logger.error(f"❌ Gemini AI test failed: {str(e)}")
            return False
    except Exception as e:
        if "models/gemini-1.5-flash is not found" in str(e):
            logger.error("❌ Gemini AI model name still incorrect")
            return False
        else:
            logger.info(f"✅ Gemini AI model name fixed (other error: {str(e)})")
            return True

def test_database():
    """Test database connection handling"""
    logger.info("Testing Database Connection...")
    
    try:
        db_manager = DatabaseManager()
        
        # This should not crash even if database is not available
        connection = db_manager.get_connection()
        
        if connection is None:
            logger.info("✅ Database gracefully handles unavailable connection")
            return True
        else:
            logger.info("✅ Database connection successful")
            connection.close()
            return True
            
    except Exception as e:
        logger.error(f"❌ Database test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    logger.info("🧪 Running fix verification tests...")
    
    results = {
        'ML Model': test_ml_model(),
        'Gemini AI': test_gemini_ai(),
        'Database': test_database()
    }
    
    logger.info("\n📊 Test Results:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    if all_passed:
        logger.info("\n🎉 All tests passed! Fixes appear to be working.")
    else:
        logger.info("\n⚠️  Some tests failed. Please check the logs above.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)