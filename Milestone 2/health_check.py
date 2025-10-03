#!/usr/bin/env python3
"""
Application Health Check Script
Checks all components of the real estate application
"""

import sys
import os
sys.path.append('/workspaces/AI-Based-Real-Estate-Valuation-System/Milestone 2')

import logging
import pandas as pd
from ml_model import RealEstatePricePredictor
from database import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_datasets():
    """Check if datasets are available and valid"""
    logger.info("🗂️  Checking datasets...")
    
    datasets_dir = "/workspaces/AI-Based-Real-Estate-Valuation-System/Milestone 2/datasets"
    required_files = [
        'mumbai_properties.csv',
        'delhi_properties.csv',
        'bangalore_properties.csv',
        'gurugram_properties.csv',
        'noida_properties.csv'
    ]
    
    missing_files = []
    valid_files = []
    total_records = 0
    
    for filename in required_files:
        filepath = os.path.join(datasets_dir, filename)
        if os.path.exists(filepath):
            try:
                df = pd.read_csv(filepath)
                records = len(df)
                total_records += records
                valid_files.append(f"{filename}: {records} records")
                logger.info(f"✅ {filename}: {records} records")
            except Exception as e:
                logger.error(f"❌ {filename}: Error reading - {str(e)}")
                missing_files.append(filename)
        else:
            logger.error(f"❌ {filename}: File not found")
            missing_files.append(filename)
    
    logger.info(f"📊 Total records across all datasets: {total_records}")
    
    return len(missing_files) == 0, total_records

def check_model_files():
    """Check if trained model files exist"""
    logger.info("🤖 Checking model files...")
    
    models_dir = "/workspaces/AI-Based-Real-Estate-Valuation-System/Milestone 2/models"
    model_files = [
        'decision_tree_model.pkl',
        'random_forest_model.pkl',
        'xgboost_model.pkl',
        'encoders.pkl',
        'scalers.pkl',
        'feature_columns.pkl'
    ]
    
    existing_models = []
    missing_models = []
    
    for model_file in model_files:
        filepath = os.path.join(models_dir, model_file)
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            existing_models.append(f"{model_file}: {size} bytes")
            logger.info(f"✅ {model_file}: {size} bytes")
        else:
            missing_models.append(model_file)
            logger.warning(f"⚠️  {model_file}: Not found")
    
    return len(missing_models) == 0, existing_models, missing_models

def health_check():
    """Comprehensive health check"""
    logger.info("🔍 Starting application health check...\n")
    
    # Check datasets
    datasets_ok, total_records = check_datasets()
    
    # Check model files
    models_ok, existing_models, missing_models = check_model_files()
    
    # Check database
    logger.info("🗄️  Checking database connection...")
    try:
        db_manager = DatabaseManager()
        db_ok = db_manager.connection_available
        if db_ok:
            logger.info("✅ Database connection: Available")
        else:
            logger.warning("⚠️  Database connection: Not available (running in offline mode)")
    except Exception as e:
        logger.error(f"❌ Database connection: Error - {str(e)}")
        db_ok = False
    
    # Check ML model functionality
    logger.info("🧠 Testing ML model functionality...")
    try:
        from data_loader import DataLoader
        
        predictor = RealEstatePricePredictor()
        
        if datasets_ok and total_records > 0:
            # Use the proper data loader
            data_loader = DataLoader()
            combined_data = data_loader.load_all_data()
            
            if combined_data is not None and not combined_data.empty:
                logger.info(f"📊 Combined dataset: {len(combined_data)} total records")
                logger.info(f"� Dataset columns: {list(combined_data.columns)}")
                
                # Try training
                training_success = predictor.train_model(combined_data)
                if training_success:
                    logger.info("✅ ML model training: Successful")
                    
                    # Try prediction
                    test_property = {
                        'city': 'Mumbai',
                        'district': combined_data['district'].iloc[0] if 'district' in combined_data.columns else 'Unknown',
                        'sub_district': combined_data['sub_district'].iloc[0] if 'sub_district' in combined_data.columns else 'Unknown',
                        'area_sqft': 1000,
                        'bhk': 2,
                        'property_type': 'Apartment',
                        'furnishing': 'Semi-Furnished'
                    }
                    
                    price, advice, predictions = predictor.predict(test_property)
                    if price > 0:
                        logger.info(f"✅ ML model prediction: Working (test price: ₹{price:,.0f})")
                        ml_ok = True
                    else:
                        logger.error("❌ ML model prediction: Failed")
                        ml_ok = False
                else:
                    logger.error("❌ ML model training: Failed")
                    ml_ok = False
            else:
                logger.error("❌ No valid datasets found for training")
                ml_ok = False
        else:
            logger.warning("⚠️  Cannot test ML model: No datasets available")
            ml_ok = False
            
    except Exception as e:
        logger.error(f"❌ ML model functionality: Error - {str(e)}")
        ml_ok = False
    
    # Summary
    logger.info("\n📋 Health Check Summary:")
    logger.info(f"Datasets: {'✅ OK' if datasets_ok else '❌ ISSUES'} ({total_records} records)")
    logger.info(f"Model Files: {'✅ OK' if models_ok else '⚠️  MISSING'} ({len(existing_models)} found)")
    logger.info(f"Database: {'✅ OK' if db_ok else '⚠️  OFFLINE'}")
    logger.info(f"ML Functionality: {'✅ OK' if ml_ok else '❌ ISSUES'}")
    
    overall_status = datasets_ok and ml_ok  # Database is optional
    
    if overall_status:
        logger.info("\n🎉 Application Status: HEALTHY")
        logger.info("The application should work correctly!")
    else:
        logger.info("\n⚠️  Application Status: NEEDS ATTENTION")
        logger.info("Some issues were found that may affect functionality.")
    
    return overall_status

if __name__ == "__main__":
    success = health_check()
    sys.exit(0 if success else 1)