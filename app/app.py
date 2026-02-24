import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from ml_model import RealEstatePricePredictor
from data_loader import DataLoader
from emi_calculator import EMICalculator
from database import DatabaseManager
from property_analyzer import PropertyAnalyzer
from chatbot import RealEstateChatbot
from financial_calculator import render_financial_tools
from content_system import render_content_system
# Use production modules instead of legacy ones
from production_config import config
from production_logging import ProductionLogger
from production_security import SecurityManager, RateLimiter
from validators import InputValidator, DataValidator

# Initialize production components
logger = ProductionLogger()
security_manager = SecurityManager()
rate_limiter = RateLimiter()

# Simple replacements for legacy functions
def safe_execute(func, error_handler=None, fallback_value=None, context=""):
    """Simple safe execution wrapper"""
    try:
        return func()
    except Exception as e:
        logger.error(f"Error in {context}: {str(e)}")
        return fallback_value

def log_user_interaction(action, data=None):
    """Simple user interaction logging"""
    logger.info(f"User interaction: {action}", extra={'data': data or {}})

class SimplePerformanceMonitor:
    """Simple performance monitoring replacement"""
    def __init__(self):
        self.timers = {}
    
    def start_timer(self, name):
        import time
        timer_id = f"{name}_{time.time()}"
        self.timers[timer_id] = time.time()
        return timer_id
    
    def end_timer(self, timer_id, name):
        import time
        if timer_id in self.timers:
            duration = time.time() - self.timers[timer_id]
            del self.timers[timer_id]
            return duration
        return 0
    
    def record_prediction(self, city, duration, success):
        logger.info(f"Prediction recorded: {city}, duration: {duration}s, success: {success}")
    
    def get_performance_summary(self):
        return {"status": "monitoring active"}

class SimpleCacheManager:
    """Simple cache management replacement"""
    @staticmethod
    def load_data():
        # Load data using DataLoader
        from data_loader import DataLoader
        loader = DataLoader()
        return loader.load_all_data()
    
    @staticmethod
    def load_model():
        from ml_model import RealEstatePricePredictor
        return RealEstatePricePredictor()
    
    @staticmethod
    def clear_cache():
        pass

# Initialize simple replacements
performance_monitor = SimplePerformanceMonitor()
CacheManager = SimpleCacheManager()

class SimpleErrorHandler:
    """Simple error handler replacement"""
    def handle_data_error(self, error, context):
        logger.error(f"Data error in {context}: {str(error)}")
        return f"Data processing error: {str(error)}"
    
    def handle_prediction_error(self, error, data):
        logger.error(f"Prediction error: {str(error)}")
        return f"Prediction failed: {str(error)}"
    
    def handle_database_error(self, error, context):
        logger.error(f"Database error in {context}: {str(error)}")
        return f"Database error: {str(error)}"

# Initialize error handler
error_handler = SimpleErrorHandler()
from gemini_ai import GeminiAIService, initialize_gemini_service, get_gemini_service
import uuid
import warnings
warnings.filterwarnings('ignore')

# Initialize error handler
error_handler = SimpleErrorHandler()

# Configure page
st.set_page_config(
    page_title=config.STREAMLIT_CONFIG['page_title'],
    page_icon=config.STREAMLIT_CONFIG['page_icon'],
    layout=config.STREAMLIT_CONFIG['layout'],
    initial_sidebar_state=config.STREAMLIT_CONFIG['initial_sidebar_state']
)

# Initialize session state
if 'predictor' not in st.session_state:
    st.session_state.predictor = None
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'db_manager' not in st.session_state:
    st.session_state.db_manager = DatabaseManager()
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'property_analyzer' not in st.session_state:
    st.session_state.property_analyzer = PropertyAnalyzer()
if 'data_loader' not in st.session_state:
    st.session_state.data_loader = DataLoader()
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = None
if 'gemini_service' not in st.session_state:
    st.session_state.gemini_service = None
if 'gemini_initialized' not in st.session_state:
    st.session_state.gemini_initialized = False

def load_data_and_model():
    """Load data and train model with error handling and performance monitoring"""
    timer_id = performance_monitor.start_timer("data_loading")
    
    try:
        # Use cached data loading for better performance
        combined_data = CacheManager.load_data()
        
        if combined_data is not None and not combined_data.empty:
            # Validate data quality
            is_valid, errors = DataValidator.validate_dataframe(combined_data)
            if not is_valid:
                st.error(f"Data validation failed: {'; '.join(errors)}")
                return False
            
            # Load and train model
            predictor = CacheManager.load_model()
            predictor.train_model(combined_data)
            
            # Update session state
            st.session_state.predictor = predictor
            st.session_state.data_loaded = True
            st.session_state.combined_data = combined_data
            
            # Initialize chatbot with loaded data
            st.session_state.chatbot = RealEstateChatbot(
                data_loader=st.session_state.data_loader,
                predictor=predictor,
                combined_data=combined_data
            )
            
            # Load data to database (optional, with error handling)
            try:
                st.session_state.db_manager.load_properties_to_db(combined_data)
            except Exception as e:
                error_handler.handle_database_error(e, "loading properties")
            
            # Record successful loading
            duration = performance_monitor.end_timer(timer_id, "data_loading")
            log_user_interaction("data_loaded", {"duration": duration, "rows": len(combined_data)})
            
            return True
        else:
            st.error("No valid data found. Please ensure CSV files are properly formatted.")
            return False
            
    except Exception as e:
        duration = performance_monitor.end_timer(timer_id, "data_loading")
        error_msg = error_handler.handle_data_error(e, "data loading")
        st.error(error_msg)
        return False

def initialize_gemini_ai():
    """Initialize Gemini AI service"""
    if not st.session_state.gemini_initialized and config.AI_CONFIG.get('enable_gemini_ai', False):
        try:
            with st.spinner("Initializing Gemini AI..."):
                api_key = config.AI_CONFIG.get('gemini_api_key')
                if api_key:
                    st.session_state.gemini_service = initialize_gemini_service(api_key)
                    st.session_state.gemini_initialized = True
                    st.success("✅ Gemini AI initialized successfully")
                else:
                    st.warning("⚠️ Gemini API key not configured")
        except Exception as e:
            st.error(f"❌ Failed to initialize Gemini AI: {str(e)}")
            error_handler.handle_error(e, "Gemini AI initialization failed")

