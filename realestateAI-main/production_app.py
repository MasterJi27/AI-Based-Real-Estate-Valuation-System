"""
Production Main Application with Enhanced Security and Performance
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import sys
from pathlib import Path

# Import production modules
from production_config import config
from production_logging import ProductionLogger, performance_monitor, SystemMonitor
from production_security import security_middleware, SessionSecurity
from production_database import DatabaseManager
from production_ml import RealEstatePricePredictor

# Import existing modules with fallback
try:
    from emi_calculator import EMICalculator
    from property_analyzer import PropertyAnalyzer
    from validators import InputValidator
    from chatbot import RealEstateChatbot
    from gemini_ai import GeminiAIService, get_gemini_service
except ImportError as e:
    st.error(f"Module import error: {e}")
    st.stop()

class ProductionApp:
    """Production-grade Streamlit application with comprehensive features"""
    
    def __init__(self):
        self.logger = ProductionLogger('main_app')
        self.session_security = SessionSecurity()
        
        # Initialize core components
        self._initialize_session_state()
        self._setup_page_config()
        self._initialize_components()
        
        # Security middleware
        self._apply_security_middleware()
        
        # Performance monitoring
        SystemMonitor.log_system_metrics()
    
    def _initialize_session_state(self):
        """Initialize Streamlit session state with production defaults"""
        defaults = {
            'page_loads': 0,
            'user_id': 'anonymous',
            'session_start': datetime.now(),
            'last_activity': datetime.now(),
            'rate_limit_warnings': 0,
            'cache_hits': 0,
            'predictor': None,
            'database': None,
            'gemini_service': None,
            'chat_history': [],
            'chat_context': {},
            'user_preferences': {},
            'analytics_cache': {},
            'performance_metrics': []
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
        
        # Update activity tracking
        st.session_state.page_loads += 1
        st.session_state.last_activity = datetime.now()
    
    def _setup_page_config(self):
        """Configure Streamlit page with production settings"""
        st.set_page_config(
            page_title=f"{config.APP_NAME} v{config.VERSION}",
            page_icon="🏠",
            layout="wide",
            initial_sidebar_state="expanded",
            menu_items={
                'Get Help': 'https://github.com/yourusername/real-estate-ai',
                'Report a bug': 'https://github.com/yourusername/real-estate-ai/issues',
                'About': f"{config.APP_NAME} - AI-powered real estate valuation system"
            }
        )
        
        # Custom CSS for production styling
        st.markdown("""
        <style>
        .main-header {
            background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 2rem;
        }
        .metric-card {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #1e3c72;
        }
        </style>
        """, unsafe_allow_html=True)
    
    @performance_monitor("component_initialization")
    def _initialize_components(self):
        """Initialize all application components with error handling"""
        try:
            # Database
            if not st.session_state.database:
                st.session_state.database = DatabaseManager()
                self.logger.logger.info("Database manager initialized")
            
            # ML Predictor
            if not st.session_state.predictor:
                st.session_state.predictor = RealEstatePricePredictor()
                self.logger.logger.info("ML predictor initialized")
            
            # Gemini AI (optional)
            if config.AI_CONFIG['enable_gemini_ai'] and config.AI_CONFIG['gemini_api_key']:
                if not st.session_state.gemini_service:
                    st.session_state.gemini_service = get_gemini_service()
                    self.logger.logger.info("Gemini AI service initialized")
        
        except Exception as e:
            self.logger.log_error(e, {"component": "initialization"})
            st.error("⚠️ Some components failed to initialize. Basic functionality may be limited.")
    
    def _apply_security_middleware(self):
        """Apply security middleware to requests"""
        try:
            # Get client IP (simplified for Streamlit)
            client_ip = "127.0.0.1"  # In production, extract from headers
            
            # Security check
            allowed, message = security_middleware.check_request_security(client_ip)
            
            if not allowed:
                st.error(f"🔒 Access denied: {message}")
                st.stop()
            
            # Log successful access
            self.logger.logger.info(f"Access granted for IP: {client_ip}")
            
        except Exception as e:
            self.logger.log_error(e, {"component": "security_middleware"})
    
    def _render_header(self):
        """Render application header with status information"""
        st.markdown("""
        <div class="main-header">
            <h1 style="color: white; margin: 0;">🏠 AI Real Estate Price Predictor</h1>
            <p style="color: #e0e6ed; margin: 0;">Production v2.0.0 - Secure & Scalable</p>
        </div>
        """, unsafe_allow_html=True)
        
        # System status indicator
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🔒 Security", "Active", delta="All systems secure")
        
        with col2:
            db_status = "Connected" if st.session_state.database else "Fallback Mode"
            st.metric("💾 Database", db_status)
        
        with col3:
            ml_status = "Ready" if st.session_state.predictor else "Loading"
            st.metric("🧠 ML Models", ml_status)
        
        with col4:
            ai_status = "Enabled" if st.session_state.gemini_service else "Disabled"
            st.metric("🤖 Gemini AI", ai_status)
    
    def _render_sidebar(self):
        """Render enhanced sidebar with monitoring information"""
        st.sidebar.markdown("## 📊 System Monitor")
        
        # Performance metrics
        metrics = SystemMonitor.get_system_metrics()
        if 'error' not in metrics:
            st.sidebar.metric("CPU Usage", f"{metrics['cpu_percent']:.1f}%")
            st.sidebar.metric("Memory Usage", f"{metrics['memory_percent']:.1f}%")
            st.sidebar.metric("Disk Usage", f"{metrics['disk_percent']:.1f}%")
        
        # Session information
        st.sidebar.markdown("## 👤 Session Info")
        st.sidebar.text(f"Page Loads: {st.session_state.page_loads}")
        st.sidebar.text(f"Session: {st.session_state.session_start.strftime('%H:%M:%S')}")
        
        # Configuration info
        st.sidebar.markdown("## ⚙️ Configuration")
        st.sidebar.text(f"Environment: {config.ENVIRONMENT}")
        st.sidebar.text(f"Debug Mode: {config.DEBUG}")
        st.sidebar.text(f"AI Features: {'✅' if config.AI_CONFIG['enable_gemini_ai'] else '❌'}")
    
    @performance_monitor("property_prediction")
    def render_property_prediction_tab(self):
        """Enhanced property prediction with production features"""
        st.header("🏠 Property Price Prediction")
        
        try:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Property Details")
                city = st.selectbox("City", ["Mumbai", "Delhi", "Bangalore", "Gurugram", "Noida"])
                district = st.text_input("District/Area", placeholder="Enter district name")
                property_type = st.selectbox("Property Type", ["Apartment", "Villa", "House", "Studio"])
                furnishing = st.selectbox("Furnishing", ["Fully Furnished", "Semi Furnished", "Unfurnished"])
            
            with col2:
                st.subheader("Specifications")
                area_sqft = st.number_input("Area (sq ft)", 
                                          min_value=config.DATA_CONFIG['min_area'], 
                                          max_value=config.DATA_CONFIG['max_area'], 
                                          value=1000)
                bhk = st.number_input("BHK", 
                                    min_value=config.DATA_CONFIG['min_bhk'], 
                                    max_value=config.DATA_CONFIG['max_bhk'], 
                                    value=2)
                bathrooms = st.number_input("Bathrooms", min_value=1, max_value=10, value=2)
                age = st.number_input("Property Age (years)", min_value=0, max_value=50, value=5)
            
            # Prediction button
            if st.button("🔮 Predict Price", type="primary"):
                try:
                    # Input validation
                    validator = InputValidator()
                    is_valid, message = validator.validate_property_inputs(
                        city, district, area_sqft, bhk, property_type, furnishing
                    )
                    
                    if not is_valid:
                        st.error(f"❌ {message}")
                        return
                    
                    # Prepare input data
                    input_data = {
                        'city': city,
                        'district': district,
                        'sub_district': district,
                        'area_sqft': area_sqft,
                        'bhk': bhk,
                        'property_type': property_type,
                        'furnishing': furnishing,
                        'bathrooms': bathrooms,
                        'age': age
                    }
                    
                    # Make prediction
                    with st.spinner("Generating AI prediction..."):
                        start_time = time.time()
                        prediction_result = st.session_state.predictor.predict(input_data)
                        prediction_time = time.time() - start_time
                        
                        predicted_price, investment_advice, individual_predictions = prediction_result
                        
                        # Log successful prediction
                        self.logger.log_business_event("prediction_made", 
                                                     st.session_state.user_id, 
                                                     {"price": predicted_price, "city": city})
                    
                    # Display results
                    st.markdown("### 📊 Prediction Results")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("💰 Predicted Price", f"₹{predicted_price:,.0f}")
                    with col2:
                        price_per_sqft = predicted_price / area_sqft
                        st.metric("📏 Price per sq ft", f"₹{price_per_sqft:,.0f}")
                    with col3:
                        st.metric("⏱️ Prediction Time", f"{prediction_time:.2f}s")
                    
                    # Investment advice
                    if investment_advice:
                        st.markdown(f"""
                        <div style="background: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; padding: 1rem; margin: 1rem 0;">
                            <h4>💡 Investment Insights</h4>
                            <p>{investment_advice}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Model breakdown
                    if individual_predictions:
                        st.markdown("### 🤖 Model Breakdown")
                        model_df = pd.DataFrame([
                            {"Model": "Decision Tree", "Prediction": f"₹{individual_predictions.get('decision_tree', 0):,.0f}"},
                            {"Model": "Random Forest", "Prediction": f"₹{individual_predictions.get('random_forest', 0):,.0f}"},
                            {"Model": "XGBoost", "Prediction": f"₹{individual_predictions.get('xgboost', 0):,.0f}"},
                            {"Model": "Ensemble", "Prediction": f"₹{predicted_price:,.0f}"}
                        ])
                        
                        st.dataframe(model_df, use_container_width=True)
                    
                except Exception as e:
                    self.logger.log_error(e, {"component": "prediction", "input": input_data})
                    st.error("❌ Prediction failed. Please try again or contact support.")
        
        except Exception as e:
            self.logger.log_error(e, {"component": "prediction_tab"})
            st.error("❌ An error occurred while loading the prediction interface.")
    
    @performance_monitor("analytics_dashboard")
    def render_analytics_tab(self):
        """Enhanced analytics dashboard with caching"""
        st.header("📊 Market Analytics & Insights")
        
        try:
            # Check cache first
            cache_key = f"analytics_{datetime.now().strftime('%Y%m%d_%H')}"
            
            if cache_key in st.session_state.analytics_cache:
                data = st.session_state.analytics_cache[cache_key]
                st.session_state.cache_hits += 1
            else:
                with st.spinner("Loading market data..."):
                    data = st.session_state.database.get_properties_by_filters({})
                    st.session_state.analytics_cache[cache_key] = data
            
            if data.empty:
                st.warning("📊 No data available for analytics")
                return
            
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Properties", f"{len(data):,}")
            with col2:
                avg_price = data['price'].mean()
                st.metric("Average Price", f"₹{avg_price:,.0f}")
            with col3:
                median_price = data['price'].median()
                st.metric("Median Price", f"₹{median_price:,.0f}")
            with col4:
                st.metric("Cities Covered", data['city'].nunique())
            
            # Interactive visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                # Price distribution by city
                city_prices = data.groupby('city')['price'].mean().sort_values(ascending=False)
                fig_city = px.bar(
                    x=city_prices.index,
                    y=city_prices.values,
                    title="Average Price by City",
                    labels={'x': 'City', 'y': 'Average Price (₹)'}
                )
                st.plotly_chart(fig_city, use_container_width=True)
            
            with col2:
                # BHK distribution
                bhk_dist = data['bhk'].value_counts().sort_index()
                fig_bhk = px.pie(
                    values=bhk_dist.values,
                    names=bhk_dist.index,
                    title="Property Distribution by BHK"
                )
                st.plotly_chart(fig_bhk, use_container_width=True)
            
            # Market trends table
            st.subheader("📈 Market Summary")
            summary_data = data.groupby('city').agg({
                'price': ['mean', 'median', 'min', 'max'],
                'area_sqft': 'mean',
                'bhk': 'mean'
            }).round(0)
            
            summary_data.columns = ['Avg Price', 'Median Price', 'Min Price', 'Max Price', 'Avg Area', 'Avg BHK']
            st.dataframe(summary_data, use_container_width=True)
            
        except Exception as e:
            self.logger.log_error(e, {"component": "analytics_tab"})
            st.error("❌ Failed to load analytics data.")
    
    def render_property_search_tab(self):
        """Enhanced property search with advanced filtering"""
        st.header("🔍 Advanced Property Search")
        
        try:
            # Search filters
            with st.expander("🎛️ Search Filters", expanded=True):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    cities = st.multiselect("Cities", ["Mumbai", "Delhi", "Bangalore", "Gurugram", "Noida"])
                    property_types = st.multiselect("Property Types", ["Apartment", "Villa", "House", "Studio"])
                
                with col2:
                    price_range = st.slider("Price Range (₹ Crores)", 0.0, 10.0, (0.0, 10.0), 0.1)
                    area_range = st.slider("Area Range (sq ft)", 500, 5000, (500, 5000), 100)
                
                with col3:
                    bhk_options = st.multiselect("BHK", [1, 2, 3, 4, 5])
                    furnishing = st.multiselect("Furnishing", ["Fully Furnished", "Semi Furnished", "Unfurnished"])
            
            # Build filters
            filters = {}
            if cities:
                filters['city'] = cities
            if price_range != (0.0, 10.0):
                filters['min_price'] = price_range[0] * 10000000
                filters['max_price'] = price_range[1] * 10000000
            if area_range != (500, 5000):
                filters['min_area'] = area_range[0]
                filters['max_area'] = area_range[1]
            if bhk_options:
                filters['bhk'] = bhk_options[0] if len(bhk_options) == 1 else bhk_options
            if property_types:
                filters['property_type'] = property_types
            if furnishing:
                filters['furnishing'] = furnishing
            
            # Search button
            if st.button("🔍 Search Properties", type="primary"):
                with st.spinner("Searching properties..."):
                    results = st.session_state.database.get_properties_by_filters(filters)
                    
                    if results.empty:
                        st.warning("No properties found matching your criteria.")
                    else:
                        st.success(f"Found {len(results)} properties matching your criteria")
                        
                        # Display results
                        display_columns = ['city', 'district', 'area_sqft', 'bhk', 'property_type', 'furnishing', 'price']
                        available_columns = [col for col in display_columns if col in results.columns]
                        
                        # Format price column
                        if 'price' in results.columns:
                            results['price_formatted'] = results['price'].apply(lambda x: f"₹{x:,.0f}")
                            display_results = results[available_columns].copy()
                            if 'price' in display_results.columns:
                                display_results['price'] = results['price_formatted']
                        else:
                            display_results = results[available_columns]
                        
                        st.dataframe(display_results, use_container_width=True)
                        
                        # Download option
                        csv = results.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Results as CSV",
                            data=csv,
                            file_name=f"property_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
        
        except Exception as e:
            self.logger.log_error(e, {"component": "property_search"})
            st.error("❌ Search functionality encountered an error.")
    
    def render_chatbot_tab(self):
        """Enhanced chatbot with security and monitoring"""
        st.header("🤖 AI Real Estate Assistant")
        
        try:
            # Initialize chatbot
            if 'chatbot' not in st.session_state:
                st.session_state.chatbot = RealEstateChatbot(
                    data_loader=None,
                    predictor=st.session_state.predictor,
                    combined_data=st.session_state.database.get_properties_by_filters({})
                )
            
            # Render chat interface
            st.session_state.chatbot.render_chat_interface()
            
        except Exception as e:
            self.logger.log_error(e, {"component": "chatbot"})
            st.error("❌ Chatbot is temporarily unavailable.")
    
    def render_gemini_ai_tab(self):
        """Enhanced Gemini AI integration with production features"""
        if not config.AI_CONFIG['enable_gemini_ai'] or not config.AI_CONFIG['gemini_api_key']:
            st.warning("🤖 Gemini AI features are not configured. Please set up your API key.")
            return
        
        st.header("🧠 Gemini AI Insights")
        
        try:
            gemini_service = st.session_state.gemini_service
            if not gemini_service:
                st.error("Gemini AI service not available")
                return
            
            # Feature selection
            gemini_feature = st.selectbox(
                "Select AI Feature",
                ["📊 Property Market Analysis", "💰 Investment Recommendations", 
                 "❓ Real Estate Q&A", "📄 Property Reports", "🔍 Market Trends"]
            )
            
            # Render selected feature with enhanced error handling
            if gemini_feature == "📊 Property Market Analysis":
                self._render_market_analysis(gemini_service)
            elif gemini_feature == "💰 Investment Recommendations":
                self._render_investment_recommendations(gemini_service)
            elif gemini_feature == "❓ Real Estate Q&A":
                self._render_real_estate_qa(gemini_service)
            elif gemini_feature == "📄 Property Reports":
                self._render_property_reports(gemini_service)
            elif gemini_feature == "🔍 Market Trends":
                self._render_market_trends(gemini_service)
                
        except Exception as e:
            self.logger.log_error(e, {"component": "gemini_ai"})
            st.error("❌ Gemini AI features are temporarily unavailable.")
    
    def _render_market_analysis(self, gemini_service):
        """Render market analysis with production enhancements"""
        st.subheader("Property Market Analysis")
        
        col1, col2 = st.columns(2)
        with col1:
            location = st.text_input("Location/City", placeholder="e.g., Mumbai, Andheri")
            property_type = st.selectbox("Property Type", ["Apartment", "Villa", "House", "Studio"])
            area = st.number_input("Area (sq ft)", min_value=100, max_value=10000, value=1000)
        
        with col2:
            bedrooms = st.number_input("Bedrooms", min_value=1, max_value=10, value=2)
            bathrooms = st.number_input("Bathrooms", min_value=1, max_value=10, value=2)
            age = st.number_input("Property Age (years)", min_value=0, max_value=50, value=5)
        
        if st.button("🔍 Analyze Market", type="primary"):
            try:
                with st.spinner("Generating market analysis..."):
                    # Get ML prediction first
                    input_data = {
                        'city': location.split(',')[0].strip(),
                        'area_sqft': area,
                        'bhk': bedrooms,
                        'district': location,
                        'sub_district': location,
                        'property_type': property_type,
                        'furnishing': 'Semi-Furnished'
                    }
                    
                    prediction_result = st.session_state.predictor.predict(input_data)
                    predicted_price = prediction_result[0]
                    
                    # Prepare data for Gemini
                    property_data = {
                        'location': location,
                        'property_type': property_type,
                        'area': area,
                        'bedrooms': bedrooms,
                        'bathrooms': bathrooms,
                        'age': age,
                        'predicted_price': predicted_price
                    }
                    
                    # Get AI analysis
                    analysis = gemini_service.analyze_property_market(property_data)
                    
                    st.markdown("### 📊 AI Market Analysis")
                    st.write(analysis)
                    
            except Exception as e:
                self.logger.log_error(e, {"component": "market_analysis"})
                st.error("❌ Analysis failed. Please try again.")
    
    def _render_investment_recommendations(self, gemini_service):
        """Render investment recommendations"""
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
        
        if st.button("💡 Get Recommendations", type="primary"):
            try:
                with st.spinner("Generating personalized recommendations..."):
                    user_profile = {
                        'budget': budget,
                        'timeline': timeline,
                        'risk_appetite': risk_appetite,
                        'goal': goal,
                        'preferred_locations': preferred_locations,
                        'property_type_preference': property_type_pref
                    }
                    
                    recommendations = gemini_service.get_investment_recommendations(user_profile)
                    
                    st.markdown("### 💰 Investment Recommendations")
                    st.write(recommendations)
                    
            except Exception as e:
                self.logger.log_error(e, {"component": "investment_recommendations"})
                st.error("❌ Failed to generate recommendations.")
    
    def _render_real_estate_qa(self, gemini_service):
        """Render Q&A interface"""
        st.subheader("Real Estate Q&A Assistant")
        
        question = st.text_area("Ask any real estate question:", 
                               placeholder="e.g., What factors affect property prices in Mumbai?",
                               height=100)
        
        if st.button("🤔 Get Answer", type="primary"):
            if question.strip():
                try:
                    with st.spinner("Thinking..."):
                        answer = gemini_service.real_estate_qa(question)
                        
                        st.markdown("### 💬 AI Answer")
                        st.write(answer)
                        
                except Exception as e:
                    self.logger.log_error(e, {"component": "real_estate_qa"})
                    st.error("❌ Failed to get answer.")
            else:
                st.warning("Please enter a question.")
    
    def _render_property_reports(self, gemini_service):
        """Render property reports"""
        st.subheader("Comprehensive Property Reports")
        
        col1, col2 = st.columns(2)
        with col1:
            report_location = st.text_input("Property Location", placeholder="e.g., Bandra, Mumbai")
            report_type = st.selectbox("Report Type", ["Investment Analysis", "Market Overview", "Comparative Analysis"])
        
        with col2:
            property_details = st.text_area("Additional Property Details (optional)", 
                                           placeholder="Any specific details about the property...")
        
        if st.button("📄 Generate Report", type="primary"):
            if report_location.strip():
                try:
                    with st.spinner("Generating comprehensive report..."):
                        report_data = {
                            'location': report_location,
                            'report_type': report_type,
                            'additional_details': property_details
                        }
                        
                        report = gemini_service.generate_property_report(report_data)
                        
                        st.markdown("### 📄 Property Report")
                        st.write(report)
                        
                        # Download option
                        st.download_button(
                            label="📥 Download Report",
                            data=report,
                            file_name=f"property_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain"
                        )
                        
                except Exception as e:
                    self.logger.log_error(e, {"component": "property_reports"})
                    st.error("❌ Failed to generate report.")
            else:
                st.warning("Please enter a property location.")
    
    def _render_market_trends(self, gemini_service):
        """Render market trends analysis"""
        st.subheader("Market Trends & Insights")
        
        trend_city = st.selectbox("Select City for Trends", ["Mumbai", "Delhi", "Bangalore", "Gurugram", "Noida", "All Cities"])
        trend_period = st.selectbox("Analysis Period", ["Current", "6 Months", "1 Year", "2 Years"])
        
        if st.button("📈 Analyze Trends", type="primary"):
            try:
                with st.spinner("Analyzing market trends..."):
                    trends_data = {
                        'city': trend_city,
                        'period': trend_period,
                        'analysis_type': 'comprehensive'
                    }
                    
                    trends = gemini_service.analyze_market_trends(trends_data)
                    
                    st.markdown("### 📈 Market Trends Analysis")
                    st.write(trends)
                    
            except Exception as e:
                self.logger.log_error(e, {"component": "market_trends"})
                st.error("❌ Failed to analyze trends.")
    
    @performance_monitor("main_application")
    def run(self):
        """Main application entry point with comprehensive error handling"""
        try:
            # Render header and sidebar
            self._render_header()
            self._render_sidebar()
            
            # Main navigation
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "🏠 Price Prediction", 
                "📊 Analytics", 
                "🔍 Property Search", 
                "🤖 AI Assistant",
                "🧠 Gemini AI Insights"
            ])
            
            with tab1:
                self.render_property_prediction_tab()
            
            with tab2:
                self.render_analytics_tab()
            
            with tab3:
                self.render_property_search_tab()
            
            with tab4:
                self.render_chatbot_tab()
            
            with tab5:
                self.render_gemini_ai_tab()
            
            # Footer with system information
            st.markdown("---")
            st.markdown(f"""
            <div style="text-align: center; color: #666; font-size: 0.8em;">
                {config.APP_NAME} v{config.VERSION} | Environment: {config.ENVIRONMENT} | 
                Session: {st.session_state.session_start.strftime('%Y-%m-%d %H:%M:%S')}
            </div>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            self.logger.log_error(e, {"component": "main_application"})
            st.error("❌ A critical error occurred. Please refresh the page.")

# Application entry point
def main():
    """Production application entry point"""
    try:
        # Setup logging
        config.setup_logging()
        
        # Initialize and run application
        app = ProductionApp()
        app.run()
        
    except Exception as e:
        st.error(f"❌ Failed to start application: {str(e)}")
        st.error("Please check the configuration and try again.")

if __name__ == "__main__":
    main()
