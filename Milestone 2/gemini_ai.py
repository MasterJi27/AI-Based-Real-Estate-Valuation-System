"""
Gemini AI Integration for Real Estate Valuation System
Provides advanced AI capabilities using Google's Gemini 2.5 API
"""

import google.generativeai as genai
import logging
import os
import streamlit as st
from typing import Dict, Any, Optional, List
import json
import time
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

class GeminiAIService:
    """
    Google Gemini AI Service for Real Estate Intelligence
    
    Features:
    - Property market analysis
    - Investment recommendations
    - Market trend predictions
    - Real estate Q&A
    - Property valuation insights
    """
    
    def __init__(self, api_key: str = None):
        """Initialize Gemini AI service with secure API key handling"""
        # Try multiple sources for API key
        self.api_key = (
            api_key or 
            st.secrets.get("GOOGLE_API_KEY") or 
            os.getenv('GOOGLE_API_KEY')
        )
        
        if not self.api_key:
            logger.error("Google API key not provided")
            raise ValueError("Google API key is required for Gemini AI integration")
        
        try:
            # Configure Gemini API
            genai.configure(api_key=self.api_key)
            
            # Initialize model with optimal settings for real estate analysis
            model_name = 'gemini-1.5-flash-latest'  # Use correct model name for API v1beta
            self.model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,  # Conservative for factual information
                    top_p=0.8,
                    top_k=40,
                    max_output_tokens=1024,  # Reduced for flash model
                )
            )
            
            # Initialize conversation history
            self.conversation_history = []
            
            logger.info("Gemini AI service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini AI: {str(e)}")
            raise
    
    def analyze_property_market(self, property_data: Dict[str, Any]) -> str:
        """
        Analyze property market conditions and provide insights
        
        Args:
            property_data: Dictionary containing property information
            
        Returns:
            Detailed market analysis as string
        """
        try:
            prompt = f"""
            As a real estate market analyst, provide a comprehensive analysis of this property:
            
            Property Details:
            - Location: {property_data.get('location', 'N/A')}
            - Property Type: {property_data.get('property_type', 'N/A')}
            - Area: {property_data.get('area', 'N/A')} sq ft
            - Bedrooms: {property_data.get('bedrooms', 'N/A')}
            - Bathrooms: {property_data.get('bathrooms', 'N/A')}
            - Age: {property_data.get('age', 'N/A')} years
            - Predicted Price: ₹{property_data.get('predicted_price', 'N/A'):,}
            
            Please provide:
            1. Market positioning analysis
            2. Investment potential assessment
            3. Price competitiveness evaluation
            4. Future appreciation prospects
            5. Risk factors and considerations
            6. Recommendations for buyers/investors
            
            Keep the analysis practical, data-driven, and specific to the Indian real estate market.
            """
            
            response = self.model.generate_content(prompt)
            
            # Log the interaction
            self._log_interaction("property_market_analysis", property_data, response.text)
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error in property market analysis: {str(e)}")
            return "Unable to generate market analysis at this time. Please try again later."
    
    def get_investment_recommendations(self, user_profile: Dict[str, Any]) -> str:
        """
        Provide personalized investment recommendations
        
        Args:
            user_profile: User investment profile and preferences
            
        Returns:
            Personalized investment recommendations
        """
        try:
            prompt = f"""
            As a real estate investment advisor, provide personalized recommendations for this investor:
            
            Investor Profile:
            - Budget: ₹{user_profile.get('budget', 'N/A'):,}
            - Investment Timeline: {user_profile.get('timeline', 'N/A')}
            - Risk Appetite: {user_profile.get('risk_appetite', 'N/A')}
            - Investment Goal: {user_profile.get('goal', 'N/A')}
            - Preferred Locations: {user_profile.get('preferred_locations', 'N/A')}
            - Property Type Preference: {user_profile.get('property_type', 'N/A')}
            
            Please provide:
            1. Recommended property types and locations
            2. Investment strategy suggestions
            3. Market timing advice
            4. Portfolio diversification tips
            5. Expected returns and timeline
            6. Risk mitigation strategies
            
            Focus on the Indian real estate market and current market conditions.
            """
            
            response = self.model.generate_content(prompt)
            
            # Log the interaction
            self._log_interaction("investment_recommendations", user_profile, response.text)
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating investment recommendations: {str(e)}")
            return "Unable to generate investment recommendations at this time. Please try again later."
    
    def analyze_market_trends(self, city: str, property_type: str = None) -> str:
        """
        Analyze current market trends for a specific city/region
        
        Args:
            city: Target city for analysis
            property_type: Optional property type filter
            
        Returns:
            Market trend analysis
        """
        try:
            prompt = f"""
            As a real estate market researcher, analyze the current market trends for:
            
            Location: {city}
            Property Type: {property_type or 'All property types'}
            
            Please provide insights on:
            1. Current market conditions and sentiment
            2. Price trends and growth patterns
            3. Supply and demand dynamics
            4. Upcoming infrastructure developments
            5. Government policies impact
            6. Future market outlook (6-12 months)
            7. Best areas for investment within the city
            8. Market risks and opportunities
            
            Focus on actionable insights for investors and homebuyers in the Indian market.
            """
            
            response = self.model.generate_content(prompt)
            
            # Log the interaction
            self._log_interaction("market_trends", {"city": city, "property_type": property_type}, response.text)
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error analyzing market trends: {str(e)}")
            return "Unable to analyze market trends at this time. Please try again later."
    
    def real_estate_qa(self, question: str, context: Dict[str, Any] = None) -> str:
        """
        Answer real estate related questions with context awareness
        
        Args:
            question: User's question
            context: Optional context information
            
        Returns:
            AI-generated answer
        """
        try:
            context_info = ""
            if context:
                context_info = f"\nContext: {json.dumps(context, indent=2)}"
            
            prompt = f"""
            As a knowledgeable real estate expert in India, please answer this question:
            
            Question: {question}
            {context_info}
            
            Provide a comprehensive, accurate, and helpful answer. Include:
            - Direct answer to the question
            - Relevant explanations and context
            - Practical advice or recommendations
            - Current market considerations
            - Legal or regulatory aspects if relevant
            
            Keep the response informative yet accessible, focusing on the Indian real estate market.
            """
            
            response = self.model.generate_content(prompt)
            
            # Add to conversation history
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "question": question,
                "answer": response.text,
                "context": context
            })
            
            # Log the interaction
            self._log_interaction("qa_session", {"question": question, "context": context}, response.text)
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error in Q&A session: {str(e)}")
            return "I'm unable to answer your question right now. Please try again later."
    
    def generate_property_report(self, property_data: Dict[str, Any]) -> str:
        """
        Generate a comprehensive property analysis report
        
        Args:
            property_data: Complete property information
            
        Returns:
            Detailed property report
        """
        try:
            prompt = f"""
            Generate a comprehensive property analysis report for:
            
            Property Information:
            {json.dumps(property_data, indent=2)}
            
            Create a detailed report including:
            
            1. EXECUTIVE SUMMARY
            2. PROPERTY OVERVIEW
            3. LOCATION ANALYSIS
            4. PRICE EVALUATION
            5. MARKET COMPARISON
            6. INVESTMENT POTENTIAL
            7. RISK ASSESSMENT
            8. RECOMMENDATIONS
            9. CONCLUSION
            
            Make the report professional, data-driven, and actionable for decision-making.
            Focus on the Indian real estate market context.
            """
            
            response = self.model.generate_content(prompt)
            
            # Log the interaction
            self._log_interaction("property_report", property_data, response.text)
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating property report: {str(e)}")
            return "Unable to generate property report at this time. Please try again later."
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Return conversation history for the session"""
        return self.conversation_history
    
    def clear_conversation_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("Conversation history cleared")
    
    def _log_interaction(self, interaction_type: str, input_data: Any, output_data: str):
        """Log AI interactions for monitoring and improvement"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "interaction_type": interaction_type,
                "input_size": len(str(input_data)),
                "output_size": len(output_data),
                "status": "success"
            }
            logger.info(f"Gemini AI interaction logged: {log_entry}")
        except Exception as e:
            logger.error(f"Failed to log interaction: {str(e)}")