def main():
    # Security check - rate limiting
    session_id = st.session_state.get('session_id', 'unknown')
    if not rate_limiter.is_allowed(session_id, 'page_load', config.RATE_LIMIT['predictions_per_hour']):
        st.error("Rate limit exceeded. Please try again later.")
        st.stop()
    
    # Load data if not already loaded
    if not st.session_state.data_loaded:
        with st.spinner("Loading property data and training ML model..."):
            if not load_data_and_model():
                st.error("Failed to load data and train models. Please check the data files.")
                if config.DEBUG:
                    if st.button("Clear Cache and Retry"):
                        CacheManager.clear_cache()
                        st.rerun()
                st.stop()
    
    # Initialize Gemini AI if not already done
    if not st.session_state.gemini_initialized:
        initialize_gemini_ai()
    
    # Header with version info
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title("🏠 AI Real Estate Price Predictor")
        st.markdown("### Professional Property Price Prediction & Investment Analysis for Indian Cities")
    with col2:
        if config.DEBUG:
            st.info(f"Version: {config.VERSION}")
            with st.expander("System Status"):
                metrics = performance_monitor.get_performance_summary()
                st.json(metrics)
    
    # Navigation tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["🔮 Price Prediction", "📊 Property Valuation", "💼 Investment Analysis", "💰 Financial Tools", "📚 Knowledge Center", "🤖 AI Assistant", "🧠 Gemini AI Insights"])
    
    with tab1:
        price_prediction_interface()
    
    with tab2:
        property_valuation_interface()
    
    with tab3:
        investment_analysis_interface()
    
    with tab4:
        render_financial_tools()
    
    with tab5:
        render_content_system()
    
    with tab6:
        ai_assistant_interface()
    
    with tab7:
        st.header("🧠 Gemini AI Insights")
        st.markdown("### Advanced Real Estate Intelligence powered by Google Gemini 2.5")
        
        # Check if Gemini AI is available
        gemini_service = get_gemini_service()
        if not gemini_service:
            st.warning("⚠️ Gemini AI is not available. Please check configuration.")
            if st.button("🔄 Retry Initialization"):
                initialize_gemini_ai()
                st.rerun()
        else:
            # Gemini AI Features
            gemini_feature = st.selectbox(
                "Choose AI Analysis Type:",
                [
                    "🏘️ Property Market Analysis",
                    "💰 Investment Recommendations", 
                    "📈 Market Trends Analysis",
                    "❓ Real Estate Q&A",
                    "📋 Property Report Generation"
                ]
            )
            
            if gemini_feature == "🏘️ Property Market Analysis":
                st.subheader("Property Market Analysis")
                
                col1, col2 = st.columns(2)
                with col1:
                    location = st.selectbox("City", ["Mumbai", "Delhi", "Bangalore", "Gurugram", "Noida"])
                    property_type = st.selectbox("Property Type", ["Apartment", "Villa", "Studio"])
                    area = st.number_input("Area (sq ft)", min_value=100, max_value=10000, value=1000)
                
                with col2:
                    bedrooms = st.selectbox("Bedrooms", [1, 2, 3, 4, 5])
                    bathrooms = st.selectbox("Bathrooms", [1, 2, 3, 4, 5])
                    age = st.number_input("Property Age (years)", min_value=0, max_value=50, value=5)
                
                if st.button("🔍 Analyze Property Market"):
                    # Get prediction first
                    if st.session_state.predictor:
                        try:
                            input_data = pd.DataFrame({
                                'city': [location],
                                'district': [location],  # Use city as district fallback
                                'sub_district': [location],  # Use city as sub_district fallback  
                                'area_sqft': [area],
                                'bhk': [bedrooms],
                                'property_type': [property_type],
                                'furnishing': ['Semi-Furnished']  # Default furnishing
                            })
                            
                            prediction_result = st.session_state.predictor.predict(input_data)
                            predicted_price = prediction_result[0]  # Get ensemble prediction
                            
                            property_data = {
                                'location': location,
                                'property_type': property_type,
                                'area': area,
                                'bedrooms': bedrooms,
                                'bathrooms': bathrooms,
                                'age': age,
                                'predicted_price': predicted_price
                            }
                            
                            with st.spinner("Generating AI market analysis..."):
                                analysis = gemini_service.analyze_property_market(property_data)
                                st.markdown("### 📊 AI Market Analysis")
                                st.write(analysis)
                                
                        except Exception as e:
                            st.error(f"Analysis failed: {str(e)}")
            
            elif gemini_feature == "💰 Investment Recommendations":
                st.subheader("Personalized Investment Recommendations")
                
                col1, col2 = st.columns(2)
                with col1:
                    budget = st.number_input("Investment Budget (₹)", min_value=100000, max_value=100000000, value=5000000, step=100000)
                    timeline = st.selectbox("Investment Timeline", ["1-2 years", "3-5 years", "5-10 years", "10+ years"])
                    risk_appetite = st.selectbox("Risk Appetite", ["Conservative", "Moderate", "Aggressive"])
                
                with col2:
                    goal = st.selectbox("Investment Goal", ["Capital Appreciation", "Rental Income", "Both"])
                    preferred_locations = st.multiselect("Preferred Cities", ["Mumbai", "Delhi", "Bangalore", "Gurugram", "Noida"])
                    property_type_pref = st.selectbox("Property Type Preference", ["Apartment", "Villa", "Commercial", "Any"])
                
                if st.button("💡 Get Investment Recommendations"):
                    user_profile = {
                        'budget': budget,
                        'timeline': timeline,
                        'risk_appetite': risk_appetite,
                        'goal': goal,
                        'preferred_locations': ', '.join(preferred_locations),
                        'property_type': property_type_pref
                    }
                    
                    with st.spinner("Generating personalized investment recommendations..."):
                        recommendations = gemini_service.get_investment_recommendations(user_profile)
                        st.markdown("### 💼 Investment Recommendations")
                        st.write(recommendations)
            
            elif gemini_feature == "📈 Market Trends Analysis":
                st.subheader("Market Trends Analysis")
                
                col1, col2 = st.columns(2)
                with col1:
                    city = st.selectbox("City for Analysis", ["Mumbai", "Delhi", "Bangalore", "Gurugram", "Noida"])
                with col2:
                    property_type_filter = st.selectbox("Property Type", ["All Types", "Apartment", "Villa", "Commercial"])
                
                if st.button("📊 Analyze Market Trends"):
                    prop_type = None if property_type_filter == "All Types" else property_type_filter
                    
                    with st.spinner("Analyzing market trends..."):
                        trends = gemini_service.analyze_market_trends(city, prop_type)
                        st.markdown("### 📈 Market Trends Analysis")
                        st.write(trends)
            
            elif gemini_feature == "❓ Real Estate Q&A":
                st.subheader("Real Estate Q&A")
                st.markdown("Ask any question about real estate markets, investments, or property analysis.")
                
                # Initialize conversation history for Gemini
                if 'gemini_chat_history' not in st.session_state:
                    st.session_state.gemini_chat_history = []
                
                user_question = st.text_area("Your Question:", placeholder="e.g., What are the best areas for investment in Mumbai?")
                
                if st.button("🤔 Ask Gemini AI"):
                    if user_question.strip():
                        with st.spinner("Getting AI response..."):
                            answer = gemini_service.real_estate_qa(user_question)
                            
                            # Add to conversation
                            st.session_state.gemini_chat_history.append({
                                "question": user_question,
                                "answer": answer,
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            })
                            
                            st.markdown("### 🤖 AI Response")
                            st.write(answer)
                
                # Display recent conversations
                if st.session_state.gemini_chat_history:
                    st.markdown("### 📜 Recent Conversations")
                    for i, conv in enumerate(st.session_state.gemini_chat_history[-3:]):  # Show last 3
                        with st.expander(f"Q: {conv['question'][:50]}... ({conv['timestamp']})"):
                            st.write(f"**Question:** {conv['question']}")
                            st.write(f"**Answer:** {conv['answer']}")
            
            elif gemini_feature == "📋 Property Report Generation":
                st.subheader("Comprehensive Property Report")
                st.markdown("Generate a detailed AI-powered property analysis report.")
                
                # Property details input
                col1, col2 = st.columns(2)
                with col1:
                    report_location = st.selectbox("Location", ["Mumbai", "Delhi", "Bangalore", "Gurugram", "Noida"], key="report_location")
                    report_property_type = st.selectbox("Property Type", ["Apartment", "Villa", "Studio"], key="report_property_type")
                    report_area = st.number_input("Area (sq ft)", min_value=100, max_value=10000, value=1200, key="report_area")
                
                with col2:
                    report_bedrooms = st.selectbox("Bedrooms", [1, 2, 3, 4, 5], key="report_bedrooms")
                    report_bathrooms = st.selectbox("Bathrooms", [1, 2, 3, 4, 5], key="report_bathrooms")
                    report_age = st.number_input("Property Age (years)", min_value=0, max_value=50, value=3, key="report_age")
                
                if st.button("📋 Generate Comprehensive Report"):
                    if st.session_state.predictor:
                        try:
                            input_data = pd.DataFrame({
                                'city': [report_location],
                                'district': [report_location],  # Use city as district fallback
                                'sub_district': [report_location],  # Use city as sub_district fallback
                                'area_sqft': [report_area],
                                'bhk': [report_bedrooms],
                                'property_type': [report_property_type],
                                'furnishing': ['Semi-Furnished']  # Default furnishing
                            })
                            
                            prediction_result = st.session_state.predictor.predict(input_data)
                            predicted_price = prediction_result[0]  # Get ensemble prediction
                            
                            property_data = {
                                'location': report_location,
                                'property_type': report_property_type,
                                'area': report_area,
                                'bedrooms': report_bedrooms,
                                'bathrooms': report_bathrooms,
                                'age': report_age,
                                'predicted_price': predicted_price,
                                'analysis_date': datetime.now().strftime("%Y-%m-%d"),
                                'price_per_sqft': predicted_price / report_area
                            }
                            
                            with st.spinner("Generating comprehensive property report..."):
                                report = gemini_service.generate_property_report(property_data)
                                st.markdown("### 📋 Comprehensive Property Report")
                                st.write(report)
                                
                                # Option to download report
                                st.download_button(
                                    label="📥 Download Report",
                                    data=report,
                                    file_name=f"property_report_{report_location}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                                    mime="text/plain"
                                )
                                
                        except Exception as e:
                            st.error(f"Report generation failed: {str(e)}")

    # Footer with disclaimer
    st.markdown("---")
    st.markdown("""
    **Disclaimer:** This application provides estimated property prices based on historical data and machine learning models. 
    Actual prices may vary based on market conditions, property condition, and other factors. 
    Please consult with real estate professionals for accurate valuations.
    """)
    
    # Performance monitoring
    log_user_interaction("page_view")

