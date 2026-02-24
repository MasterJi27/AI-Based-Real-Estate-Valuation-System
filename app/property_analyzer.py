import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

# Setup logging
logger = logging.getLogger(__name__)

class PropertyAnalyzer:
    def __init__(self):
        # Historical appreciation rates by city (annual %)
        self.city_appreciation_rates = {
            'Mumbai': {'historical': 8.2, 'current': 7.8, 'projected': 7.5},
            'Delhi': {'historical': 9.1, 'current': 8.5, 'projected': 8.0},
            'Bangalore': {'historical': 10.3, 'current': 9.8, 'projected': 9.2},
            'Gurugram': {'historical': 9.7, 'current': 8.9, 'projected': 8.5},
            'Noida': {'historical': 8.5, 'current': 7.2, 'projected': 7.0}
        }
        
        # Market cycle indicators
        self.market_indicators = {
            'Mumbai': {'phase': 'stable', 'sentiment': 'positive', 'supply_demand': 'balanced'},
            'Delhi': {'phase': 'growth', 'sentiment': 'positive', 'supply_demand': 'high_demand'},
            'Bangalore': {'phase': 'growth', 'sentiment': 'very_positive', 'supply_demand': 'high_demand'},
            'Gurugram': {'phase': 'recovery', 'sentiment': 'positive', 'supply_demand': 'balanced'},
            'Noida': {'phase': 'recovery', 'sentiment': 'neutral', 'supply_demand': 'oversupply'}
        }
    
    def calculate_current_property_value(self, purchase_price: float, purchase_date: str, 
                                       city: str, property_type: str = 'Apartment', 
                                       district: str = None, sub_district: str = None) -> Dict:
        """Calculate current property value based on historical appreciation"""
        try:
            # Parse purchase date
            purchase_date_obj = datetime.strptime(purchase_date, '%Y-%m-%d')
            current_date = datetime.now()
            years_held = (current_date - purchase_date_obj).days / 365.25
            
            # Get city appreciation rate
            city_rates = self.city_appreciation_rates.get(city, {'historical': 8.0})
            appreciation_rate = city_rates['historical']
            
            # Adjust for property type
            property_multipliers = {
                'Apartment': 1.0,
                'Villa': 1.1,
                'Independent House': 1.05,
                'Studio': 0.95,
                'Penthouse': 1.15
            }
            
            # District-specific adjustments
            district_multipliers = {
                'Mumbai': {
                    'South Mumbai': 1.15,
                    'Western Suburbs': 1.1,
                    'Central Mumbai': 1.05,
                    'Eastern Suburbs': 1.0,
                    'Navi Mumbai': 0.95
                },
                'Delhi': {
                    'Central Delhi': 1.1,
                    'South Delhi': 1.15,
                    'West Delhi': 1.05,
                    'East Delhi': 0.95,
                    'North Delhi': 1.0
                },
                'Bangalore': {
                    'South Bangalore': 1.1,
                    'North Bangalore': 1.05,
                    'East Bangalore': 1.0,
                    'West Bangalore': 1.08,
                    'Central Bangalore': 1.12
                },
                'Gurugram': {
                    'Cyber City': 1.1,
                    'Golf Course Extension': 1.08,
                    'Sohna Road': 1.05,
                    'New Gurugram': 1.0,
                    'Old Gurugram': 0.95
                },
                'Noida': {
                    'Sector 62': 1.05,
                    'Greater Noida': 1.0,
                    'Noida Extension': 0.95,
                    'Central Noida': 1.08,
                    'Noida Expressway': 1.1
                }
            }
            
            type_multiplier = property_multipliers.get(property_type, 1.0)
            district_multiplier = 1.0
            
            if district and city in district_multipliers:
                district_multiplier = district_multipliers[city].get(district, 1.0)
            
            adjusted_rate = appreciation_rate * type_multiplier * district_multiplier
            
            # Calculate current value with compound appreciation
            current_value = purchase_price * ((1 + adjusted_rate/100) ** years_held)
            
            # Calculate gains
            total_gain = current_value - purchase_price
            total_gain_percentage = (total_gain / purchase_price) * 100
            annual_gain_percentage = total_gain_percentage / years_held if years_held > 0 else 0
            
            return {
                'purchase_price': purchase_price,
                'current_estimated_value': current_value,
                'total_gain': total_gain,
                'total_gain_percentage': total_gain_percentage,
                'annual_gain_percentage': annual_gain_percentage,
                'years_held': years_held,
                'appreciation_rate_used': adjusted_rate,
                'city': city,
                'property_type': property_type,
                'district': district,
                'sub_district': sub_district
            }
            
        except Exception as e:
            logger.error(f"Error calculating current value: {str(e)}")
            return {}
    
    def should_sell_or_hold(self, property_value_data: Dict, current_market_price: float = None) -> Dict:
        """Analyze whether to sell or hold the property"""
        try:
            city = property_value_data['city']
            current_value = property_value_data['current_estimated_value']
            annual_gain = property_value_data['annual_gain_percentage']
            years_held = property_value_data['years_held']
            
            # Get market indicators
            market_info = self.market_indicators.get(city, {})
            city_rates = self.city_appreciation_rates.get(city, {})
            
            # Decision factors
            factors = {
                'hold_factors': [],
                'sell_factors': [],
                'scores': {}
            }
            
            # Factor 1: Historical performance vs market
            if annual_gain >= city_rates.get('historical', 8.0):
                factors['hold_factors'].append("Property has outperformed market average")
                factors['scores']['performance'] = 8
            elif annual_gain >= 6.0:
                factors['hold_factors'].append("Property shows steady appreciation")
                factors['scores']['performance'] = 6
            else:
                factors['sell_factors'].append("Property underperforming market")
                factors['scores']['performance'] = 3
            
            # Factor 2: Market phase
            market_phase = market_info.get('phase', 'stable')
            if market_phase == 'growth':
                factors['hold_factors'].append("Market is in growth phase")
                factors['scores']['market_phase'] = 8
            elif market_phase == 'stable':
                factors['hold_factors'].append("Stable market conditions")
                factors['scores']['market_phase'] = 6
            else:  # recovery
                factors['sell_factors'].append("Market in recovery phase")
                factors['scores']['market_phase'] = 4
            
            # Factor 3: Holding period
            if years_held < 3:
                factors['sell_factors'].append("Short holding period - consider tax implications")
                factors['scores']['holding_period'] = 4
            elif years_held < 10:
                factors['hold_factors'].append("Good holding period for appreciation")
                factors['scores']['holding_period'] = 7
            else:
                factors['sell_factors'].append("Long holding period - consider taking profits")
                factors['scores']['holding_period'] = 5
            
            # Factor 4: Future prospects
            projected_rate = city_rates.get('projected', 7.0)
            if projected_rate >= 8.5:
                factors['hold_factors'].append("Strong future growth prospects")
                factors['scores']['future_prospects'] = 8
            elif projected_rate >= 7.0:
                factors['hold_factors'].append("Moderate future growth expected")
                factors['scores']['future_prospects'] = 6
            else:
                factors['sell_factors'].append("Limited future growth potential")
                factors['scores']['future_prospects'] = 4
            
            # Factor 5: Market sentiment
            sentiment = market_info.get('sentiment', 'neutral')
            if sentiment == 'very_positive':
                factors['hold_factors'].append("Very positive market sentiment")
                factors['scores']['sentiment'] = 9
            elif sentiment == 'positive':
                factors['hold_factors'].append("Positive market sentiment")
                factors['scores']['sentiment'] = 7
            else:
                factors['sell_factors'].append("Neutral/negative market sentiment")
                factors['scores']['sentiment'] = 4
            
            # Calculate overall score
            total_score = sum(factors['scores'].values())
            max_possible = 40  # 5 factors * 8 max score each
            recommendation_score = (total_score / max_possible) * 100
            
            # Make recommendation
            if recommendation_score >= 70:
                recommendation = "HOLD"
                confidence = "High"
                reasoning = "Strong fundamentals and growth prospects favor holding"
            elif recommendation_score >= 55:
                recommendation = "HOLD"
                confidence = "Moderate" 
                reasoning = "Market conditions generally support holding"
            elif recommendation_score >= 40:
                recommendation = "NEUTRAL"
                confidence = "Moderate"
                reasoning = "Mixed signals - consider personal financial goals"
            else:
                recommendation = "CONSIDER SELLING"
                confidence = "Moderate"
                reasoning = "Market conditions favor selling or diversifying"
            
            # Market comparison
            market_comparison = ""
            if current_market_price:
                value_vs_market = ((current_value - current_market_price) / current_market_price) * 100
                if value_vs_market > 10:
                    market_comparison = f"Property valued {value_vs_market:.1f}% above current market - good selling opportunity"
                elif value_vs_market < -10:
                    market_comparison = f"Property valued {abs(value_vs_market):.1f}% below market - hold for recovery"
                else:
                    market_comparison = f"Property fairly valued relative to market ({value_vs_market:.1f}% difference)"
            
            return {
                'recommendation': recommendation,
                'confidence': confidence,
                'reasoning': reasoning,
                'recommendation_score': recommendation_score,
                'hold_factors': factors['hold_factors'],
                'sell_factors': factors['sell_factors'],
                'market_comparison': market_comparison,
                'projected_1_year_value': current_value * (1 + projected_rate/100),
                'projected_3_year_value': current_value * ((1 + projected_rate/100) ** 3),
                'projected_5_year_value': current_value * ((1 + projected_rate/100) ** 5)
            }
            
        except Exception as e:
            logger.error(f"Error in sell/hold analysis: {str(e)}")
            return {}
    
    def analyze_investment_opportunity(self, asking_price: float, property_details: Dict, 
                                     comparable_market_price: float = None) -> Dict:
        """Analyze if a property at given price is a good investment opportunity"""
        try:
            city = property_details.get('city', 'Mumbai')
            property_type = property_details.get('property_type', 'Apartment')
            area_sqft = property_details.get('area_sqft', 1000)
            
            # Get market data
            city_rates = self.city_appreciation_rates.get(city, {'projected': 7.0})
            market_info = self.market_indicators.get(city, {})
            projected_rate = city_rates['projected']
            
            # Calculate metrics
            analysis = {
                'investment_score': 0,
                'recommendation': '',
                'key_insights': [],
                'risk_factors': [],
                'financial_projections': {}
            }
            
            # Price per sq ft analysis
            price_per_sqft = asking_price / area_sqft
            
            # City benchmark price per sq ft (approximate current market rates)
            city_benchmarks = {
                'Mumbai': 15000,
                'Delhi': 12000,
                'Bangalore': 8000,
                'Gurugram': 9000,
                'Noida': 6500
            }
            
            benchmark_price = city_benchmarks.get(city, 10000)
            price_premium = ((price_per_sqft - benchmark_price) / benchmark_price) * 100
            
            # Investment scoring factors
            score_components = {}
            
            # 1. Price competitiveness (25% weight)
            if price_premium <= -15:
                score_components['price'] = 25
                analysis['key_insights'].append(f"Excellent price - {abs(price_premium):.1f}% below market")
            elif price_premium <= -5:
                score_components['price'] = 20
                analysis['key_insights'].append(f"Good price - {abs(price_premium):.1f}% below market")
            elif price_premium <= 5:
                score_components['price'] = 15
                analysis['key_insights'].append("Fair market pricing")
            elif price_premium <= 15:
                score_components['price'] = 10
                analysis['risk_factors'].append(f"Price {price_premium:.1f}% above market")
            else:
                score_components['price'] = 5
                analysis['risk_factors'].append(f"Significantly overpriced - {price_premium:.1f}% above market")
            
            # 2. Growth potential (25% weight)
            if projected_rate >= 9:
                score_components['growth'] = 25
                analysis['key_insights'].append(f"Excellent growth potential - {projected_rate}% projected")
            elif projected_rate >= 7.5:
                score_components['growth'] = 20
                analysis['key_insights'].append(f"Good growth potential - {projected_rate}% projected")
            elif projected_rate >= 6:
                score_components['growth'] = 15
                analysis['key_insights'].append(f"Moderate growth expected - {projected_rate}%")
            else:
                score_components['growth'] = 10
                analysis['risk_factors'].append(f"Limited growth potential - {projected_rate}%")
            
            # 3. Market conditions (20% weight)
            sentiment = market_info.get('sentiment', 'neutral')
            phase = market_info.get('phase', 'stable')
            
            if sentiment == 'very_positive' and phase == 'growth':
                score_components['market'] = 20
                analysis['key_insights'].append("Excellent market conditions")
            elif sentiment == 'positive':
                score_components['market'] = 15
                analysis['key_insights'].append("Favorable market conditions")
            elif sentiment == 'neutral':
                score_components['market'] = 10
                analysis['key_insights'].append("Stable market conditions")
            else:
                score_components['market'] = 5
                analysis['risk_factors'].append("Challenging market conditions")
            
            # 4. Property characteristics (15% weight)
            char_score = 0
            if 800 <= area_sqft <= 2000:
                char_score += 5
                analysis['key_insights'].append("Optimal property size for resale")
            
            if property_type in ['Apartment', 'Villa']:
                char_score += 5
                analysis['key_insights'].append("High-demand property type")
            
            bhk = property_details.get('bhk', 2)
            if 2 <= bhk <= 3:
                char_score += 5
                analysis['key_insights'].append("Popular BHK configuration")
            
            score_components['characteristics'] = char_score
            
            # 5. Supply-demand balance (15% weight)
            supply_demand = market_info.get('supply_demand', 'balanced')
            if supply_demand == 'high_demand':
                score_components['supply_demand'] = 15
                analysis['key_insights'].append("High demand area")
            elif supply_demand == 'balanced':
                score_components['supply_demand'] = 10
                analysis['key_insights'].append("Balanced supply-demand")
            else:
                score_components['supply_demand'] = 5
                analysis['risk_factors'].append("Oversupply in the area")
            
            # Calculate total investment score
            total_score = sum(score_components.values())
            analysis['investment_score'] = total_score
            
            # Financial projections
            analysis['financial_projections'] = {
                '1_year_value': asking_price * (1 + projected_rate/100),
                '3_year_value': asking_price * ((1 + projected_rate/100) ** 3),
                '5_year_value': asking_price * ((1 + projected_rate/100) ** 5),
                '10_year_value': asking_price * ((1 + projected_rate/100) ** 10),
                'price_per_sqft': price_per_sqft,
                'market_benchmark_sqft': benchmark_price,
                'price_premium_percentage': price_premium
            }
            
            # Make recommendation
            if total_score >= 80:
                analysis['recommendation'] = "EXCELLENT BUY"
                analysis['confidence'] = "Very High"
                analysis['summary'] = "Outstanding investment opportunity with strong fundamentals"
            elif total_score >= 65:
                analysis['recommendation'] = "GOOD BUY"
                analysis['confidence'] = "High"
                analysis['summary'] = "Solid investment with good growth potential"
            elif total_score >= 50:
                analysis['recommendation'] = "FAIR BUY"
                analysis['confidence'] = "Moderate"
                analysis['summary'] = "Reasonable investment but consider alternatives"
            elif total_score >= 35:
                analysis['recommendation'] = "PROCEED WITH CAUTION"
                analysis['confidence'] = "Low"
                analysis['summary'] = "Several risk factors present"
            else:
                analysis['recommendation'] = "AVOID"
                analysis['confidence'] = "High"
                analysis['summary'] = "Poor investment opportunity"
            
            # Add comparable analysis
            if comparable_market_price:
                savings = comparable_market_price - asking_price
                savings_percentage = (savings / comparable_market_price) * 100
                if savings > 0:
                    analysis['key_insights'].append(f"Save ₹{savings:,.0f} vs comparable properties")
                else:
                    analysis['risk_factors'].append(f"Pay ₹{abs(savings):,.0f} premium vs comparable properties")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in investment analysis: {str(e)}")
            return {}
    
    def calculate_optimal_exit_strategy(self, property_value_data: Dict, target_return: float = 15.0) -> Dict:
        """Calculate optimal timing for selling based on target returns"""
        try:
            city = property_value_data['city']
            current_value = property_value_data['current_estimated_value']
            purchase_price = property_value_data['purchase_price']
            
            projected_rate = self.city_appreciation_rates.get(city, {}).get('projected', 7.0)
            
            # Calculate time to reach target return
            current_return = ((current_value - purchase_price) / purchase_price) * 100
            
            if current_return >= target_return:
                years_to_target = 0
                target_achieved = True
            else:
                # Calculate years needed to reach target
                years_to_target = np.log(1 + target_return/100) / np.log(1 + projected_rate/100)
                target_achieved = False
            
            # Calculate values at different time horizons
            projections = {}
            for years in [1, 2, 3, 5, 10]:
                future_value = current_value * ((1 + projected_rate/100) ** years)
                future_return = ((future_value - purchase_price) / purchase_price) * 100
                projections[f'{years}_year'] = {
                    'value': future_value,
                    'total_return': future_return,
                    'annual_return': future_return / (property_value_data['years_held'] + years)
                }
            
            return {
                'current_return_percentage': current_return,
                'target_return_percentage': target_return,
                'target_achieved': target_achieved,
                'years_to_target': years_to_target if not target_achieved else 0,
                'projections': projections,
                'recommendation': {
                    'optimal_hold_period': '3-5 years' if projected_rate >= 7 else '1-3 years',
                    'reasoning': f"Based on {projected_rate}% projected growth rate"
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating exit strategy: {str(e)}")
            return {}