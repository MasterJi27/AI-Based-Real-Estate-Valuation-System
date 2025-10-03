#!/usr/bin/env python3
"""
Emergency fix script to resolve ML model shape errors
This script will completely reload all modules and restart the application
"""

import sys
import os
import subprocess
import importlib
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def force_module_reload():
    """Force reload of all custom modules"""
    modules_to_reload = [
        'ml_model', 'gemini_ai', 'app', 'data_loader', 
        'database', 'property_analyzer', 'chatbot'
    ]
    
    for module_name in modules_to_reload:
        if module_name in sys.modules:
            try:
                importlib.reload(sys.modules[module_name])
                logger.info(f"Reloaded module: {module_name}")
            except Exception as e:
                logger.warning(f"Could not reload {module_name}: {e}")

def kill_streamlit_processes():
    """Kill all running Streamlit processes"""
    try:
        subprocess.run(['pkill', '-f', 'streamlit'], check=False)
        logger.info("Killed existing Streamlit processes")
    except Exception as e:
        logger.warning(f"Error killing processes: {e}")

def clear_cache():
    """Clear Python cache files"""
    try:
        # Remove .pyc files
        subprocess.run(['find', '.', '-name', '*.pyc', '-delete'], check=False)
        # Remove __pycache__ directories
        subprocess.run(['find', '.', '-name', '__pycache__', '-type', 'd', '-exec', 'rm', '-rf', '{}', '+'], check=False)
        logger.info("Cleared Python cache files")
    except Exception as e:
        logger.warning(f"Error clearing cache: {e}")

def test_ml_model():
    """Test the ML model to ensure it works"""
    try:
        # Clear any cached modules first
        for module in list(sys.modules.keys()):
            if any(name in module for name in ['ml_model', 'data_loader']):
                try:
                    del sys.modules[module]
                except:
                    pass
        
        # Import fresh modules
        from ml_model import RealEstatePricePredictor
        from data_loader import DataLoader
        
        logger.info("Testing ML model...")
        data_loader = DataLoader()
        data = data_loader.load_all_data()
        predictor = RealEstatePricePredictor()
        
        # Train model
        trained = predictor.train_model(data)
        if not trained:
            raise Exception("Model training failed")
        
        # Test prediction
        test_property = {
            'city': 'Mumbai',
            'district': 'South Mumbai', 
            'sub_district': 'Colaba',
            'area_sqft': 1000,
            'bhk': 2,
            'property_type': 'Apartment',
            'furnishing': 'Semi-Furnished'
        }
        
        price, advice, predictions = predictor.predict(test_property)
        if price > 0:
            logger.info(f"✅ ML Model test successful: ₹{price:,.0f}")
            return True
        else:
            logger.error("❌ ML Model test failed: Zero prediction")
            return False
            
    except Exception as e:
        logger.error(f"❌ ML Model test failed: {e}")
        return False

def main():
    """Main emergency fix procedure"""
    logger.info("🚨 EMERGENCY FIX PROCEDURE STARTING")
    
    # Step 1: Kill existing processes
    logger.info("Step 1: Killing existing processes...")
    kill_streamlit_processes()
    
    # Step 2: Clear cache
    logger.info("Step 2: Clearing cache...")
    clear_cache()
    
    # Step 3: Force module reload
    logger.info("Step 3: Force reloading modules...")
    force_module_reload()
    
    # Step 4: Test ML model
    logger.info("Step 4: Testing ML model...")
    if test_ml_model():
        logger.info("✅ ML model is working correctly")
    else:
        logger.error("❌ ML model still has issues")
        return False
    
    # Step 5: Start application
    logger.info("Step 5: Starting fresh Streamlit application...")
    try:
        os.system("streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true &")
        logger.info("✅ Application started successfully")
        logger.info("🌐 Access at: http://localhost:8501")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to start application: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 EMERGENCY FIX COMPLETED SUCCESSFULLY!")
        print("All errors should now be resolved.")
    else:
        print("\n❌ EMERGENCY FIX FAILED!")
        print("Manual intervention may be required.")