def price_prediction_interface():
    """Enhanced price prediction interface with validation and monitoring"""
    
    # Rate limiting check for predictions
    session_id = st.session_state.get('session_id', 'unknown')
    if not rate_limiter.is_allowed(session_id, 'prediction', config.RATE_LIMIT['predictions_per_hour'], 60):
        st.error("You've exceeded the hourly prediction limit. Please try again later.")
        return
    
    # Sidebar for inputs
    st.sidebar.header("Property Details")
    
    # User Analytics Section
    with st.sidebar.expander("📊 Your Analytics", expanded=False):
        user_analytics = st.session_state.db_manager.get_user_analytics(st.session_state.session_id)
        if user_analytics:
            st.metric("Predictions Made", user_analytics.get('predictions_made', 0))
            st.metric("Page Views", user_analytics.get('page_views', 0))
            if user_analytics.get('favorite_city'):
                st.write(f"**Favorite City:** {user_analytics['favorite_city']}")
            if user_analytics.get('avg_property_price'):
                st.write(f"**Avg Search Price:** ₹{user_analytics['avg_property_price']:,.0f}")
    
    # Prediction History
    with st.sidebar.expander("🔍 Recent Searches", expanded=False):
        history = st.session_state.db_manager.get_prediction_history(st.session_state.session_id, limit=5)
        if history:
            for i, pred in enumerate(history):
                st.write(f"**{i+1}.** {pred['city']} - {pred['bhk']} BHK")
                st.write(f"₹{pred['predicted_price']:,.0f} | {pred['investment_advice']}")
                st.write(f"_{pred['created_at'].strftime('%m/%d %H:%M')}_")
                st.write("---")
        else:
            st.write("No recent searches found.")
    
    # City selection
    cities = ['Mumbai', 'Delhi', 'Gurugram', 'Noida', 'Bangalore']
    selected_city = st.sidebar.selectbox("Select City", cities)
    
    # Get districts and sub-districts based on selected city
    city_data = st.session_state.combined_data[
        st.session_state.combined_data['city'] == selected_city
    ]
    
    districts = sorted(city_data['district'].unique())
    selected_district = st.sidebar.selectbox("Select District", districts)
    
    district_data = city_data[city_data['district'] == selected_district]
    sub_districts = sorted(district_data['sub_district'].unique())
    selected_sub_district = st.sidebar.selectbox("Select Sub-District", sub_districts)
    
    # Property details with validation
    st.sidebar.subheader("Property Specifications")
    
    sq_ft = st.sidebar.number_input(
        "Area (Square Feet)", 
        min_value=config.DATA_CONFIG['min_area'], 
        max_value=config.DATA_CONFIG['max_area'], 
        value=1000,
        step=50,
        help=f"Enter area between {config.DATA_CONFIG['min_area']} and {config.DATA_CONFIG['max_area']} sqft"
    )
    
    bhk = st.sidebar.selectbox("BHK", list(range(config.DATA_CONFIG['min_bhk'], config.DATA_CONFIG['max_bhk'] + 1)))
    
    property_types = ['Apartment', 'Villa', 'Independent House', 'Studio', 'Penthouse']
    property_type = st.sidebar.selectbox("Property Type", property_types)
    
    furnishing_options = ['Unfurnished', 'Semi-Furnished', 'Fully Furnished']
    furnishing = st.sidebar.selectbox("Furnishing", furnishing_options)
    
    # Input validation
    inputs_valid = True
    validation_errors = []
    
    # Validate inputs
    is_valid, error_msg = InputValidator.validate_property_inputs(
        selected_city, selected_district, sq_ft, bhk, property_type, furnishing
    )
    
    if not is_valid:
        inputs_valid = False
        validation_errors.append(error_msg)
    
    # Show validation errors
    if validation_errors:
        for error in validation_errors:
            st.sidebar.error(error)
    
    # Predict button
    predict_button = st.sidebar.button("🔮 Predict Price", type="primary", disabled=not inputs_valid)
    
    if predict_button and inputs_valid:
        if st.session_state.predictor:
            timer_id = performance_monitor.start_timer("prediction")
            
            try:
                # Prepare prediction data
                prediction_data = {
                    'city': selected_city,
                    'district': selected_district,
                    'sub_district': selected_sub_district,
                    'area_sqft': sq_ft,
                    'bhk': bhk,
                    'property_type': property_type,
                    'furnishing': furnishing
                }
                
                # Make prediction with error handling
                def make_prediction():
                    return st.session_state.predictor.predict(prediction_data)
                
                result = safe_execute(
                    make_prediction, 
                    error_handler, 
                    fallback_value=(None, "Unable to generate prediction", {}),
                    context="price_prediction"
                )
                
                predicted_price, investment_advice, model_predictions = result
                
                if predicted_price is not None:
                    # Record metrics
                    duration = performance_monitor.end_timer(timer_id, "prediction")
                    performance_monitor.record_prediction(selected_city, duration, True)
                    
                    # Save prediction to database
                    try:
                        st.session_state.db_manager.save_prediction(
                            st.session_state.session_id, prediction_data, model_predictions,
                            predicted_price, investment_advice
                        )
                        
                        # Update user analytics
                        st.session_state.db_manager.update_user_analytics(
                            st.session_state.session_id, increment_predictions=True,
                            favorite_city=selected_city, avg_price=predicted_price
                        )
                    except Exception as e:
                        error_handler.handle_database_error(e, "saving prediction")
                    
                    # Store results in session state
                    st.session_state.prediction_results = {
                        'price': predicted_price,
                        'investment_advice': investment_advice,
                        'property_details': prediction_data,
                        'model_predictions': model_predictions
                    }
                    
                    # Log successful prediction
                    log_user_interaction("prediction", {
                        "city": selected_city,
                        "bhk": bhk,
                        "area": sq_ft,
                        "predicted_price": predicted_price
                    })
                    
                    st.rerun()
                else:
                    # Record failed prediction
                    performance_monitor.record_prediction(selected_city, 0, False)
                    
            except Exception as e:
                duration = performance_monitor.end_timer(timer_id, "prediction")
                performance_monitor.record_prediction(selected_city, duration, False)
                error_msg = error_handler.handle_prediction_error(e, prediction_data)
                st.error(error_msg)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Display prediction results
        if 'prediction_results' in st.session_state:
            results = st.session_state.prediction_results
            
            st.header("🎯 Price Prediction Results")
            
            # Price display
            price_col1, price_col2, price_col3 = st.columns(3)
            
            with price_col1:
                st.metric(
                    "Predicted Price",
                    f"₹{results['price']:,.0f}",
                    delta=None
                )
            
            with price_col2:
                price_per_sqft = results['price'] / sq_ft
                st.metric(
                    "Price per Sq Ft",
                    f"₹{price_per_sqft:,.0f}",
                    delta=None
                )
            
            with price_col3:
                # Investment recommendation
                advice_color = "normal" if results['investment_advice'] == "Good Investment" else "inverse"
                st.metric(
                    "Investment Advice",
                    results['investment_advice'],
                    delta=None
                )
            
            # Model Comparison
            st.subheader("🤖 AI Model Predictions")
            if 'model_predictions' in results:
                model_cols = st.columns(4)
                model_names = ['Decision Tree', 'Random Forest', 'XGBoost', 'Ensemble']
                model_keys = ['decision_tree', 'random_forest', 'xgboost']
                
                for i, (name, key) in enumerate(zip(model_names[:-1], model_keys)):
                    with model_cols[i]:
                        pred_price = results['model_predictions'].get(key, 0)
                        st.metric(name, f"₹{pred_price:,.0f}")
                
                with model_cols[3]:
                    st.metric("Ensemble", f"₹{results['price']:,.0f}", delta="Best Prediction")
            
            # Property summary
            st.subheader("📋 Property Summary")
            summary_data = {
                "Location": f"{selected_sub_district}, {selected_district}, {selected_city}",
                "Area": f"{sq_ft:,} sq ft",
                "Configuration": f"{bhk} BHK",
                "Property Type": property_type,
                "Furnishing": furnishing,
                "Predicted Price": f"₹{results['price']:,.0f}",
                "Price per Sq Ft": f"₹{price_per_sqft:,.0f}"
            }
            
            for key, value in summary_data.items():
                st.write(f"**{key}:** {value}")
            
            # Investment Analysis
            st.subheader("💰 Investment Analysis")
            
            # Property Appreciation Calculator
            st.write("**Property Appreciation Forecast**")
            appreciation_years = st.selectbox("Investment Period", [5, 10, 15, 20], index=1, key="appreciation_years")
            appreciation_rate = st.slider("Annual Appreciation Rate (%)", 5.0, 12.0, 8.0, 0.5, key="appreciation_rate")
            
            appreciation_data = st.session_state.predictor.calculate_property_appreciation(
                results['price'], appreciation_years, appreciation_rate
            )
            
            if appreciation_data:
                appr_col1, appr_col2, appr_col3 = st.columns(3)
                with appr_col1:
                    st.metric("Future Value", f"₹{appreciation_data['future_value']:,.0f}")
                with appr_col2:
                    st.metric("Total Appreciation", f"₹{appreciation_data['total_appreciation']:,.0f}")
                with appr_col3:
                    st.metric("Appreciation %", f"{appreciation_data['appreciation_percentage']:.1f}%")
            
            # ROI Analysis for Rental Investment
            st.write("**Rental Investment ROI Analysis**")
            monthly_rent = st.number_input("Expected Monthly Rent (₹)", 
                                         min_value=5000, max_value=500000, 
                                         value=int(results['price'] * 0.001), step=1000)
            
            roi_data = st.session_state.predictor.calculate_roi_analysis(
                results['price'], monthly_rent, investment_years=10
            )
            
            if roi_data:
                roi_col1, roi_col2, roi_col3, roi_col4 = st.columns(4)
                with roi_col1:
                    st.metric("Annual ROI", f"{roi_data['annual_roi']:.1f}%")
                with roi_col2:
                    st.metric("Rental Yield", f"{roi_data['rental_yield']:.1f}%")
                with roi_col3:
                    st.metric("Payback Period", f"{roi_data['payback_period']:.1f} years")
                with roi_col4:
                    st.metric("Total Returns", f"₹{roi_data['total_returns']:,.0f}")
        
        # Market Analysis & Trends
        st.header("📊 Advanced Market Analysis & Trends")
        
        if st.session_state.data_loaded:
            # Market Trend Predictions
            st.subheader("📈 Market Trend Predictions")
            market_trends = st.session_state.predictor.predict_market_trends(selected_city, years_ahead=5)
            
            if market_trends:
                trend_col1, trend_col2 = st.columns(2)
                
                with trend_col1:
                    st.metric("Current Avg Price", f"₹{market_trends['current_avg_price']:,.0f}")
                    st.metric("Current Price/Sq Ft", f"₹{market_trends['current_price_per_sqft']:,.0f}")
                    st.metric("Growth Rate", f"{market_trends['growth_rate_used']}% per annum")
                
                with trend_col2:
                    # Future price predictions chart
                    trend_df = pd.DataFrame(market_trends['predictions'])
                    fig_trend = px.line(
                        trend_df, 
                        x='year', 
                        y='predicted_avg_price',
                        title=f'{selected_city} - 5 Year Price Forecast',
                        markers=True
                    )
                    fig_trend.update_layout(height=300)
                    st.plotly_chart(fig_trend, use_container_width=True)
            
            # Price Trend Analysis for Selected City
            st.subheader(f"🏙️ {selected_city} Market Analysis")
            price_analysis = st.session_state.predictor.get_price_trend_analysis(selected_city, property_type)
            
            if price_analysis:
                analysis_col1, analysis_col2, analysis_col3, analysis_col4 = st.columns(4)
                with analysis_col1:
                    st.metric("Average Price", f"₹{price_analysis['avg_price']:,.0f}")
                with analysis_col2:
                    st.metric("Median Price", f"₹{price_analysis['median_price']:,.0f}")
                with analysis_col3:
                    st.metric("Price per Sq Ft", f"₹{price_analysis['price_per_sqft']:,.0f}")
                with analysis_col4:
                    st.metric("Total Properties", f"{price_analysis['total_properties']:,}")
                
                # Price distribution chart
                st.write("**Price Distribution Analysis**")
                range_data = price_analysis['price_range']
                price_ranges = ['Min', 'Q25', 'Median', 'Q75', 'Max']
                price_values = [range_data['min'], range_data['q25'], price_analysis['median_price'], 
                              range_data['q75'], range_data['max']]
                
                fig_dist = px.bar(
                    x=price_ranges, 
                    y=price_values,
                    title=f'Price Distribution in {selected_city}',
                    color=price_values,
                    color_continuous_scale='viridis'
                )
                st.plotly_chart(fig_dist, use_container_width=True)
            
            # Model Performance Metrics
            st.subheader("🎯 AI Model Performance")
            model_metrics = st.session_state.predictor.get_model_metrics()
            
            if model_metrics:
                metrics_col1, metrics_col2 = st.columns(2)
                
                with metrics_col1:
                    st.write("**Model Accuracy Comparison**")
                    metrics_df = pd.DataFrame({
                        'Model': list(model_metrics.keys()),
                        'R² Score': [metrics['r2_score'] for metrics in model_metrics.values()],
                        'MAE': [metrics['mae'] for metrics in model_metrics.values()]
                    })
                    
                    fig_metrics = px.bar(
                        metrics_df, 
                        x='Model', 
                        y='R² Score',
                        title='Model Performance (R² Score)',
                        color='R² Score',
                        color_continuous_scale='viridis'
                    )
                    st.plotly_chart(fig_metrics, use_container_width=True)
                
                with metrics_col2:
                    st.write("**Feature Importance Analysis**")
                    feature_importance = st.session_state.predictor.get_feature_importance()
                    
                    if feature_importance and 'random_forest' in feature_importance:
                        rf_features = feature_importance['random_forest'][:5]  # Top 5 features
                        feature_names = [f[0] for f in rf_features]
                        feature_scores = [f[1] for f in rf_features]
                        
                        fig_features = px.bar(
                            x=feature_scores,
                            y=feature_names,
                            orientation='h',
                            title='Top Features (Random Forest)',
                            color=feature_scores,
                            color_continuous_scale='blues'
                        )
                        st.plotly_chart(fig_features, use_container_width=True)
            
            # City-wise comparison
            st.subheader("🌆 City Comparison")
            city_stats = st.session_state.combined_data.groupby('city')['price'].agg(['mean', 'median', 'count']).reset_index()
            city_stats.columns = ['City', 'Average Price', 'Median Price', 'Properties Count']
            
            comp_col1, comp_col2 = st.columns(2)
            
            with comp_col1:
                fig_city = px.bar(
                    city_stats, 
                    x='City', 
                    y='Average Price',
                    title='Average Property Prices by City',
                    color='Average Price',
                    color_continuous_scale='viridis'
                )
                fig_city.update_layout(height=400)
                st.plotly_chart(fig_city, use_container_width=True)
            
            with comp_col2:
                # Property type analysis for selected city
                city_type_data = city_data.groupby('property_type')['price'].mean().reset_index()
                fig_type = px.pie(
                    city_type_data,
                    values='price',
                    names='property_type',
                    title=f'Property Types in {selected_city}'
                )
                fig_type.update_layout(height=400)
                st.plotly_chart(fig_type, use_container_width=True)
    
    with col2:
        # EMI Calculator
        st.header("💳 EMI Calculator")
        
        if 'prediction_results' in st.session_state:
            default_price = st.session_state.prediction_results['price']
        else:
            default_price = 5000000
        
        emi_calc = EMICalculator()
        
        property_price = st.number_input(
            "Property Price (₹)",
            min_value=100000,
            max_value=100000000,
            value=int(default_price),
            step=100000
        )
        
        down_payment_percent = st.slider(
            "Down Payment (%)",
            min_value=10,
            max_value=50,
            value=20,
            step=5
        )
        
        loan_tenure = st.selectbox(
            "Loan Tenure (Years)",
            [5, 10, 15, 20, 25, 30],
            index=4
        )
        
        interest_rate = st.slider(
            "Interest Rate (% per annum)",
            min_value=6.5,
            max_value=12.0,
            value=8.5,
            step=0.25
        )
        
        # Calculate EMI
        down_payment = property_price * (down_payment_percent / 100)
        loan_amount = property_price - down_payment
        
        emi_amount = emi_calc.calculate_emi(loan_amount, interest_rate, loan_tenure)
        total_payment = emi_amount * loan_tenure * 12
        total_interest = total_payment - loan_amount
        
        # Display EMI details
        st.subheader("💰 Loan Breakdown")
        
        st.metric("Monthly EMI", f"₹{emi_amount:,.0f}")
        st.metric("Down Payment", f"₹{down_payment:,.0f}")
        st.metric("Loan Amount", f"₹{loan_amount:,.0f}")
        st.metric("Total Interest", f"₹{total_interest:,.0f}")
        st.metric("Total Payment", f"₹{total_payment:,.0f}")
        
        # EMI Chart
        months = list(range(1, loan_tenure * 12 + 1))
        remaining_balance = []
        current_balance = loan_amount
        
        monthly_rate = interest_rate / (12 * 100)
        
        for month in months:
            interest_payment = current_balance * monthly_rate
            principal_payment = emi_amount - interest_payment
            current_balance -= principal_payment
            remaining_balance.append(max(0, current_balance))
        
        fig_emi = go.Figure()
        fig_emi.add_trace(go.Scatter(
            x=months,
            y=remaining_balance,
            mode='lines',
            name='Outstanding Balance',
            line=dict(color='red', width=2)
        ))
        
        fig_emi.update_layout(
            title='Loan Outstanding Balance Over Time',
            xaxis_title='Months',
            yaxis_title='Outstanding Balance (₹)',
            height=300
        )
        
        st.plotly_chart(fig_emi, use_container_width=True)
    
    # Additional Market Insights
    st.header("📈 Additional Market Insights")
    
    if st.session_state.data_loaded:
        insights_col1, insights_col2 = st.columns(2)
        
        with insights_col1:
            # BHK-wise analysis
            bhk_stats = st.session_state.combined_data.groupby('bhk')['price'].mean().reset_index()
            fig_bhk = px.line(
                bhk_stats,
                x='bhk',
                y='price',
                title='Average Price by BHK Configuration',
                markers=True
            )
            st.plotly_chart(fig_bhk, use_container_width=True)
        
        with insights_col2:
            # Furnishing impact
            furnishing_stats = st.session_state.combined_data.groupby('furnishing')['price'].mean().reset_index()
            fig_furnishing = px.bar(
                furnishing_stats,
                x='furnishing',
                y='price',
                title='Average Price by Furnishing Type',
                color='price',
                color_continuous_scale='blues'
            )
            st.plotly_chart(fig_furnishing, use_container_width=True)
        
        # Investment Opportunity Analysis
        st.subheader("🎯 Investment Opportunity Score")
        if 'prediction_results' in st.session_state:
            opportunity_data = st.session_state.prediction_results
            
            # Calculate investment opportunity score based on multiple factors
            city_growth_rates = {'Mumbai': 7.5, 'Delhi': 8.0, 'Bangalore': 9.0, 'Gurugram': 8.5, 'Noida': 7.0}
            selected_growth_rate = city_growth_rates.get(selected_city, 7.5)
            
            price_per_sqft = opportunity_data['price'] / sq_ft
            city_avg_price_per_sqft = st.session_state.combined_data[
                st.session_state.combined_data['city'] == selected_city
            ]['price'].sum() / st.session_state.combined_data[
                st.session_state.combined_data['city'] == selected_city
            ]['area_sqft'].sum()
            
            # Scoring factors
            location_score = min(selected_growth_rate / 10 * 100, 100)
            price_score = max(0, (1 - (price_per_sqft / city_avg_price_per_sqft - 1)) * 100) if price_per_sqft <= city_avg_price_per_sqft else 50
            size_score = 100 if 800 <= sq_ft <= 2000 else 70
            bhk_score = 100 if 2 <= bhk <= 3 else 80
            furnishing_score = 90 if furnishing in ['Semi-Furnished', 'Fully Furnished'] else 70
            
            overall_score = (location_score * 0.3 + price_score * 0.25 + size_score * 0.2 + 
                           bhk_score * 0.15 + furnishing_score * 0.1)
            
            score_col1, score_col2, score_col3 = st.columns(3)
            with score_col1:
                st.metric("Overall Investment Score", f"{overall_score:.1f}/100")
            with score_col2:
                if overall_score >= 80:
                    recommendation = "Excellent Investment"
                    color = "🟢"
                elif overall_score >= 60:
                    recommendation = "Good Investment" 
                    color = "🟡"
                else:
                    recommendation = "Consider Alternatives"
                    color = "🔴"
                st.metric("Recommendation", f"{color} {recommendation}")
            with score_col3:
                st.metric("Expected Annual Growth", f"{selected_growth_rate}%")
            
            # Detailed scoring breakdown
            with st.expander("View Detailed Scoring Breakdown"):
                st.write(f"**Location Growth Potential:** {location_score:.1f}/100")
                st.write(f"**Price Competitiveness:** {price_score:.1f}/100") 
                st.write(f"**Property Size Optimality:** {size_score:.1f}/100")
                st.write(f"**BHK Configuration:** {bhk_score:.1f}/100")
                st.write(f"**Furnishing Value:** {furnishing_score:.1f}/100")
    
    # Database Analytics Dashboard
    st.header("🗄️ Database Analytics Dashboard")
    
    # Get market statistics from database
    market_stats = st.session_state.db_manager.get_market_statistics()
    
    if market_stats:
        # Overall market stats
        st.subheader("📈 Overall Market Statistics")
        if 'overall_statistics' in market_stats:
            stats = market_stats['overall_statistics']
            stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
            
            with stats_col1:
                st.metric("Total Properties", f"{stats['total_properties']:,}")
            with stats_col2:
                st.metric("Average Price", f"₹{stats['avg_price']:,.0f}")
            with stats_col3:
                st.metric("Price Range", f"₹{stats['min_price']:,.0f} - ₹{stats['max_price']:,.0f}")
            with stats_col4:
                st.metric("Average Area", f"{stats['avg_area']:,.0f} sq ft")
        
        # City-wise database statistics
        st.subheader("🏙️ City-wise Database Statistics")
        if 'city_statistics' in market_stats:
            city_stats_df = pd.DataFrame(market_stats['city_statistics'])
            
            db_col1, db_col2 = st.columns(2)
            
            with db_col1:
                fig_city_count = px.bar(
                    city_stats_df,
                    x='city',
                    y='total_properties',
                    title='Properties Count by City (Database)',
                    color='total_properties',
                    color_continuous_scale='blues'
                )
                st.plotly_chart(fig_city_count, use_container_width=True)
            
            with db_col2:
                fig_city_price_per_sqft = px.bar(
                    city_stats_df,
                    x='city',
                    y='avg_price_per_sqft',
                    title='Average Price per Sq Ft by City (Database)',
                    color='avg_price_per_sqft',
                    color_continuous_scale='viridis'
                )
                st.plotly_chart(fig_city_price_per_sqft, use_container_width=True)
        
        # Property type statistics
        st.subheader("🏠 Property Type Analysis (Database)")
        if 'property_types' in market_stats:
            prop_types_df = pd.DataFrame(market_stats['property_types'])
            
            prop_col1, prop_col2 = st.columns(2)
            
            with prop_col1:
                fig_prop_count = px.pie(
                    prop_types_df,
                    values='count',
                    names='type',
                    title='Property Distribution by Type'
                )
                st.plotly_chart(fig_prop_count, use_container_width=True)
            
            with prop_col2:
                fig_prop_price = px.bar(
                    prop_types_df,
                    x='type',
                    y='avg_price',
                    title='Average Price by Property Type',
                    color='avg_price',
                    color_continuous_scale='plasma'
                )
                st.plotly_chart(fig_prop_price, use_container_width=True)
    
    # Advanced Property Search using Database
    st.subheader("🔍 Advanced Property Search (Database)")
    
    # Database status info
    db_status = "🟢 Using CSV Data" if not st.session_state.db_manager.connection_available else "🟢 Database Connected"
    st.info(f"Data Source: {db_status} | Search from 500+ properties across 5 major cities")
    
    search_col1, search_col2, search_col3 = st.columns(3)
    
    with search_col1:
        search_city = st.selectbox("Search City", ['All'] + cities, key="search_city")
        search_min_area = st.number_input("Min Area (sq ft)", min_value=0, value=600, step=100, key="search_min_area")
        search_max_area = st.number_input("Max Area (sq ft)", min_value=0, value=2500, step=100, key="search_max_area")
    
    with search_col2:
        search_min_bhk = st.selectbox("Min BHK", [1, 2, 3, 4, 5], key="search_min_bhk")
        search_max_bhk = st.selectbox("Max BHK", [1, 2, 3, 4, 5], index=4, key="search_max_bhk")
        search_property_type = st.selectbox("Property Type", ['All'] + property_types, key="search_property_type")
    
    with search_col3:
        search_furnishing = st.selectbox("Furnishing", ['All'] + furnishing_options, key="search_furnishing")
        search_min_price = st.number_input("Min Price (₹)", min_value=0, value=5000000, step=100000, key="search_min_price")
        search_max_price = st.number_input("Max Price (₹)", min_value=0, value=75000000, step=1000000, key="search_max_price")
    
    if st.button("🔍 Search Properties", type="primary"):
        # Build search filters
        search_filters = {
            'min_area': search_min_area,
            'max_area': search_max_area,
            'min_bhk': search_min_bhk,
            'max_bhk': search_max_bhk,
            'min_price': search_min_price,
            'max_price': search_max_price
        }
        
        if search_city != 'All':
            search_filters['city'] = search_city
        if search_property_type != 'All':
            search_filters['property_type'] = search_property_type
        if search_furnishing != 'All':
            search_filters['furnishing'] = search_furnishing
        
        # Search properties from database
        search_results = st.session_state.db_manager.get_properties_by_filters(search_filters)
        
        if not search_results.empty:
            st.success(f"Found {len(search_results)} properties matching your criteria:")
            
            # Display search results
            display_cols = ['city', 'district', 'sub_district', 'area_sqft', 'bhk', 'property_type', 'furnishing', 'price']
            st.dataframe(search_results[display_cols], use_container_width=True)
            
            # Search results analytics
            if len(search_results) > 1:
                search_analytics_col1, search_analytics_col2 = st.columns(2)
                
                with search_analytics_col1:
                    st.metric("Average Price", f"₹{search_results['price'].mean():,.0f}")
                    st.metric("Price Range", f"₹{search_results['price'].min():,.0f} - ₹{search_results['price'].max():,.0f}")
                
                with search_analytics_col2:
                    st.metric("Average Area", f"{search_results['area_sqft'].mean():,.0f} sq ft")
                    st.metric("Avg Price/Sq Ft", f"₹{(search_results['price']/search_results['area_sqft']).mean():,.0f}")
                
                # Save search option
                save_search_name = st.text_input("Save this search as:", placeholder="e.g., 3BHK Mumbai under 2Cr")
                if st.button("💾 Save Search") and save_search_name:
                    if st.session_state.db_manager.save_search(st.session_state.session_id, save_search_name, search_filters):
                        st.success(f"Search saved as '{save_search_name}'")
                    else:
                        st.error("Failed to save search")
        else:
            st.warning("No properties found matching your criteria. Try adjusting the filters.")
    
    # Saved Searches
    with st.expander("💾 Your Saved Searches"):
        saved_searches = st.session_state.db_manager.get_saved_searches(st.session_state.session_id)
        if saved_searches:
            for search in saved_searches:
                st.write(f"**{search['search_name']}**")
                st.write(f"City: {search['city']} | BHK: {search['min_bhk']}-{search['max_bhk']} | "
                        f"Area: {search['min_area']}-{search['max_area']} sq ft")
                st.write(f"Price: ₹{search['min_price']:,} - ₹{search['max_price']:,}")
                st.write(f"Saved: {search['created_at'].strftime('%m/%d/%Y %H:%M')}")
                st.write("---")
        else:
            st.write("No saved searches found.")
    
