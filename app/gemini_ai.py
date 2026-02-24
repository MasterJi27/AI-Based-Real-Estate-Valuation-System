"""
AI Integration for Real Estate Valuation System
Uses OpenRouter API with meta-llama/llama-3.3-70b-instruct
"""

from openai import OpenAI
import logging
import os
import streamlit as st
from typing import Dict, Any, Optional, List
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

logger = logging.getLogger(__name__)

class GeminiAIService:
    def __init__(self, api_key: str = None):
        self.api_key = (
            api_key or
            os.getenv("OPENROUTER_API_KEY") or
            (st.secrets.get("OPENROUTER_API_KEY") if hasattr(st, "secrets") else None)
        )
        self.model = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct:free")
        if not self.api_key:
            raise ValueError("OpenRouter API key is required")
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://ai-real-estate-valuation.streamlit.app",
                "X-Title": "AI Real Estate Valuation System"
            }
        )
        self.conversation_history = []
        logger.info(f"OpenRouter AI initialized with model: {self.model}")

    def _call_ai(self, prompt: str, operation: str = "general") -> Optional[str]:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert real estate analyst specializing in the Indian real estate market. Provide accurate, practical, and data-driven insights."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1024,
                timeout=30,
            )
            text = response.choices[0].message.content
            if text and text.strip():
                logger.info(f"{operation}: {len(text)} chars received")
                return text.strip()
            return None
        except Exception as e:
            logger.error(f"{operation}: API error: {str(e)}", exc_info=False)
            return None

    def analyze_property_market(self, property_data: Dict[str, Any]) -> str:
        price = property_data.get("predicted_price", "N/A")
        price_str = f"{price:,}" if isinstance(price, (int, float)) else str(price)
        prompt = f"""As a real estate market analyst, analyze this property:
Location: {property_data.get("location", "N/A")}, Type: {property_data.get("property_type", "N/A")}, Area: {property_data.get("area", "N/A")} sqft, Bedrooms: {property_data.get("bedrooms", "N/A")}, Predicted Price: Rs{price_str}
Provide: 1) Market positioning 2) Investment potential 3) Price competitiveness 4) Appreciation prospects 5) Risk factors 6) Recommendations. Focus on Indian market."""
        result = self._call_ai(prompt, "market_analysis")
        if result:
            self._log_interaction("market_analysis", property_data, result)
            return result
        return self._fallback_market_analysis(property_data)

    def _fallback_market_analysis(self, d):
        p = d.get("predicted_price", 0)
        return f"""**Market Analysis**\n\n- Location: {d.get("location","N/A")}\n- Type: {d.get("property_type","N/A")}\n- Area: {d.get("area","N/A")} sqft\n- Value: Rs{p:,}\n\n**Investment Potential:** 8-12% annual appreciation expected.\n**Recommendation:** Verify legal documents, check infrastructure plans, hold 5+ years."""

    def get_investment_recommendations(self, user_profile: Dict[str, Any]) -> str:
        b = user_profile.get("budget", "N/A")
        budget_str = f"Rs{b:,}" if isinstance(b, (int, float)) else str(b)
        prompt = f"""As a real estate investment advisor, recommend investments for:
Budget: {budget_str}, Timeline: {user_profile.get("timeline","N/A")}, Risk: {user_profile.get("risk_appetite","N/A")}, Goal: {user_profile.get("goal","N/A")}, Locations: {user_profile.get("preferred_locations","N/A")}, Type: {user_profile.get("property_type","N/A")}
Provide: 1) Recommended types/locations 2) Strategy 3) Market timing 4) Diversification 5) Expected returns 6) Risk mitigation. Indian market focus."""
        result = self._call_ai(prompt, "investment_recs")
        if result:
            self._log_interaction("investment_recs", user_profile, result)
            return result
        return self._fallback_investment(user_profile)

    def _fallback_investment(self, p):
        b = p.get("budget", 0)
        return f"""**Investment Recommendations**\n\nBudget: {'Rs{:,}'.format(b) if isinstance(b,(int,float)) else b}\nTimeline: {p.get("timeline","N/A")}\nRisk: {p.get("risk_appetite","N/A")}\n\n1. Residential apartments in Tier-1 cities\n2. 8-12% annual appreciation expected\n3. Diversify across 2-3 cities\n4. Verify all legal documents\n\n*Consult certified financial advisors for personalized advice.*"""

    def analyze_market_trends(self, city: str, property_type: str = None) -> str:
        prompt = f"""Analyze real estate market trends for {city}, {property_type or "all property types"}.
Provide: 1) Market conditions 2) Price trends 3) Supply/demand 4) Infrastructure 5) Government policies 6) 6-12 month outlook 7) Best investment areas 8) Risks. Indian market focus."""
        result = self._call_ai(prompt, "market_trends")
        if result:
            self._log_interaction("market_trends", {"city": city}, result)
            return result
        return f"""**Market Trends - {city}**\n\n- Steady growth patterns with 6-10% YoY appreciation\n- Strong demand from IT professionals and families\n- Infrastructure development supporting long-term growth\n- Good rental yield potential in established areas"""

    def real_estate_qa(self, question: str, context: Dict[str, Any] = None) -> str:
        try:
            ctx_str = json.dumps(context, default=str) if context else ""
        except (TypeError, ValueError):
            ctx_str = str(context) if context else ""
        ctx = f"\nContext: {ctx_str}" if ctx_str else ""
        prompt = f"""As a real estate expert in India, answer:\n\nQ: {question}{ctx}\n\nProvide a direct, comprehensive answer with practical advice and current market considerations."""
        result = self._call_ai(prompt, "qa")
        if result:
            history = list(self.conversation_history)  # copy before appending
            history.append({"timestamp": datetime.now().isoformat(), "question": question, "answer": result})
            # Bound history to last 50 entries
            self.conversation_history = history[-50:]
            self._log_interaction("qa", {"question": question}, result)
            return result
        return f"""**Answer to:** {question}\n\nFor property buying: verify legal documents, check developer track record, assess location connectivity.\nFor investment: diversify portfolio, focus on infrastructure growth areas, hold 5+ years.\n\n*Consult certified real estate professionals for specific advice.*"""

    def generate_property_report(self, property_data: Dict[str, Any]) -> str:
        prompt = f"""Generate a professional property analysis report for:\n{json.dumps(property_data, indent=2)}\n\nInclude: 1) Executive Summary 2) Property Overview 3) Location Analysis 4) Price Evaluation 5) Investment Potential 6) Risk Assessment 7) Recommendations. Indian market context."""
        result = self._call_ai(prompt, "property_report")
        if result:
            self._log_interaction("property_report", property_data, result)
            return result
        p = property_data.get("predicted_price", 0)
        return f"""# PROPERTY REPORT\n\n**Location:** {property_data.get("location","N/A")}\n**Type:** {property_data.get("property_type","N/A")}\n**Area:** {property_data.get("area_sqft","N/A")} sqft\n**Value:** {'Rs{:,}'.format(p) if isinstance(p,(int,float)) else p}\n\n**Investment Potential:** 8-12% annual appreciation, 2-4% rental yield.\n**Recommendation:** Verify legal documents, hold 5+ years for optimal returns."""

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        return self.conversation_history

    def clear_conversation_history(self):
        self.conversation_history = []

    def _log_interaction(self, itype: str, inp: Any, out: str):
        # Log only the type and output length; never log raw input PII
        logger.info(f"AI interaction: {itype}, output={len(out)} chars")


def get_cached_market_analysis(city: str, property_type: str = None) -> str:
    """Get cached market analysis by calling get_gemini_service() internally to acquire the service instance."""
    service = get_gemini_service()
    if service is None:
        return "AI service not initialized"
    return service.analyze_market_trends(city, property_type)

def initialize_gemini_service(api_key: str = None) -> GeminiAIService:
    try:
        service = GeminiAIService(api_key)
        st.session_state.gemini_service = service
        return service
    except Exception as e:
        logger.error(f"Failed to initialize AI service: {str(e)}")
        raise

def get_gemini_service() -> Optional[GeminiAIService]:
    return st.session_state.get("gemini_service")