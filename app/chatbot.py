import streamlit as st
import re
import random
import math
from datetime import datetime
from typing import Dict, List, Tuple

# Simple regex functions to replace secure_regex
def extract_safe_bhk(text):
    """Extract BHK information from text"""
    match = re.search(r'(\d+)\s*(?:bhk|bedroom)', text.lower())
    return int(match.group(1)) if match else None

def extract_safe_area(text):
    """Extract area information from text"""
    match = re.search(r'(\d+)\s*(?:sq\s*ft|sqft|square\s*feet)', text.lower())
    return int(match.group(1)) if match else None

def extract_safe_budget(text):
    """Extract budget information from text"""
    # Look for numbers with crore, lakh, etc.
    patterns = [
        r'(\d+(?:\.\d+)?)\s*crore',
        r'(\d+(?:\.\d+)?)\s*lakh',
        r'(\d+(?:\.\d+)?)\s*lac'
    ]
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            amount = float(match.group(1))
            if 'crore' in pattern:
                return amount * 10000000
            elif 'lakh' in pattern or 'lac' in pattern:
                return amount * 100000
    return None

def extract_safe_city(text):
    """Extract city information from text using whole-word matching"""
    cities = ['mumbai', 'delhi', 'bangalore', 'gurugram', 'noida', 'pune', 'chennai']
    for city in cities:
        if re.search(rf'\b{re.escape(city)}\b', text, re.IGNORECASE):
            return city.title()
    return None