def property_valuation_interface():
    """Interface for property valuation and sell/hold analysis"""
    st.header("🏡 Property Valuation & Sell/Hold Analysis")
    st.markdown("Evaluate your existing property's current value and get recommendations on whether to sell or hold.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📝 Property Details")
        
        # Property purchase information
        purchase_price = st.number_input(
            "Original Purchase Price (₹)",
            min_value=100000,
            max_value=500000000,
            value=5000000,
            step=100000
        )
        
        purchase_date = st.date_input(
            "Purchase Date",
            value=pd.to_datetime("2020-01-01"),
            min_value=pd.to_datetime("2000-01-01"),
            max_value=pd.to_datetime("2024-12-31")
        )
        
        # Property characteristics
        prop_col1, prop_col2 = st.columns(2)
        
        with prop_col1:
            prop_city = st.selectbox("City", ['Mumbai', 'Delhi', 'Gurugram', 'Noida', 'Bangalore'], key="prop_city")
            
            # Get districts for selected city
            if hasattr(st.session_state, 'combined_data') and st.session_state.combined_data is not None:
                districts = st.session_state.data_loader.get_districts_by_city(prop_city, st.session_state.combined_data)
            else:
                districts = st.session_state.data_loader.get_districts_by_city(prop_city)
            prop_district = st.selectbox("District", districts, key="prop_district") if districts else None
            
            prop_type = st.selectbox("Property Type", ['Apartment', 'Villa', 'Independent House', 'Studio', 'Penthouse'], key="prop_type")
        
        with prop_col2:
            # Get sub-districts for selected district
            if prop_district:
                if hasattr(st.session_state, 'combined_data') and st.session_state.combined_data is not None:
                    subdistricts = st.session_state.data_loader.get_subdistricts_by_district(prop_city, prop_district, st.session_state.combined_data)
                else:
                    subdistricts = st.session_state.data_loader.get_subdistricts_by_district(prop_city, prop_district)
                prop_subdistrict = st.selectbox("Sub-District", subdistricts, key="prop_subdistrict") if subdistricts else None
            else:
                prop_subdistrict = None
                st.info("Select a district to see sub-districts")
            
            prop_area = st.number_input("Area (sq ft)", min_value=200, max_value=5000, value=1200, key="prop_area")
            prop_bhk = st.selectbox("BHK", [1, 2, 3, 4, 5], index=1, key="prop_bhk")
        
        # Current market price (optional)
        current_market_price = st.number_input(
            "Current Market Price (₹) - Optional for comparison",
            min_value=0,
            value=0,
            step=100000,
            help="Enter current market price of similar properties for comparison"
        )
        
        if st.button("🔍 Analyze Property Value", type="primary"):
            # Calculate current property value
            property_value = st.session_state.property_analyzer.calculate_current_property_value(
                purchase_price=purchase_price,
                purchase_date=purchase_date.strftime('%Y-%m-%d'),
                city=prop_city,
                property_type=prop_type,
                district=prop_district,
                sub_district=prop_subdistrict
            )
            
            if property_value:
                st.session_state.property_valuation_results = property_value
                
                # Get sell/hold recommendation
                sell_hold_analysis = st.session_state.property_analyzer.should_sell_or_hold(
                    property_value, 
                    current_market_price if current_market_price > 0 else None
                )
                st.session_state.sell_hold_results = sell_hold_analysis
                
                # Calculate exit strategy
                exit_strategy = st.session_state.property_analyzer.calculate_optimal_exit_strategy(property_value)
                st.session_state.exit_strategy_results = exit_strategy
                
                st.rerun()
    
    with col2:
        # Display user's property history from database
        st.subheader("📋 Your Property Portfolio")
        user_analytics = st.session_state.db_manager.get_user_analytics(st.session_state.session_id)
        
        if user_analytics.get('predictions_made', 0) > 0:
            st.metric("Properties Analyzed", user_analytics['predictions_made'])
            st.metric("Avg Property Value", f"₹{user_analytics.get('avg_property_price', 0):,.0f}")
        else:
            st.info("No properties analyzed yet. Start by analyzing your first property!")
    
    # Display results if available
    if 'property_valuation_results' in st.session_state:
        results = st.session_state.property_valuation_results
        
        st.markdown("---")
        st.subheader("📊 Valuation Results")
        
        # Property location information
        if results.get('district') or results.get('sub_district'):
            st.subheader("📍 Property Location")
            loc_col1, loc_col2, loc_col3 = st.columns(3)
            
            with loc_col1:
                st.write(f"**City:** {results['city']}")
            with loc_col2:
                if results.get('district'):
                    st.write(f"**District:** {results['district']}")
            with loc_col3:
                if results.get('sub_district'):
                    st.write(f"**Sub-District:** {results['sub_district']}")
        
        # Key metrics
        metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
        
        with metrics_col1:
            st.metric("Current Value", f"₹{results['current_estimated_value']:,.0f}")
        with metrics_col2:
            st.metric("Total Gain", f"₹{results['total_gain']:,.0f}")
        with metrics_col3:
            st.metric("Total Return", f"{results['total_gain_percentage']:.1f}%")
        with metrics_col4:
            st.metric("Annual Return", f"{results['annual_gain_percentage']:.1f}%")
        
        # Sell/Hold Analysis
        if 'sell_hold_results' in st.session_state:
            sell_hold = st.session_state.sell_hold_results
            
            st.subheader("🤔 Sell or Hold Recommendation")
            
            rec_col1, rec_col2 = st.columns([1, 2])
            
            with rec_col1:
                # Recommendation badge
                rec_color = {
                    "HOLD": "🟢",
                    "NEUTRAL": "🟡", 
                    "CONSIDER SELLING": "🔴"
                }.get(sell_hold['recommendation'], "⚪")
                
                st.markdown(f"### {rec_color} {sell_hold['recommendation']}")
                st.write(f"**Confidence:** {sell_hold['confidence']}")
                st.write(f"**Score:** {sell_hold['recommendation_score']:.1f}/100")
            
            with rec_col2:
                st.write(f"**Reasoning:** {sell_hold['reasoning']}")
                
                if sell_hold.get('market_comparison'):
                    st.write(f"**Market Analysis:** {sell_hold['market_comparison']}")
            
            # Detailed factors
            factor_col1, factor_col2 = st.columns(2)
            
            with factor_col1:
                if sell_hold['hold_factors']:
                    st.write("**✅ Factors Supporting HOLD:**")
                    for factor in sell_hold['hold_factors']:
                        st.write(f"• {factor}")
            
            with factor_col2:
                if sell_hold['sell_factors']:
                    st.write("**⚠️ Factors Supporting SELL:**")
                    for factor in sell_hold['sell_factors']:
                        st.write(f"• {factor}")
            
            # Future projections
            st.subheader("📈 Future Value Projections")
            proj_col1, proj_col2, proj_col3 = st.columns(3)
            
            with proj_col1:
                st.metric("1 Year", f"₹{sell_hold['projected_1_year_value']:,.0f}")
            with proj_col2:
                st.metric("3 Years", f"₹{sell_hold['projected_3_year_value']:,.0f}")
            with proj_col3:
                st.metric("5 Years", f"₹{sell_hold['projected_5_year_value']:,.0f}")
        
        # Exit Strategy
        if 'exit_strategy_results' in st.session_state:
            exit_data = st.session_state.exit_strategy_results
            
            st.subheader("🎯 Optimal Exit Strategy")
            
            exit_col1, exit_col2 = st.columns(2)
            
            with exit_col1:
                st.metric("Current Return", f"{exit_data['current_return_percentage']:.1f}%")
                
                if exit_data['target_achieved']:
                    st.success("🎉 Target return already achieved!")
                else:
                    st.metric("Years to 15% Return", f"{exit_data['years_to_target']:.1f}")
            
            with exit_col2:
                st.write(f"**Recommended Hold Period:** {exit_data['recommendation']['optimal_hold_period']}")
                st.write(f"**Strategy:** {exit_data['recommendation']['reasoning']}")

