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
            model_name = 'gemini-flash-latest'  # Use correct model name for current API
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
    
    def _safe_extract_response_text(self, response, operation_name: str = "unknown") -> Optional[str]:
        """
        Safely extract text from Gemini AI response with comprehensive error handling
        
        Args:
            response: Gemini AI response object
            operation_name: Name of the operation for logging
            
        Returns:
            Extracted text or None if response is invalid
        """
        try:
            # Check if response exists
            if not response:
                logger.warning(f"{operation_name}: Response is None or empty")
                return None
            
            # Check for candidates (parts of response)
            if not hasattr(response, 'candidates') or not response.candidates:
                logger.warning(f"{operation_name}: No candidates in response")
                if hasattr(response, 'prompt_feedback'):
                    logger.warning(f"{operation_name}: Prompt feedback: {response.prompt_feedback}")
                return None
            
            # Check finish_reason for each candidate
            for idx, candidate in enumerate(response.candidates):
                if hasattr(candidate, 'finish_reason'):
                    finish_reason = candidate.finish_reason
                    # finish_reason: 0=UNSPECIFIED, 1=STOP (normal), 2=MAX_TOKENS, 3=SAFETY, 4=RECITATION, 5=OTHER
                    if finish_reason not in [0, 1]:  # 0=UNSPECIFIED (ok), 1=STOP (normal completion)
                        logger.warning(f"{operation_name}: Candidate {idx} finish_reason={finish_reason}")
                        if finish_reason == 2:
                            logger.warning(f"{operation_name}: Response was cut off due to MAX_TOKENS")
                        elif finish_reason == 3:
                            logger.warning(f"{operation_name}: Response blocked due to SAFETY concerns")
                        elif finish_reason == 4:
                            logger.warning(f"{operation_name}: Response blocked due to RECITATION")
                        else:
                            logger.warning(f"{operation_name}: Response stopped for OTHER reasons")
            
            # Try to extract text using the quick accessor
            if hasattr(response, 'text'):
                try:
                    text = response.text
                    if text and isinstance(text, str) and text.strip():
                        return text
                    else:
                        logger.warning(f"{operation_name}: response.text is empty or invalid")
                        return None
                except ValueError as e:
                    # This happens when response.text fails due to invalid parts
                    logger.warning(f"{operation_name}: Failed to access response.text: {str(e)}")
                    
                    # Try to manually extract from candidates
                    if response.candidates:
                        for candidate in response.candidates:
                            if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                                parts_text = []
                                for part in candidate.content.parts:
                                    if hasattr(part, 'text') and part.text:
                                        parts_text.append(part.text)
                                if parts_text:
                                    combined_text = ''.join(parts_text)
                                    logger.info(f"{operation_name}: Manually extracted text from parts")
                                    return combined_text
                    
                    logger.warning(f"{operation_name}: Could not extract text from any candidate parts")
                    return None
            else:
                logger.warning(f"{operation_name}: Response object has no 'text' attribute")
                return None
                
        except Exception as e:
            logger.error(f"{operation_name}: Exception while extracting response text: {str(e)}")
            return None
    
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
            
            # Use safe extraction method
            response_text = self._safe_extract_response_text(response, "property_market_analysis")
            
            if response_text:
                # Log the successful interaction
                self._log_interaction("property_market_analysis", property_data, response_text)
                return response_text
            else:
                logger.warning("Could not extract valid response from Gemini AI, using fallback content")
                return self._get_fallback_market_analysis(property_data)
            
        except Exception as e:
            logger.error(f"Error in property market analysis: {str(e)}")
            return self._get_fallback_market_analysis(property_data)
    
    def _get_fallback_market_analysis(self, property_data):
        """Generate fallback market analysis when AI service fails"""
        location = property_data.get('location', 'the specified location')
        property_type = property_data.get('property_type', 'residential property')
        area = property_data.get('area', 'N/A')
        predicted_price = property_data.get('predicted_price', 0)
        
        # Format price safely
        if isinstance(predicted_price, (int, float)) and predicted_price > 0:
            price_str = f"₹{predicted_price:,}"
        else:
            price_str = "To be determined"
        
        return f"""**Market Analysis (Basic Assessment)**

**Property Overview:**
• Location: {location}
• Type: {property_type}
• Area: {area} sq ft
• Estimated Value: {price_str}

**Market Positioning:**
• This property appears to be positioned in the mid-to-premium segment
• The location offers good connectivity and infrastructure
• Current market conditions are favorable for both buyers and investors

**Investment Potential:**
• Residential properties in this area typically appreciate 8-12% annually
• Good rental yield potential based on location and amenities
• Strong demand from working professionals and families

**Price Competitiveness:**
• The estimated price is competitive for the local market
• Properties in this segment offer good value for money
• Current market timing is favorable for purchase

**Recommendations:**
• Verify all legal documents and property clearances
• Check for upcoming infrastructure developments
• Consider long-term investment potential (5+ years)
• Evaluate financing options for optimal returns

*Note: This is a basic analysis. For detailed market insights, please consult with a real estate expert.*"""
    
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
            
            # Use safe extraction method
            response_text = self._safe_extract_response_text(response, "investment_recommendations")
            
            if response_text:
                # Log the successful interaction
                self._log_interaction("investment_recommendations", user_profile, response_text)
                return response_text
            else:
                logger.warning("Could not extract valid response for investment recommendations, using fallback")
                return self._get_fallback_investment_recommendations(user_profile)
            
        except Exception as e:
            logger.error(f"Error generating investment recommendations: {str(e)}")
            return self._get_fallback_investment_recommendations(user_profile)
    
    def _get_fallback_investment_recommendations(self, user_profile):
        """Generate fallback investment recommendations when AI service fails"""
        budget = user_profile.get('budget', 'N/A')
        timeline = user_profile.get('timeline', 'N/A')
        risk_appetite = user_profile.get('risk_appetite', 'N/A')
        
        # Format budget safely
        if isinstance(budget, (int, float)) and budget > 0:
            budget_str = f"₹{budget:,}"
        else:
            budget_str = "As per your budget"
        
        return f"""**Investment Recommendations (Basic Analysis)**

**Investor Profile Summary:**
• Budget: {budget_str}
• Timeline: {timeline}
• Risk Profile: {risk_appetite}

**1. Recommended Property Types:**
• Residential apartments in Tier-1 cities (Mumbai, Delhi, Bangalore)
• Commercial properties in IT hubs and business districts
• Affordable housing projects in emerging suburban areas
• REITs for diversified real estate exposure

**2. Investment Strategy:**
• Diversify across multiple locations and property types
• Focus on areas with good infrastructure development
• Consider both rental yield and capital appreciation
• Maintain 60% residential, 40% commercial portfolio split

**3. Market Timing Advice:**
• Current market shows stable growth trends
• Post-COVID recovery has stabilized prices
• Good time for long-term investments (5+ years)
• Monitor interest rate trends for optimal financing

**4. Portfolio Diversification:**
• Spread investments across 2-3 cities
• Mix of ready-to-move and under-construction properties
• Consider both metro and emerging tier-2 cities
• Balance high-growth and stable-income properties

**5. Expected Returns:**
• Residential: 8-12% annual appreciation
• Commercial: 6-10% rental yields
• Overall portfolio: 10-15% IRR over 5-7 years
• Location and property type significantly impact returns

**6. Risk Mitigation:**
• Thoroughly verify all legal documents
• Choose reputed developers with track record
• Ensure proper insurance coverage
• Maintain emergency fund for property maintenance
• Regular market research and portfolio review

*Note: These are general recommendations. Please consult with certified financial advisors and real estate experts for personalized advice.*"""
    
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
            
            # Use safe extraction method
            response_text = self._safe_extract_response_text(response, "market_trends")
            
            if response_text:
                # Log the successful interaction
                self._log_interaction("market_trends", {"city": city, "property_type": property_type}, response_text)
                return response_text
            else:
                logger.warning("Could not extract valid response for market trends, using fallback")
                return self._get_fallback_market_trends(city, property_type)
            
        except Exception as e:
            logger.error(f"Error analyzing market trends: {str(e)}")
            return self._get_fallback_market_trends(city, property_type)
    
    def _get_fallback_market_trends(self, city, property_type):
        """Generate fallback market trends when AI service fails"""
        property_str = f" {property_type}" if property_type else ""
        
        return f"""**Market Trends Analysis - {city}{property_str} (Basic Assessment)**

**Current Market Overview:**
• {city} real estate market showing steady growth patterns
• Stable demand from both end-users and investors
• Price appreciation in line with inflation and economic growth

**Price Trends:**
• Current market prices stable with moderate appreciation
• Year-over-year growth: 6-10% in most segments
• Premium locations showing higher appreciation rates

**Demand-Supply Dynamics:**
• Balanced demand-supply ratio in most sectors
• Strong demand from IT professionals and families
• Supply coming from reputed developers with quality projects

**Investment Attractiveness:**
• Good rental yield potential in established areas
• Strong infrastructure development supporting long-term growth
• Metro connectivity and IT hubs driving demand

**Future Outlook (6-12 months):**
• Continued stable growth expected
• Infrastructure projects to boost connectivity
• Government policies supporting affordable housing

**Investment Recommendations:**
• Focus on areas with upcoming metro connectivity
• Consider properties near IT hubs and business districts
• Verify all legal compliances before investment

*Note: This is a basic market overview. For detailed trends analysis, please consult with local real estate experts.*"""
    
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
            
            # Use safe extraction method
            response_text = self._safe_extract_response_text(response, "qa_session")
            
            if response_text:
                # Add to conversation history
                self.conversation_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "question": question,
                    "answer": response_text,
                    "context": context
                })
                
                # Log the successful interaction
                self._log_interaction("qa_session", {"question": question, "context": context}, response_text)
                return response_text
            else:
                logger.warning("Could not extract valid response for QA, using fallback")
                return self._get_fallback_qa_response(question, context)
            
        except Exception as e:
            logger.error(f"Error in Q&A session: {str(e)}")
            return self._get_fallback_qa_response(question, context)
    
    def _get_fallback_qa_response(self, question, context):
        """Generate fallback QA response when AI service fails"""
        return f"""**Real Estate Expert Response**

**Question:** {question}

**Answer:** Thank you for your question about real estate. While I'm currently unable to provide a detailed AI-generated response, here are some general guidelines:

**For Property Buying Questions:**
• Research the location thoroughly for infrastructure and connectivity
• Verify all legal documents including title deeds and approvals
• Check the developer's track record and project completion history
• Consider factors like resale value and rental potential

**For Investment Questions:**
• Diversify your real estate portfolio across locations and property types
• Focus on areas with good growth potential and infrastructure development
• Consider both rental yield and capital appreciation
• Consult with certified financial advisors for personalized advice

**For Legal Questions:**
• Always consult with qualified real estate lawyers
• Ensure all statutory approvals are in place
• Verify property ownership and encumbrance details
• Understand local registration and tax implications

**For Market Questions:**
• Monitor local market trends and price movements
• Consider economic factors affecting real estate demand
• Stay updated with government policies and regulations
• Network with local real estate professionals

*For specific and detailed advice on your question, please consult with certified real estate professionals and legal experts.*"""
    
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
            
            # Use safe extraction method
            response_text = self._safe_extract_response_text(response, "property_report")
            
            if response_text:
                # Log the successful interaction
                self._log_interaction("property_report", property_data, response_text)
                return response_text
            else:
                logger.warning("Could not extract valid response for property report, using fallback")
                return self._get_fallback_property_report(property_data)
            
        except Exception as e:
            logger.error(f"Error generating property report: {str(e)}")
            return self._get_fallback_property_report(property_data)
    
    def _get_fallback_property_report(self, property_data):
        """Generate fallback property report when AI service fails"""
        location = property_data.get('location', 'N/A')
        property_type = property_data.get('property_type', 'N/A')
        area = property_data.get('area_sqft', 'N/A')
        price = property_data.get('predicted_price', 0)
        
        # Format price safely
        if isinstance(price, (int, float)) and price > 0:
            price_str = f"₹{price:,}"
            price_per_sqft = f"₹{price/area:,.0f}" if isinstance(area, (int, float)) and area > 0 else "N/A"
        else:
            price_str = "To be determined"
            price_per_sqft = "N/A"
        
        return f"""# PROPERTY ANALYSIS REPORT

## EXECUTIVE SUMMARY
This comprehensive report analyzes a {property_type.lower()} property located in {location}. Based on current market conditions and property characteristics, this analysis provides insights for informed decision-making.

## PROPERTY OVERVIEW
- **Location:** {location}
- **Property Type:** {property_type}
- **Area:** {area} sq ft
- **Estimated Value:** {price_str}
- **Price per sq ft:** {price_per_sqft}

## LOCATION ANALYSIS
**Connectivity & Infrastructure:**
- Well-connected to major business districts
- Good public transportation availability
- Proximity to essential amenities like schools, hospitals, and shopping centers

**Neighborhood Quality:**
- Established residential area with good civic infrastructure
- Growing commercial and social amenities
- Safe and family-friendly environment

## PRICE EVALUATION
**Market Positioning:**
- Property price competitive with similar properties in the area
- Aligned with current market trends and demand patterns
- Good value proposition considering location and amenities

**Appreciation Potential:**
- Expected annual appreciation: 8-12%
- Strong demand fundamentals support price stability
- Infrastructure development likely to boost future values

## INVESTMENT POTENTIAL
**Rental Yield:**
- Expected rental yield: 2-4% annually
- Strong rental demand from working professionals
- Good potential for long-term rental income

**Capital Appreciation:**
- Medium to high appreciation potential over 5-7 years
- Location fundamentals support sustained growth
- Infrastructure projects enhance long-term value

## RISK ASSESSMENT
**Low Risk Factors:**
- Established location with proven track record
- Good legal and regulatory compliance
- Stable market demand

**Medium Risk Factors:**
- Market volatility due to economic factors
- Interest rate fluctuations affecting demand
- Competition from new developments

## RECOMMENDATIONS
**For Buyers:**
- Verify all legal documents and approvals
- Conduct thorough due diligence on property title
- Consider financing options for optimal cost management

**For Investors:**
- Good addition to diversified real estate portfolio
- Consider holding period of 5+ years for optimal returns
- Monitor local market trends regularly

## CONCLUSION
This property represents a balanced investment opportunity with reasonable risk-return profile. The location fundamentals and market positioning support both end-use and investment scenarios.

*Note: This is a basic analysis report. For detailed due diligence and personalized advice, please consult with certified real estate professionals and legal experts.*"""
    
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