class RealEstateChatbot:
    def __init__(self, data_loader=None, predictor=None, combined_data=None):
        self.data_loader = data_loader
        self.predictor = predictor
        self.combined_data = combined_data
        
        # Initialize conversation context
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'chat_context' not in st.session_state:
            st.session_state.chat_context = {}
            
        # Knowledge base
        self.responses = {
            'greeting': [
                "Hello! 👋 I'm your AI Real Estate Assistant. How can I help you with property queries today?",
                "Hi there! 🏠 I'm here to help you with property prices, market insights, and investment advice. What would you like to know?",
                "Welcome! 🌟 I can assist you with property valuations, market trends, and investment guidance. What's on your mind?"
            ],
            'price_query': [
                "I can help you get property price predictions! You can use the Price Prediction tab or tell me the property details.",
                "For accurate price estimates, I'll need details like city, area, BHK, and property type. Shall we start?",
                "Property pricing depends on location, size, and amenities. Let me help you get a precise estimate!"
            ],
            'investment_advice': [
                "Great question! Investment potential depends on location, price trends, and growth prospects.",
                "I can analyze investment opportunities based on market data and price projections.",
                "Let me help you evaluate the investment potential of different properties!"
            ],
            'market_trends': [
                "Market trends vary by city and locality. I can provide insights based on our data.",
                "Current market analysis shows interesting patterns across Indian metro cities.",
                "I can share market statistics and growth trends for different areas!"
            ],
            'features': [
                "I can help with: 🔮 Price Prediction, 📊 Property Valuation, 💼 Investment Analysis, and 📈 Market Insights!",
                "My features include property price estimation, investment advice, EMI calculation, and market trend analysis.",
                "I offer comprehensive real estate assistance including pricing, valuation, and investment guidance!"
            ],
            'emi': [
                "I can help calculate EMI for property loans! I'll need loan amount, interest rate, and tenure.",
                "EMI calculation helps plan your property investment. Shall we calculate yours?",
                "Property loan EMI depends on principal, rate, and tenure. Let me help you calculate!"
            ],
            'goodbye': [
                "Thank you for using our AI Real Estate Assistant! 🏠 Feel free to ask anytime!",
                "Goodbye! Hope I helped with your property queries. Have a great day! 👋",
                "Thanks for chatting! Remember, I'm here whenever you need real estate assistance! 🌟"
            ],
            'default': [
                "I'm specialized in real estate queries. Could you ask about property prices, market trends, or investment advice?",
                "I can help with property-related questions. Try asking about prices, locations, or investment opportunities!",
                "Let me assist you with real estate matters! Ask about property valuation, market insights, or investment advice."
            ]
        }
        
        # Intent patterns
        self.intent_patterns = {
            'greeting': [r'\b(hi|hello|hey|good morning|good afternoon|good evening)\b', r'^\s*(hi|hello)\s*$'],
            'goodbye': [r'\b(bye|goodbye|see you|thanks|thank you)\b', r'(exit|quit|end)'],
            'price_query': [r'\b(price|cost|value|worth|estimate|prediction)\b', r'\b(how much|what.*cost|price of)\b'],
            'investment_advice': [r'\b(invest|investment|buy|purchase|should i buy)\b', r'\b(good investment|worth buying)\b'],
            'market_trends': [r'\b(market|trend|growth|appreciation|demand)\b', r'\b(market condition|property market)\b'],
            'emi': [r'\b(emi|loan|mortgage|installment)\b', r'\b(monthly payment|loan calculation)\b'],
            'features': [r'\b(what can you do|features|help|capabilities)\b', r'\b(how can you help|what do you offer)\b'],
            'location': [r'\b(mumbai|delhi|bangalore|gurugram|noida|location|area|district)\b'],
            'bhk': [r'\b(\d+\s*bhk|bedroom|room)\b'],
            'property_type': [r'\b(apartment|villa|house|studio|penthouse|flat)\b'],
            'recommend': [r'\b(recommend|suggest|find|show me|best)\b', r'\b(which property|what should|advice)\b'],
            'budget': [r'\b(budget|afford|range|between|under)\b', r'\b(\d+\s*(lakh|crore|million))\b']
        }

    def classify_intent(self, user_input: str) -> str:
        """Classify user intent based on input patterns with priority ordering"""
        user_input = user_input.lower().strip()
        
        # Limit input length for security
        if len(user_input) > 500:
            user_input = user_input[:500]
        
        # Specific intents are checked before generic ones to prevent shadowing
        priority_order = [
            'price_query', 'emi', 'recommend', 'budget', 'investment_advice',
            'market_trends', 'location', 'bhk', 'property_type', 'features',
            'greeting', 'goodbye'
        ]
        
        for intent in priority_order:
            patterns = self.intent_patterns.get(intent, [])
            for pattern in patterns:
                if re.search(pattern, user_input, re.IGNORECASE):
                    return intent
        
        for intent, patterns in self.intent_patterns.items():
            if intent in priority_order:
                continue
            for pattern in patterns:
                if re.search(pattern, user_input, re.IGNORECASE):
                    return intent
        
        return 'default'

    def get_market_insights(self, city: str = None) -> str:
        """Get market insights for a city"""
        if self.combined_data is None or self.combined_data.empty:
            return "Market data is currently being loaded. Please try again in a moment."
        
        try:
            if city:
                city_data = self.combined_data[self.combined_data['city'].str.lower() == city.lower()]
                if not city_data.empty:
                    avg_price = city_data['price'].mean()
                    valid_area = city_data['area_sqft'].replace(0, float('nan'))
                    avg_price_per_sqft = (city_data['price'] / valid_area).mean(skipna=True)
                    total_properties = len(city_data)
                    avg_ppsf_display = (
                        "N/A" if math.isnan(avg_price_per_sqft)
                        else f"₹{avg_price_per_sqft:,.0f}"
                    )
                    return f"""📊 **{city.title()} Market Insights:**
- Average Property Price: ₹{avg_price:,.0f}
- Average Price per Sqft: {avg_ppsf_display}
- Properties in Database: {total_properties}
- Popular Property Types: {', '.join(city_data['property_type'].value_counts().head(3).index.tolist())}"""
                else:
                    return f"Sorry, I don't have market data for {city.title()} at the moment."
            else:
                # Overall market insights
                all_cities = self.combined_data['city'].unique()
                insights = "🏠 **Overall Market Overview:**\n"
                for city_name in all_cities:
                    city_data = self.combined_data[self.combined_data['city'].str.lower() == city_name.lower()]
                    avg_price = city_data['price'].mean()
                    insights += f"- {city_name}: ₹{avg_price:,.0f} (avg)\n"
                return insights
        except Exception as e:
            return "I'm having trouble accessing market data right now. Please try again later."

    def calculate_quick_emi(self, principal: float, rate: float, tenure: int) -> str:
        """Calculate EMI quickly"""
        if not (isinstance(principal, (int, float)) and principal > 0):
            return "Please provide positive numbers for principal and tenure."
        if not (isinstance(tenure, (int, float)) and tenure > 0):
            return "Please provide positive numbers for principal and tenure."
        if not (isinstance(rate, (int, float)) and rate >= 0):
            return "Please provide a non-negative interest rate."
        try:
            monthly_rate = rate / (12 * 100)
            months = int(round(tenure * 12))
            
            if monthly_rate == 0:
                emi = principal / months
            else:
                emi = principal * monthly_rate * (1 + monthly_rate)**months / ((1 + monthly_rate)**months - 1)
            
            total_amount = emi * months
            total_interest = total_amount - principal
            
            return f"""💰 **EMI Calculation:**
- Monthly EMI: ₹{emi:,.0f}
- Total Amount: ₹{total_amount:,.0f}
- Total Interest: ₹{total_interest:,.0f}
- Loan Amount: ₹{principal:,.0f}
- Interest Rate: {rate}% per annum
- Tenure: {tenure} years"""
        except (ValueError, TypeError, ZeroDivisionError) as e:
            return "Please provide valid numbers for EMI calculation."

    def generate_response(self, user_input: str) -> str:
        """Generate chatbot response based on user input"""
        # Validate and bound input length before any downstream processing
        user_input = user_input.strip()[:500]

        intent = self.classify_intent(user_input)
        
        # Store context — use already-bounded user_input
        st.session_state.chat_context['last_intent'] = intent
        st.session_state.chat_context['last_input'] = user_input
        
        if intent == 'greeting':
            return random.choice(self.responses['greeting'])
        
        elif intent == 'goodbye':
            return random.choice(self.responses['goodbye'])
        
        elif intent == 'price_query':
            details = self.extract_property_details(user_input)
            if details:
                if len(details) >= 3:  # Enough details for prediction
                    return f"I found these details: {details}. You can get an accurate price prediction using the 'Price Prediction' tab above!"
                else:
                    return f"I see you're asking about property prices. I found: {details}. For accurate pricing, please use the Price Prediction tab or provide more details like city, BHK, and area."
            return random.choice(self.responses['price_query'])
        
        elif intent == 'investment_advice':
            return random.choice(self.responses['investment_advice']) + " Check out the 'Investment Analysis' tab for detailed insights!"
        
        elif intent == 'market_trends':
            details = self.extract_property_details(user_input)
            city = details.get('city')
            insights = self.get_market_insights(city)
            return insights
        
        elif intent == 'emi':
            # Try to extract budget using the helper first (handles lakh/crore units)
            budget = extract_safe_budget(user_input)
            numbers = re.findall(r'\d+(?:\.\d+)?', user_input)
            if budget is not None and len(numbers) >= 3:
                try:
                    # budget already contains the principal (with lakh/crore scaling).
                    # With at least 3 numeric tokens the last two are rate and tenure.
                    remaining = [float(n) for n in numbers]
                    return self.calculate_quick_emi(budget, remaining[-2], remaining[-1])
                except (ValueError, IndexError, TypeError):
                    pass
            if len(numbers) >= 3:
                try:
                    # Require an explicit unit keyword so we know the intended scale.
                    unit_pattern = r'\b(lakh|lac|crore|\u20b9|rs\.?|rupees?)\b'
                    if re.search(unit_pattern, user_input, re.IGNORECASE):
                        principal = float(numbers[0]) * (100000 if float(numbers[0]) < 1000 else 1)
                        rate = float(numbers[1])
                        tenure = float(numbers[2])
                        return self.calculate_quick_emi(principal, rate, tenure)
                    else:
                        return (
                            "Please re-enter the loan amount with an explicit unit "
                            "(e.g., '50 lakh', '1.2 crore', or '₹5000000') so I can "
                            "determine the correct scale."
                        )
                except (ValueError, IndexError, TypeError):
                    pass
            return random.choice(self.responses['emi']) + " Please provide: loan amount, interest rate, and tenure in years."
        
        elif intent == 'features':
            return random.choice(self.responses['features'])
        
        elif intent == 'location':
            details = self.extract_property_details(user_input)
            city = details.get('city')
            if city:
                insights = self.get_market_insights(city)
                # Add property suggestions
                if self.combined_data is not None:
                    city_data = self.combined_data[self.combined_data['city'].str.lower() == city.lower()]
                    if not city_data.empty:
                        popular_areas = city_data['district'].value_counts().head(3)
                        insights += f"\n\n🏘️ **Popular Areas in {city.title()}:**\n"
                        for area, count in popular_areas.items():
                            avg_price = city_data[city_data['district'] == area]['price'].mean()
                            insights += f"- {area}: ₹{avg_price:,.0f} avg ({count} properties)\n"
                return insights
            return "I can provide information about Mumbai, Delhi, Bangalore, Gurugram, and Noida. Which city interests you?"
        
        elif intent in ('recommend', 'budget', 'bhk', 'property_type'):
            details = self.extract_property_details(user_input)
            return self.get_property_recommendations(details)
        
        else:
            return random.choice(self.responses['default'])

    def get_property_recommendations(self, criteria: Dict) -> str:
        """Get property recommendations based on criteria"""
        if self.combined_data is None or self.combined_data.empty:
            return "Property data is loading. Please try again in a moment."
        
        try:
            filtered_data = self.combined_data.copy()
            recommendations = "🏠 **Property Recommendations:**\n\n"
            
            # Filter by budget
            if 'budget' in criteria:
                budget = criteria['budget']
                filtered_data = filtered_data[
                    (filtered_data['price'] <= budget * 1.1) & 
                    (filtered_data['price'] >= budget * 0.8)
                ]
                recommendations += f"📊 **Budget Range:** ₹{budget*0.8:,.0f} - ₹{budget*1.1:,.0f}\n\n"
            
            # Filter by city
            if 'city' in criteria:
                filtered_data = filtered_data[filtered_data['city'].str.lower() == criteria['city'].lower()]
            
            # Filter by BHK
            if 'bhk' in criteria:
                filtered_data = filtered_data[filtered_data['bhk'] == criteria['bhk']]
            
            if filtered_data.empty:
                return "Sorry, I couldn't find properties matching your criteria. Try adjusting your requirements!"
            
            # Get top recommendations
            top_properties = filtered_data.nlargest(3, 'price')
            
            # Use vectorized operations instead of iterrows for better performance
            for idx, prop in enumerate(top_properties.to_dict('records'), 1):
                recommendations += f"**Option {idx}:**\n"
                recommendations += f"• 📍 Location: {prop['city']}, {prop['district']}\n"
                recommendations += f"• 🏠 Type: {prop['bhk']} BHK {prop['property_type']}\n"
                area_sqft_display = prop.get('area_sqft')
                recommendations += (
                    f"• 📐 Area: {area_sqft_display:,.0f} sqft\n"
                    if area_sqft_display else "• 📐 Area: N/A\n"
                )
                recommendations += f"• 💰 Price: ₹{prop['price']:,.0f}\n"
                area_sqft = prop.get('area_sqft')
                if area_sqft:
                    recommendations += f"• 💵 Price/sqft: ₹{prop['price']/area_sqft:,.0f}\n\n"
                else:
                    recommendations += "• 💵 Price/sqft: N/A\n\n"
            
            return recommendations
            
        except Exception as e:
            return "I'm having trouble processing your request. Please try again or be more specific!"

    def extract_property_details(self, text: str) -> Dict:
        """Extract property details from user input using secure regex"""
        details = {}
        
        # Use secure extraction methods
        bhk = extract_safe_bhk(text)
        if bhk:
            details['bhk'] = bhk
            
        area = extract_safe_area(text)
        if area:
            details['area'] = area
            
        budget = extract_safe_budget(text)
        if budget:
            details['budget'] = budget
            
        city = extract_safe_city(text)
        if city:
            details['city'] = city
        
        return details

    def render_chat_interface(self):
        """Render the chat interface"""
        st.markdown("### 🤖 AI Real Estate Assistant")
        st.markdown("Ask me about property prices, market trends, investment advice, or EMI calculations!")
        
        # Chat history container
        chat_container = st.container()
        
        # Display chat history
        with chat_container:
            for i, (role, message, timestamp) in enumerate(st.session_state.chat_history):
                if role == "user":
                    with st.chat_message("user"):
                        st.markdown(message)
                        st.caption(timestamp)
                else:
                    with st.chat_message("assistant"):
                        st.markdown(message)
                        st.caption(timestamp)
        
        # Chat input
        user_input = st.chat_input("Type your question here...")
        
        if user_input:
            # Add user message to history
            timestamp = datetime.now().strftime("%H:%M")
            st.session_state.chat_history.append(("user", user_input, timestamp))
            
            # Generate and add bot response
            bot_response = self.generate_response(user_input)
            st.session_state.chat_history.append(("assistant", bot_response, timestamp))
            
            # Rerun to update the chat
            st.rerun()
        
        # Quick action buttons
        st.markdown("#### Quick Actions:")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("💰 EMI Calculator"):
                st.session_state.chat_history.append(("user", "Calculate EMI", datetime.now().strftime("%H:%M")))
                response = "I can help calculate your EMI! Please provide:\n1. Loan amount (₹)\n2. Interest rate (% per annum)\n3. Tenure (years)\n\nExample: 'Calculate EMI for 50 lakh loan at 8.5% for 20 years'"
                st.session_state.chat_history.append(("assistant", response, datetime.now().strftime("%H:%M")))
                st.rerun()
        
        with col2:
            if st.button("📈 Market Trends"):
                st.session_state.chat_history.append(("user", "Show market trends", datetime.now().strftime("%H:%M")))
                response = self.get_market_insights()
                st.session_state.chat_history.append(("assistant", response, datetime.now().strftime("%H:%M")))
                st.rerun()
        
        with col3:
            if st.button("🏠 Price Estimate"):
                st.session_state.chat_history.append(("user", "Get price estimate", datetime.now().strftime("%H:%M")))
                response = "I can help estimate property prices! Please tell me:\n- City (Mumbai, Delhi, Bangalore, Gurugram, Noida)\n- Number of BHK\n- Area in sqft\n- Property type\n\nOr use the 'Price Prediction' tab above for detailed analysis!"
                st.session_state.chat_history.append(("assistant", response, datetime.now().strftime("%H:%M")))
                st.rerun()
        
        with col4:
            if st.button("🔄 Clear Chat"):
                st.session_state.chat_history = []
                st.rerun()
        
        # Sample questions
        with st.expander("💡 Sample Questions"):
            st.markdown("""
            - "What's the average property price in Mumbai?"
            - "Calculate EMI for 75 lakh loan at 9% for 15 years"
            - "Should I invest in Bangalore real estate?"
            - "What are the market trends in Delhi?"
            - "Price of 3 BHK apartment in Gurugram"
            - "What features do you offer?"
            """)