def investment_analysis_interface():
    """Interface for analyzing new investment opportunities"""
    st.header("💼 Investment Opportunity Analysis")
    st.markdown("Analyze whether a property at a specific price is a good investment opportunity.")
    
    # Investment analysis form
    st.subheader("🎯 Property Investment Analysis")
    
    inv_col1, inv_col2 = st.columns(2)
    
    with inv_col1:
        asking_price = st.number_input(
            "Property Asking Price (₹)",
            min_value=100000,
            max_value=500000000,
            value=8000000,
            step=100000
        )
        
        inv_city = st.selectbox("City", ['Mumbai', 'Delhi', 'Gurugram', 'Noida', 'Bangalore'], key="inv_city")
        
        # Get districts for selected city
        if hasattr(st.session_state, 'combined_data') and st.session_state.combined_data is not None:
            inv_districts = st.session_state.data_loader.get_districts_by_city(inv_city, st.session_state.combined_data)
        else:
            inv_districts = st.session_state.data_loader.get_districts_by_city(inv_city)
        inv_district = st.selectbox("District", inv_districts, key="inv_district") if inv_districts else None
        
        inv_area = st.number_input("Area (sq ft)", min_value=200, max_value=5000, value=1000, key="inv_area")
        inv_bhk = st.selectbox("BHK", [1, 2, 3, 4, 5], index=1, key="inv_bhk")
    
    with inv_col2:
        # Get sub-districts for selected district
        if inv_district:
            if hasattr(st.session_state, 'combined_data') and st.session_state.combined_data is not None:
                inv_subdistricts = st.session_state.data_loader.get_subdistricts_by_district(inv_city, inv_district, st.session_state.combined_data)
            else:
                inv_subdistricts = st.session_state.data_loader.get_subdistricts_by_district(inv_city, inv_district)
            inv_subdistrict = st.selectbox("Sub-District", inv_subdistricts, key="inv_subdistrict") if inv_subdistricts else None
        else:
            inv_subdistrict = None
            st.info("Select a district to see sub-districts")
        
        inv_property_type = st.selectbox("Property Type", ['Apartment', 'Villa', 'Independent House', 'Studio', 'Penthouse'], key="inv_property_type")
        inv_furnishing = st.selectbox("Furnishing", ['Unfurnished', 'Semi-Furnished', 'Fully Furnished'], key="inv_furnishing")
        
        # Optional comparable price
        comparable_price = st.number_input(
            "Comparable Market Price (₹) - Optional",
            min_value=0,
            value=0,
            step=100000,
            help="Price of similar properties in the area"
        )
    
    if st.button("📊 Analyze Investment Opportunity", type="primary"):
        property_details = {
            'city': inv_city,
            'area_sqft': inv_area,
            'bhk': inv_bhk,
            'property_type': inv_property_type,
            'furnishing': inv_furnishing,
            'district': inv_district,
            'sub_district': inv_subdistrict
        }
        
        # Perform investment analysis
        investment_analysis = st.session_state.property_analyzer.analyze_investment_opportunity(
            asking_price=asking_price,
            property_details=property_details,
            comparable_market_price=comparable_price if comparable_price > 0 else None
        )
        
        if investment_analysis:
            st.session_state.investment_analysis_results = investment_analysis
            st.rerun()
    
    # Display investment analysis results
    if 'investment_analysis_results' in st.session_state:
        analysis = st.session_state.investment_analysis_results
        
        st.markdown("---")
        st.subheader("📊 Investment Analysis Results")
        
        # Overall recommendation
        rec_colors = {
            "EXCELLENT BUY": "🟢",
            "GOOD BUY": "🟢",
            "FAIR BUY": "🟡",
            "PROCEED WITH CAUTION": "🟠",
            "AVOID": "🔴"
        }
        
        rec_color = rec_colors.get(analysis['recommendation'], "⚪")
        
        result_col1, result_col2, result_col3 = st.columns([1, 1, 1])
        
        with result_col1:
            st.markdown(f"### {rec_color} {analysis['recommendation']}")
            st.write(f"**Confidence:** {analysis['confidence']}")
        
        with result_col2:
            st.metric("Investment Score", f"{analysis['investment_score']}/100")
        
        with result_col3:
            price_per_sqft = asking_price / inv_area
            st.metric("Price per Sq Ft", f"₹{price_per_sqft:,.0f}")
        
        # Property location details
        if inv_district or inv_subdistrict:
            st.subheader("📍 Investment Location Analysis")
            loc_col1, loc_col2, loc_col3 = st.columns(3)
            
            with loc_col1:
                st.write(f"**City:** {inv_city}")
            with loc_col2:
                if inv_district:
                    st.write(f"**District:** {inv_district}")
            with loc_col3:
                if inv_subdistrict:
                    st.write(f"**Sub-District:** {inv_subdistrict}")
        
        st.write(f"**Summary:** {analysis['summary']}")
        
        # Key insights and risk factors
        insight_col1, insight_col2 = st.columns(2)
        
        with insight_col1:
            if analysis['key_insights']:
                st.write("**✅ Key Investment Strengths:**")
                for insight in analysis['key_insights']:
                    st.write(f"• {insight}")
        
        with insight_col2:
            if analysis['risk_factors']:
                st.write("**⚠️ Risk Factors:**")
                for risk in analysis['risk_factors']:
                    st.write(f"• {risk}")
        
        # Financial projections
        st.subheader("💰 Financial Projections")
        projections = analysis['financial_projections']
        
        proj_metrics_col1, proj_metrics_col2, proj_metrics_col3, proj_metrics_col4 = st.columns(4)
        
        with proj_metrics_col1:
            st.metric("1 Year Value", f"₹{projections['1_year_value']:,.0f}")
        with proj_metrics_col2:
            st.metric("3 Year Value", f"₹{projections['3_year_value']:,.0f}")
        with proj_metrics_col3:
            st.metric("5 Year Value", f"₹{projections['5_year_value']:,.0f}")
        with proj_metrics_col4:
            st.metric("10 Year Value", f"₹{projections['10_year_value']:,.0f}")
        
        # Market comparison
        if projections.get('price_premium_percentage') is not None:
            premium = projections['price_premium_percentage']
            benchmark = projections['market_benchmark_sqft']
            
            st.write(f"**Market Analysis:**")
            st.write(f"• Asking price per sq ft: ₹{projections['price_per_sqft']:,.0f}")
            st.write(f"• Market benchmark: ₹{benchmark:,.0f} per sq ft")
            
            if premium > 0:
                st.write(f"• Price premium: {premium:.1f}% above market")
            else:
                st.write(f"• Price discount: {abs(premium):.1f}% below market")

    # Market insights for investment decisions
    st.subheader("🌟 Investment Market Insights")
    
    market_col1, market_col2 = st.columns(2)
    
    with market_col1:
        st.write("**🏆 Top Investment Cities (2024-25):**")
        st.write("1. **Bangalore** - 9.2% projected growth")
        st.write("2. **Gurugram** - 8.5% projected growth") 
        st.write("3. **Delhi** - 8.0% projected growth")
        st.write("4. **Mumbai** - 7.5% projected growth")
        st.write("5. **Noida** - 7.0% projected growth")
    
    with market_col2:
        st.write("**💡 Investment Tips:**")
        st.write("• Look for properties 10-15% below market rate")
        st.write("• Focus on 2-3 BHK apartments for better liquidity")
        st.write("• Consider emerging areas with infrastructure development")
        st.write("• Factor in rental yield potential (4-6% annually)")
        st.write("• Plan for 5-7 year investment horizon for optimal returns")