# Streamlit integration functions
@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_cached_market_analysis(city: str, property_type: str = None) -> str:
    """Cached market analysis for better performance"""
    if 'gemini_service' not in st.session_state:
        return "Gemini AI service not initialized"
    
    return st.session_state.gemini_service.analyze_market_trends(city, property_type)

def initialize_gemini_service(api_key: str) -> GeminiAIService:
    """Initialize Gemini service and store in session state"""
    try:
        service = GeminiAIService(api_key)
        st.session_state.gemini_service = service
        logger.info("Gemini AI service initialized and cached in session state")
        return service
    except Exception as e:
        logger.error(f"Failed to initialize Gemini service: {str(e)}")
        st.error(f"Failed to initialize Gemini AI: {str(e)}")
        raise

def get_gemini_service() -> Optional[GeminiAIService]:
    """Get Gemini service from session state"""
    return st.session_state.get('gemini_service')

# Test function for development
def test_gemini_integration():
    """Test Gemini AI integration"""
    try:
        # Test with environment variable API key
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        test_key = os.getenv('GEMINI_API_KEY', '')
        if not test_key:
            print("❌ No API key found in environment variables")
            return False
            
        service = GeminiAIService(test_key)
        
        # Test property analysis
        test_property = {
            "location": "Bangalore",
            "property_type": "Apartment",
            "area": 1200,
            "bedrooms": 3,
            "bathrooms": 2,
            "age": 5,
            "predicted_price": 8500000
        }
        
        analysis = service.analyze_property_market(test_property)
        print("Property Analysis:")
        print(analysis)
        print("\n" + "="*50 + "\n")
        
        # Test Q&A
        question = "What are the key factors affecting property prices in Bangalore?"
        answer = service.real_estate_qa(question)
        print("Q&A Response:")
        print(answer)
        
        return True
        
    except Exception as e:
        print(f"Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    # Run test
    test_gemini_integration()