def ai_assistant_interface():
    """Enhanced AI Chatbot Interface with validation and monitoring"""
    
    # Rate limiting for chat messages
    session_id = st.session_state.get('session_id', 'unknown')
    if not rate_limiter.is_allowed(session_id, 'chat', config.RATE_LIMIT['api_calls_per_minute'], 1):
        st.error("You've sent too many messages. Please wait a moment before sending another.")
        return
    
    if st.session_state.chatbot is None:
        st.warning("🤖 AI Assistant is loading... Please wait a moment.")
        st.info("The AI Assistant will be available once the data and ML models are fully loaded.")
        return
    
    # Enhanced chatbot interface with validation
    st.header("🤖 AI Real Estate Assistant")
    st.markdown("Ask me about property prices, market trends, investment advice, or EMI calculations!")
    
    # Chat input with validation
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        # Validate chat input
        is_valid, error_msg = InputValidator.validate_chat_input(user_input)
        
        if not is_valid:
            st.error(error_msg)
            return
        
        # Sanitize input
        sanitized_input = InputValidator.sanitize_text_input(user_input, 500)
        
        # Add user message to chat history
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        st.session_state.chat_history.append({
            "role": "user",
            "content": sanitized_input,
            "timestamp": datetime.now().isoformat()
        })
        
        # Generate bot response with monitoring
        timer_id = performance_monitor.start_timer("chatbot_response")
        
        try:
            def get_bot_response():
                return st.session_state.chatbot.generate_response(sanitized_input)
            
            bot_response = safe_execute(
                get_bot_response,
                error_handler,
                fallback_value="I'm sorry, I'm having trouble processing your request right now. Please try again.",
                context="chatbot_response"
            )
            
            # Record response time
            duration = performance_monitor.end_timer(timer_id, "chatbot_response")
            
            # Add bot response to chat history
            st.session_state.chat_history.append({
                "role": "assistant", 
                "content": bot_response,
                "timestamp": datetime.now().isoformat()
            })
            
            # Log interaction
            log_user_interaction("chat_message", {
                "message_length": len(sanitized_input),
                "response_time": duration
            })
            
        except Exception as e:
            performance_monitor.end_timer(timer_id, "chatbot_response")
            error_msg = error_handler.handle_prediction_error(e, {"input": sanitized_input})
            st.error(error_msg)
    
    # Display chat history
    if 'chat_history' in st.session_state:
        for message in st.session_state.chat_history[-10:]:  # Show last 10 messages
            with st.chat_message(message["role"]):
                st.write(message["content"])
    
    # Chat controls
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()
    
    with col2:
        if st.button("📊 Chat Analytics") and config.DEBUG:
            if 'chat_history' in st.session_state:
                st.json({
                    "total_messages": len(st.session_state.chat_history),
                    "user_messages": len([m for m in st.session_state.chat_history if m["role"] == "user"]),
                    "assistant_messages": len([m for m in st.session_state.chat_history if m["role"] == "assistant"])
                })

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center'>
            <p><strong>AI Real Estate Price Predictor with Gemini AI</strong> | Powered by Machine Learning & Google Gemini 2.5</p>
            <p><em>Advanced AI insights for smart real estate decisions</em></p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()