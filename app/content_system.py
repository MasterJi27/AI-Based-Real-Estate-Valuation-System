"""
Real Estate Content & Information System
Includes: Property Buying Guides, Legal Documentation, Market Reports, 
Investment Tips, Neighborhood Guides, and Real Estate News
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from typing import Dict, List, Any


class PropertyBuyingGuide:
    """Comprehensive property buying guide with step-by-step tutorials"""
    
    def __init__(self):
        self.buying_process_steps = {
            "1": {
                "title": "Financial Planning & Budget Assessment",
                "duration": "1-2 weeks",
                "description": "Determine your budget and financial readiness",
                "steps": [
                    "Calculate your monthly income and expenses",
                    "Assess your current savings and investments",
                    "Check your credit score and credit history",
                    "Determine down payment amount (20-30% recommended)",
                    "Get pre-approved for a home loan",
                    "Factor in additional costs (registration, taxes, etc.)"
                ],
                "tips": [
                    "Keep 6 months of EMI as emergency fund",
                    "Consider future income growth in calculations",
                    "Compare loan offers from multiple banks"
                ],
                "documents_needed": [
                    "Salary slips (last 3 months)",
                    "Bank statements (last 6 months)",
                    "Income tax returns (last 2 years)",
                    "Form 16 or salary certificate"
                ]
            },
            "2": {
                "title": "Property Research & Location Analysis",
                "duration": "2-4 weeks",
                "description": "Research and shortlist potential properties",
                "steps": [
                    "Define your requirements (location, size, amenities)",
                    "Research different localities and neighborhoods",
                    "Check connectivity and infrastructure development",
                    "Analyze price trends in target areas",
                    "Visit properties and create a shortlist",
                    "Evaluate builder reputation and project approvals"
                ],
                "tips": [
                    "Visit properties at different times of the day",
                    "Check water supply, power backup, and parking",
                    "Verify RERA registration for new projects"
                ],
                "documents_needed": [
                    "RERA registration certificate",
                    "Approved building plans",
                    "Environmental clearance",
                    "No objection certificates"
                ]
            },
            "3": {
                "title": "Legal Due Diligence",
                "duration": "1-2 weeks",
                "description": "Verify legal aspects and documentation",
                "steps": [
                    "Verify property title and ownership",
                    "Check for legal disputes or liens",
                    "Confirm property tax payments are up to date",
                    "Verify building approvals and permits",
                    "Check encumbrance certificate",
                    "Hire a lawyer for legal verification"
                ],
                "tips": [
                    "Always hire an independent lawyer",
                    "Verify documents with original records",
                    "Check for any pending litigation"
                ],
                "documents_needed": [
                    "Title deed",
                    "Sale deed",
                    "Encumbrance certificate",
                    "Property tax receipts",
                    "Building plan approvals"
                ]
            },
            "4": {
                "title": "Property Valuation & Negotiation",
                "duration": "1 week",
                "description": "Assess fair value and negotiate price",
                "steps": [
                    "Get professional property valuation",
                    "Compare with similar properties in the area",
                    "Factor in property condition and amenities",
                    "Negotiate the price with seller",
                    "Finalize terms and conditions",
                    "Prepare for agreement signing"
                ],
                "tips": [
                    "Research recent sales in the same building/area",
                    "Consider market conditions while negotiating",
                    "Factor in immediate repair costs if any"
                ],
                "documents_needed": [
                    "Property valuation report",
                    "Comparative market analysis",
                    "Property inspection report"
                ]
            },
            "5": {
                "title": "Loan Processing & Approval",
                "duration": "2-4 weeks",
                "description": "Complete loan application and approval process",
                "steps": [
                    "Submit loan application with required documents",
                    "Property technical and legal verification by bank",
                    "Wait for loan approval and sanction letter",
                    "Review loan terms and conditions",
                    "Complete loan agreement signing",
                    "Arrange for property insurance"
                ],
                "tips": [
                    "Compare interest rates and processing fees",
                    "Understand all charges and hidden costs",
                    "Keep all original documents ready"
                ],
                "documents_needed": [
                    "Loan application form",
                    "Property documents",
                    "Income and identity proofs",
                    "Bank statements"
                ]
            },
            "6": {
                "title": "Agreement & Registration",
                "duration": "1-2 weeks",
                "description": "Execute sale agreement and complete registration",
                "steps": [
                    "Draft and review sale agreement",
                    "Pay token money or advance",
                    "Complete stamp duty payment",
                    "Register the property in your name",
                    "Obtain registered sale deed",
                    "Update property records"
                ],
                "tips": [
                    "Read all clauses carefully before signing",
                    "Ensure all parties are present during registration",
                    "Keep multiple copies of all documents"
                ],
                "documents_needed": [
                    "Sale agreement",
                    "Stamp duty payment receipt",
                    "Registration fees",
                    "Identity and address proofs"
                ]
            },
            "7": {
                "title": "Post-Purchase Formalities",
                "duration": "1-2 weeks",
                "description": "Complete remaining formalities after purchase",
                "steps": [
                    "Transfer utility connections (electricity, water, gas)",
                    "Update property records with local authorities",
                    "Get property insurance",
                    "Complete interior work if needed",
                    "Plan for possession and moving",
                    "Keep all documents safely"
                ],
                "tips": [
                    "Keep digital copies of all documents",
                    "Create a property file with all papers",
                    "Get property tax account updated"
                ],
                "documents_needed": [
                    "Possession certificate",
                    "Utility connection documents",
                    "Property insurance papers",
                    "Completion certificate"
                ]
            }
        }
    
    def get_timeline_visualization(self):
        """Create a visual timeline for the buying process"""
        steps = list(self.buying_process_steps.keys())
        titles = [self.buying_process_steps[step]["title"] for step in steps]
        durations = [self.buying_process_steps[step]["duration"] for step in steps]
        
        fig = go.Figure()
        
        # Add timeline bars
        for i, (step, title, duration) in enumerate(zip(steps, titles, durations)):
            fig.add_trace(go.Bar(
                x=[duration],
                y=[f"Step {step}"],
                name=title,
                orientation='h',
                text=title,
                textposition='inside',
                showlegend=False
            ))
        
        fig.update_layout(
            title="Property Buying Process Timeline",
            xaxis_title="Duration",
            yaxis_title="Steps",
            height=500
        )
        
        return fig
    
    def get_checklist(self, step_number: str):
        """Get checklist for specific step"""
        if step_number in self.buying_process_steps:
            step = self.buying_process_steps[step_number]
            return {
                "title": step["title"],
                "checklist_items": step["steps"],
                "tips": step["tips"],
                "documents": step["documents_needed"]
            }
        return None


class LegalDocumentation:
    """Legal documentation templates and sample agreements"""
    
    def __init__(self):
        self.document_templates = {
            "sale_agreement": {
                "title": "Sale Agreement Template",
                "description": "Comprehensive sale agreement for property purchase",
                "clauses": [
                    "Party Details (Buyer and Seller)",
                    "Property Description and Survey Numbers",
                    "Sale Consideration and Payment Terms",
                    "Possession and Handover Details",
                    "Title Warranty and Representations",
                    "Default and Remedies",
                    "Registration and Documentation",
                    "Miscellaneous Provisions"
                ],
                "sample_content": """
SALE AGREEMENT

This Sale Agreement is executed on [DATE] between:

SELLER: [Name], [Address], [Contact Details]
BUYER: [Name], [Address], [Contact Details]

PROPERTY DETAILS:
- Address: [Complete Property Address]
- Survey No: [Survey Number]
- Area: [Area in sq ft/sq meters]
- Type: [Apartment/Villa/Plot]

SALE CONSIDERATION:
- Total Amount: Rs. [Amount in Numbers] ([Amount in Words])
- Advance Paid: Rs. [Advance Amount]
- Balance Payment: Rs. [Balance Amount]
- Payment Schedule: [Payment Terms]

TERMS AND CONDITIONS:
1. The Seller warrants clear and marketable title
2. Property to be handed over vacant and free from encumbrances
3. All statutory approvals are in place
4. Registration to be completed within [Number] days
5. Default interest at [Rate]% per annum for delayed payments

[Additional clauses as per requirement]

SELLER SIGNATURE: _________________
BUYER SIGNATURE: _________________
WITNESS 1: _________________
WITNESS 2: _________________
                """
            },
            "rental_agreement": {
                "title": "Rental Agreement Template",
                "description": "Standard rental agreement for lease properties",
                "clauses": [
                    "Landlord and Tenant Details",
                    "Property Description",
                    "Rent and Security Deposit",
                    "Lease Term and Renewal",
                    "Maintenance and Utilities",
                    "Restrictions and House Rules",
                    "Termination Conditions",
                    "Legal Compliance"
                ],
                "sample_content": """
RENTAL/LEASE AGREEMENT

This Rental Agreement is made on [DATE] between:

LANDLORD: [Name], [Address], [Contact Details]
TENANT: [Name], [Address], [Contact Details]

PROPERTY DETAILS:
- Address: [Complete Property Address]
- Type: [1BHK/2BHK/3BHK etc.]
- Furnished Status: [Furnished/Semi-furnished/Unfurnished]

RENTAL TERMS:
- Monthly Rent: Rs. [Amount]
- Security Deposit: Rs. [Amount]
- Lease Period: [Start Date] to [End Date]
- Rent Due Date: [Date] of every month

TERMS AND CONDITIONS:
1. Rent to be paid by [Date] of each month
2. Security deposit refundable after lease end
3. No subletting without written consent
4. Maintenance of common areas by landlord
5. Electricity/water bills to be paid by tenant
6. No illegal activities permitted
7. Notice period: [Number] months for termination

LANDLORD SIGNATURE: _________________
TENANT SIGNATURE: _________________
WITNESS 1: _________________
WITNESS 2: _________________
                """
            },
            "power_of_attorney": {
                "title": "Power of Attorney for Property",
                "description": "Legal authorization for property transactions",
                "clauses": [
                    "Principal and Attorney Details",
                    "Scope of Authority",
                    "Property Specific Powers",
                    "Limitations and Restrictions",
                    "Duration and Termination",
                    "Legal Formalities",
                    "Revocation Conditions",
                    "Registration Requirements"
                ],
                "sample_content": """
POWER OF ATTORNEY

I, [Principal Name], [Address], hereby appoint [Attorney Name], [Address] as my lawful attorney to act on my behalf in the following matters:

PROPERTY DETAILS:
- Address: [Property Address]
- Survey No: [Survey Number]
- Documents: [Title Deed Numbers]

POWERS GRANTED:
1. To negotiate and finalize sale/purchase of the property
2. To execute sale deed and other documents
3. To receive/pay money on my behalf
4. To appear before registration authorities
5. To handle all legal formalities
6. To file/defend legal proceedings if necessary

LIMITATIONS:
- This POA is valid only for the above mentioned property
- Attorney cannot transfer powers to another person
- All major decisions require my written consent

DURATION: This POA is valid from [Start Date] to [End Date]

PRINCIPAL SIGNATURE: _________________
ATTORNEY SIGNATURE: _________________
WITNESS 1: _________________
WITNESS 2: _________________

Notarized on [Date] by [Notary Name]
                """
            }
        }
        
        self.legal_checklists = {
            "due_diligence": {
                "title": "Legal Due Diligence Checklist",
                "items": [
                    "Verify original title deed and chain of title",
                    "Check encumbrance certificate for 30 years",
                    "Confirm property tax payment status",
                    "Verify building plan approvals",
                    "Check for any litigation or disputes",
                    "Confirm RERA registration (for new projects)",
                    "Verify NOCs from relevant authorities",
                    "Check mortgage/lien status",
                    "Confirm seller's identity and authority",
                    "Verify survey settlement records"
                ]
            },
            "registration_process": {
                "title": "Property Registration Checklist",
                "items": [
                    "Draft sale deed with all details",
                    "Calculate and pay stamp duty",
                    "Arrange for registration fees",
                    "Book appointment with registrar",
                    "Ensure all parties are present",
                    "Carry all original documents",
                    "Complete biometric verification",
                    "Obtain registered sale deed",
                    "Update property records",
                    "Get certified copies for future use"
                ]
            }
        }


class MarketReports:
    """Market reports and analysis generator"""
    
    def __init__(self):
        self.market_data = {
            "Mumbai": {
                "q4_2024": {
                    "avg_price_psf": 15500,
                    "price_change": 8.2,
                    "inventory_months": 11,
                    "new_launches": 125,
                    "sales_volume": 2800,
                    "absorption_rate": 68,
                    "key_highlights": [
                        "Strong demand in suburban areas",
                        "Luxury segment showing resilience",
                        "Infrastructure projects boosting western suburbs"
                    ]
                },
                "q3_2024": {
                    "avg_price_psf": 14300,
                    "price_change": 6.8,
                    "inventory_months": 12,
                    "new_launches": 98,
                    "sales_volume": 2650,
                    "absorption_rate": 64
                }
            },
            "Delhi": {
                "q4_2024": {
                    "avg_price_psf": 12800,
                    "price_change": 7.5,
                    "inventory_months": 13,
                    "new_launches": 89,
                    "sales_volume": 2100,
                    "absorption_rate": 62,
                    "key_highlights": [
                        "NCR showing steady growth",
                        "Affordable housing gaining traction",
                        "Metro connectivity improving demand"
                    ]
                }
            },
            "Bangalore": {
                "q4_2024": {
                    "avg_price_psf": 8900,
                    "price_change": 9.1,
                    "inventory_months": 9,
                    "new_launches": 156,
                    "sales_volume": 3200,
                    "absorption_rate": 72,
                    "key_highlights": [
                        "IT corridor driving demand",
                        "Strong rental yields in tech hubs",
                        "New projects in emerging micro-markets"
                    ]
                }
            }
        }
    
    def generate_quarterly_report(self, city: str, quarter: str):
        """Generate quarterly market report for a city"""
        if city not in self.market_data:
            return None
        
        data = self.market_data[city].get(quarter, {})
        if not data:
            return None
        
        report = {
            "city": city,
            "quarter": quarter,
            "metrics": data,
            "analysis": self.generate_market_analysis(city, quarter),
            "forecast": self.generate_forecast(city, data),
            "recommendations": self.generate_recommendations(city, data)
        }
        
        return report
    
    def generate_market_analysis(self, city: str, quarter: str):
        """Generate market analysis text"""
        return f"""
        {city} Real Estate Market Analysis - {quarter}
        
        The {city} real estate market has shown strong momentum in {quarter}, with several 
        key trends emerging. Price appreciation has been driven by limited supply and 
        strong demand fundamentals. The market continues to benefit from infrastructure 
        development and economic growth in the region.
        
        Key drivers include:
        - Strong employment growth in IT and financial services
        - Infrastructure projects improving connectivity
        - Limited land availability driving prices higher
        - Preference for larger homes post-pandemic
        """
    
    def generate_forecast(self, city: str, data: Dict):
        """Generate market forecast"""
        current_growth = data.get("price_change", 0)
        
        forecast = {
            "next_quarter": {
                "price_change_forecast": current_growth * 0.8,
                "confidence": "Medium",
                "key_factors": ["Interest rate trends", "Policy changes", "Supply pipeline"]
            },
            "annual_outlook": {
                "price_appreciation": current_growth * 3.5,
                "market_sentiment": "Positive" if current_growth > 6 else "Stable",
                "investment_rating": "Buy" if current_growth > 7 else "Hold"
            }
        }
        
        return forecast
    
    def generate_recommendations(self, city: str, data: Dict):
        """Generate investment recommendations"""
        price_change = data.get("price_change", 0)
        absorption_rate = data.get("absorption_rate", 0)
        
        recommendations = []
        
        if price_change > 8:
            recommendations.append("Strong capital appreciation expected")
        if absorption_rate > 70:
            recommendations.append("High demand suggests good liquidity")
        if data.get("inventory_months", 15) < 12:
            recommendations.append("Limited supply creating seller's market")
        
        return recommendations
    
    def create_market_dashboard(self, city: str):
        """Create market dashboard with visualizations"""
        if city not in self.market_data:
            return None
        
        # Price trend chart
        quarters = list(self.market_data[city].keys())
        prices = [self.market_data[city][q]["avg_price_psf"] for q in quarters]
        changes = [self.market_data[city][q]["price_change"] for q in quarters]
        
        fig_price = go.Figure()
        fig_price.add_trace(go.Scatter(
            x=quarters,
            y=prices,
            mode='lines+markers',
            name='Avg Price per Sq Ft',
            line=dict(color='blue', width=3)
        ))
        fig_price.update_layout(
            title=f'{city} Average Price Trend',
            xaxis_title='Quarter',
            yaxis_title='Price per Sq Ft (₹)'
        )
        
        # Market metrics
        fig_metrics = go.Figure()
        fig_metrics.add_trace(go.Bar(
            x=quarters,
            y=changes,
            name='Price Change %',
            marker_color='green'
        ))
        fig_metrics.update_layout(
            title=f'{city} Quarterly Price Change',
            xaxis_title='Quarter',
            yaxis_title='Price Change (%)'
        )
        
        return {
            "price_trend": fig_price,
            "metrics": fig_metrics
        }


class InvestmentTips:
    """Investment tips and expert advice library"""
    
    def __init__(self):
        self.tip_categories = {
            "first_time_buyers": {
                "title": "First-Time Buyer Tips",
                "tips": [
                    {
                        "title": "Start with Financial Planning",
                        "content": "Before house hunting, get your finances in order. Save for a down payment (20-30% of property value), check your credit score, and get pre-approved for a loan. This helps you understand your budget and makes you a serious buyer in sellers' eyes.",
                        "importance": "High",
                        "difficulty": "Easy"
                    },
                    {
                        "title": "Location Over Size",
                        "content": "Choose location over size when budget is limited. A smaller property in a good location appreciates faster than a larger property in a less desirable area. Consider proximity to work, schools, hospitals, and public transport.",
                        "importance": "High",
                        "difficulty": "Medium"
                    },
                    {
                        "title": "Factor in Hidden Costs",
                        "content": "Property purchase involves several additional costs: registration (1-2%), stamp duty (4-7%), legal fees, property inspection, moving costs, and immediate repairs. Budget an extra 8-12% of property value for these expenses.",
                        "importance": "Medium",
                        "difficulty": "Easy"
                    }
                ]
            },
            "investment_strategies": {
                "title": "Real Estate Investment Strategies",
                "tips": [
                    {
                        "title": "Buy and Hold Strategy",
                        "content": "Purchase properties in growing areas and hold for long-term appreciation. Focus on locations with upcoming infrastructure, IT parks, or educational institutions. Ideal for steady rental income and capital appreciation over 7-10 years.",
                        "importance": "High",
                        "difficulty": "Medium"
                    },
                    {
                        "title": "Rental Yield Analysis",
                        "content": "Calculate rental yield (annual rent ÷ property value × 100). Aim for 3-4% gross yield in metros, 4-6% in tier-2 cities. Consider factors like maintenance costs, vacancy periods, and tenant quality when evaluating rental properties.",
                        "importance": "High",
                        "difficulty": "Hard"
                    },
                    {
                        "title": "Diversification Across Markets",
                        "content": "Don't put all investments in one location or property type. Diversify across different cities, residential vs commercial, and price segments. This reduces risk and provides multiple income streams.",
                        "importance": "Medium",
                        "difficulty": "Hard"
                    }
                ]
            },
            "market_timing": {
                "title": "Market Timing and Trends",
                "tips": [
                    {
                        "title": "Buy During Market Corrections",
                        "content": "Real estate markets are cyclical. The best buying opportunities often come during market corrections or slowdowns when prices are lower and negotiation power is higher. Avoid buying at market peaks.",
                        "importance": "High",
                        "difficulty": "Hard"
                    },
                    {
                        "title": "Monitor Interest Rate Cycles",
                        "content": "Property demand is inversely related to interest rates. When rates are low, demand increases and prices rise. Time your purchase when rates are at cyclical lows for better affordability.",
                        "importance": "Medium",
                        "difficulty": "Medium"
                    },
                    {
                        "title": "Seasonal Purchase Patterns",
                        "content": "Historically, October to March sees higher property activity due to festive season and year-end bonuses. April to September often has better deals as demand is lower. Use seasonal patterns to your advantage.",
                        "importance": "Low",
                        "difficulty": "Easy"
                    }
                ]
            }
        }
        
        self.expert_articles = [
            {
                "title": "Real Estate vs Stock Market: Where to Invest in 2025?",
                "author": "Investment Expert",
                "date": "2025-01-15",
                "category": "Investment Comparison",
                "summary": "Comprehensive analysis of real estate vs equity investments in current market conditions",
                "content": """
                With the current market dynamics, investors are torn between real estate and stock market investments. 
                Here's a detailed comparison:
                
                Real Estate Advantages:
                - Tangible asset with intrinsic value
                - Hedge against inflation
                - Rental income provides steady cash flow
                - Tax benefits under sections 80C and 24B
                
                Stock Market Advantages:
                - Higher liquidity
                - Lower transaction costs
                - Easier diversification
                - Potential for higher returns
                
                Current Recommendation: 
                For long-term wealth creation, a balanced approach with 60% stocks and 40% real estate 
                works best for most investors.
                """
            },
            {
                "title": "Emerging Micro-Markets: The Next Investment Hotspots",
                "author": "Market Analyst",
                "date": "2025-02-01",
                "category": "Market Analysis",
                "summary": "Identifying upcoming areas with high growth potential",
                "content": """
                Several micro-markets are emerging as the next investment hotspots:
                
                Mumbai: Panvel, Dombivli East
                - Navi Mumbai Airport project
                - Metro connectivity expansion
                - Industrial development
                
                Bangalore: Whitefield Extension, Electronic City Phase 2
                - IT company expansions
                - Infrastructure improvements
                - Affordable pricing compared to core areas
                
                Delhi NCR: Dwarka Expressway, Greater Noida West
                - Upcoming metro lines
                - Commercial developments
                - Government policy support
                
                Investment Strategy:
                Focus on areas with confirmed infrastructure projects and 3-5 year development timeline.
                """
            }
        ]


class NeighborhoodGuides:
    """Area-specific neighborhood guides and information"""
    
    def __init__(self):
        self.neighborhood_data = {
            "Mumbai": {
                "Bandra": {
                    "overview": "Upscale suburb known for Bollywood celebrities and vibrant nightlife",
                    "avg_price_psf": 28000,
                    "locality_type": "Premium",
                    "connectivity": {
                        "metro": "Bandra station on Western Line",
                        "airport": "25 minutes to domestic, 35 minutes to international",
                        "highways": "Western Express Highway, Bandra-Worli Sea Link"
                    },
                    "amenities": {
                        "schools": ["Hill Spring International", "Jamnabai Narsee School"],
                        "hospitals": ["Lilavati Hospital", "Bhabha Hospital"],
                        "malls": ["Palladium Mall", "Linking Road Market"],
                        "restaurants": ["The Tasting Room", "Olive Bar & Kitchen"]
                    },
                    "demographics": {
                        "family_friendly": 9,
                        "young_professionals": 8,
                        "safety": 9,
                        "nightlife": 9
                    },
                    "investment_outlook": {
                        "capital_appreciation": "High",
                        "rental_yield": "2.5-3%",
                        "liquidity": "Excellent",
                        "risk_level": "Low"
                    }
                },
                "Andheri": {
                    "overview": "Central suburb with excellent connectivity and commercial importance",
                    "avg_price_psf": 18000,
                    "locality_type": "Mid-Premium",
                    "connectivity": {
                        "metro": "Andheri station - Western and Harbour Line junction",
                        "airport": "15 minutes to domestic and international",
                        "highways": "Western Express Highway, JVLR"
                    },
                    "amenities": {
                        "schools": ["Ryan International", "Podar International"],
                        "hospitals": ["Kokilaben Hospital", "Seven Hills Hospital"],
                        "malls": ["Infiniti Mall", "Andheri Sports Club"],
                        "restaurants": ["Trishna", "The Bombay Canteen"]
                    },
                    "demographics": {
                        "family_friendly": 8,
                        "young_professionals": 9,
                        "safety": 8,
                        "nightlife": 7
                    },
                    "investment_outlook": {
                        "capital_appreciation": "High",
                        "rental_yield": "3-3.5%",
                        "liquidity": "Excellent",
                        "risk_level": "Low"
                    }
                }
            },
            "Bangalore": {
                "Whitefield": {
                    "overview": "IT hub with major tech companies and modern infrastructure",
                    "avg_price_psf": 6500,
                    "locality_type": "IT Corridor",
                    "connectivity": {
                        "metro": "Upcoming metro extension",
                        "airport": "45 minutes to Kempegowda Airport",
                        "highways": "Outer Ring Road, Old Madras Road"
                    },
                    "amenities": {
                        "schools": ["Delhi Public School", "Vydehi School"],
                        "hospitals": ["Vydehi Institute", "Manipal Hospital"],
                        "malls": ["Phoenix MarketCity", "VR Bengaluru"],
                        "restaurants": ["Barbeque Nation", "Absolute Barbecues"]
                    },
                    "demographics": {
                        "family_friendly": 8,
                        "young_professionals": 10,
                        "safety": 8,
                        "nightlife": 6
                    },
                    "investment_outlook": {
                        "capital_appreciation": "Very High",
                        "rental_yield": "4-5%",
                        "liquidity": "Good",
                        "risk_level": "Medium"
                    }
                }
            }
        }
    
    def get_neighborhood_score(self, city: str, area: str):
        """Calculate overall neighborhood score"""
        if city not in self.neighborhood_data or area not in self.neighborhood_data[city]:
            return None
        
        data = self.neighborhood_data[city][area]
        demographics = data["demographics"]
        
        # Calculate weighted score
        weights = {"family_friendly": 0.25, "young_professionals": 0.25, "safety": 0.3, "nightlife": 0.2}
        score = sum(demographics[factor] * weight for factor, weight in weights.items())
        
        return {
            "overall_score": round(score, 1),
            "breakdown": demographics,
            "rating": "Excellent" if score >= 8.5 else "Very Good" if score >= 7.5 else "Good" if score >= 6.5 else "Average"
        }
    
    def compare_neighborhoods(self, comparisons: List[Dict]):
        """Compare multiple neighborhoods"""
        comparison_data = []
        
        for comp in comparisons:
            city, area = comp["city"], comp["area"]
            if city in self.neighborhood_data and area in self.neighborhood_data[city]:
                data = self.neighborhood_data[city][area]
                score = self.get_neighborhood_score(city, area)
                
                comparison_data.append({
                    "Location": f"{area}, {city}",
                    "Price/sq ft": f"₹{data['avg_price_psf']:,}",
                    "Overall Score": score["overall_score"],
                    "Safety": data["demographics"]["safety"],
                    "Family Friendly": data["demographics"]["family_friendly"],
                    "Investment Outlook": data["investment_outlook"]["capital_appreciation"]
                })
        
        return pd.DataFrame(comparison_data)


class RealEstateNews:
    """Real estate news and market updates system"""
    
    def __init__(self):
        self.news_articles = [
            {
                "id": 1,
                "title": "RBI Maintains Repo Rate at 6.5%, Real Estate Sector Optimistic",
                "summary": "Reserve Bank of India keeps interest rates unchanged, providing stability to home loan borrowers",
                "category": "Policy",
                "date": "2025-02-08",
                "source": "Economic Times",
                "impact": "Positive",
                "relevance": "High",
                "content": """
                The Reserve Bank of India has decided to maintain the repo rate at 6.5% in its latest monetary policy review. 
                This decision brings relief to the real estate sector, which had been anticipating a potential rate hike.
                
                Key Implications:
                - Home loan EMIs remain stable for existing borrowers
                - New buyers can continue to benefit from current interest rates
                - Developers expect sustained demand in the housing market
                - Real estate stocks gained 2-3% post announcement
                
                Industry experts believe this stability will support the ongoing recovery in the real estate sector, 
                particularly in the affordable and mid-income housing segments.
                """
            },
            {
                "id": 2,
                "title": "RERA Completion Rates Improve to 68% in 2024",
                "summary": "Real Estate Regulatory Authority reports significant improvement in project completion rates",
                "category": "Regulation",
                "date": "2025-02-05",
                "source": "Business Standard",
                "impact": "Positive",
                "relevance": "High",
                "content": """
                The Real Estate Regulatory Authority (RERA) has reported that project completion rates have improved 
                to 68% in 2024, up from 58% in 2023. This marks a significant improvement in the sector's delivery performance.
                
                Key Statistics:
                - 68% projects completed on time (vs 58% in 2023)
                - Delayed projects reduced by 15%
                - Consumer complaints decreased by 22%
                - Recovery of stuck projects increased to 45%
                
                This improvement is attributed to:
                - Stricter RERA enforcement
                - Better funding mechanisms for developers
                - Improved project monitoring systems
                - Increased buyer confidence leading to better sales
                """
            },
            {
                "id": 3,
                "title": "Mumbai Real Estate Prices Rise 12% YoY in January 2025",
                "summary": "Mumbai property prices show strong growth driven by limited supply and high demand",
                "category": "Market Update",
                "date": "2025-02-03",
                "source": "Times of India",
                "impact": "Mixed",
                "relevance": "High",
                "content": """
                Mumbai's real estate market has witnessed a significant price appreciation of 12% year-on-year in January 2025, 
                making it one of the best-performing markets in the country.
                
                Key Drivers:
                - Limited land availability constraining supply
                - Strong demand from end-users and investors
                - Infrastructure projects boosting connectivity
                - Corporate hiring driving migration to Mumbai
                
                Segment-wise Performance:
                - Luxury segment: 15% price increase
                - Mid-income: 11% price increase  
                - Affordable: 8% price increase
                
                Experts suggest this trend may continue in the near term, though affordability concerns are emerging 
                for first-time buyers in certain micro-markets.
                """
            }
        ]
        
        self.market_updates = {
            "weekly": [
                {
                    "week": "Feb 3-9, 2025",
                    "highlights": [
                        "Mumbai property registrations up 18% week-on-week",
                        "Bangalore new launches reach 15-month high",
                        "Delhi NCR inventory levels drop to 11 months",
                        "Pune rental yields improve to 3.2%"
                    ],
                    "key_metrics": {
                        "total_sales": 12500,
                        "new_launches": 8900,
                        "price_index": 152.3,
                        "inventory_months": 10.8
                    }
                }
            ]
        }
    
    def get_news_by_category(self, category: str = None):
        """Get news articles by category"""
        if category:
            return [article for article in self.news_articles if article["category"].lower() == category.lower()]
        return self.news_articles
    
    def get_market_sentiment(self):
        """Calculate market sentiment based on recent news"""
        positive_news = len([article for article in self.news_articles if article["impact"] == "Positive"])
        total_news = len(self.news_articles)
        
        sentiment_score = (positive_news / total_news) * 100
        
        if sentiment_score >= 70:
            sentiment = "Bullish"
        elif sentiment_score >= 50:
            sentiment = "Neutral"
        else:
            sentiment = "Bearish"
        
        return {
            "sentiment": sentiment,
            "score": sentiment_score,
            "positive_news": positive_news,
            "total_news": total_news,
            "confidence": "High" if total_news >= 10 else "Medium"
        }


def render_content_system():
    """Main function to render the content and information system"""
    st.header("📚 Real Estate Knowledge Center")
    st.markdown("### Comprehensive guides, legal documentation, and market insights")
    
    # Create tabs for different content sections
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📖 Buying Guide", 
        "⚖️ Legal Docs", 
        "📊 Market Reports", 
        "💡 Investment Tips",
        "🏘️ Neighborhood Guides",
        "📰 News & Updates"
    ])
    
    with tab1:
        render_buying_guide()
    
    with tab2:
        render_legal_documentation()
    
    with tab3:
        render_market_reports()
    
    with tab4:
        render_investment_tips()
    
    with tab5:
        render_neighborhood_guides()
    
    with tab6:
        render_news_updates()


def render_buying_guide():
    """Render property buying guide interface"""
    st.subheader("📖 Complete Property Buying Guide")
    
    guide = PropertyBuyingGuide()
    
    # Timeline visualization
    st.subheader("🗓️ Buying Process Timeline")
    timeline_fig = guide.get_timeline_visualization()
    st.plotly_chart(timeline_fig, use_container_width=True)
    
    # Step-by-step guide
    st.subheader("📋 Step-by-Step Process")
    
    selected_step = st.selectbox(
        "Select a step to view details:",
        options=list(guide.buying_process_steps.keys()),
        format_func=lambda x: f"Step {x}: {guide.buying_process_steps[x]['title']}"
    )
    
    if selected_step:
        step_data = guide.buying_process_steps[selected_step]
        
        # Step details
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"### {step_data['title']}")
            st.markdown(f"**Duration:** {step_data['duration']}")
            st.markdown(f"**Description:** {step_data['description']}")
            
            st.markdown("#### ✅ Action Items:")
            for i, step in enumerate(step_data['steps'], 1):
                st.markdown(f"{i}. {step}")
        
        with col2:
            st.markdown("#### 💡 Pro Tips:")
            for tip in step_data['tips']:
                st.info(tip)
        
        # Documents needed
        st.markdown("#### 📄 Documents Required:")
        doc_cols = st.columns(2)
        for i, doc in enumerate(step_data['documents_needed']):
            with doc_cols[i % 2]:
                st.markdown(f"• {doc}")
    
    # Download checklist
    if st.button("📥 Download Complete Checklist", key="download_checklist"):
        st.success("Checklist download initiated! (Feature would integrate with file download in production)")


def render_legal_documentation():
    """Render legal documentation interface"""
    st.subheader("⚖️ Legal Documentation Center")
    
    legal_docs = LegalDocumentation()
    
    # Document templates
    st.subheader("📋 Document Templates")
    
    template_type = st.selectbox(
        "Select document type:",
        options=list(legal_docs.document_templates.keys()),
        format_func=lambda x: legal_docs.document_templates[x]['title']
    )
    
    if template_type:
        template = legal_docs.document_templates[template_type]
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"### {template['title']}")
            st.markdown(f"**Description:** {template['description']}")
            
            # Show sample content
            with st.expander("📄 View Sample Content"):
                st.code(template['sample_content'], language='text')
        
        with col2:
            st.markdown("#### Key Clauses:")
            for clause in template['clauses']:
                st.markdown(f"• {clause}")
            
            if st.button(f"📥 Download {template['title']}", key=f"download_{template_type}"):
                st.success("Template download initiated!")
    
    # Legal checklists
    st.subheader("✅ Legal Checklists")
    
    checklist_cols = st.columns(2)
    
    for i, (key, checklist) in enumerate(legal_docs.legal_checklists.items()):
        with checklist_cols[i % 2]:
            with st.expander(checklist['title']):
                for item in checklist['items']:
                    st.checkbox(item, key=f"{key}_{item[:20]}")


def render_market_reports():
    """Render market reports interface"""
    st.subheader("📊 Market Reports & Analysis")
    
    reports = MarketReports()
    
    # City and quarter selection
    col1, col2 = st.columns(2)
    
    with col1:
        selected_city = st.selectbox("Select City", list(reports.market_data.keys()))
    
    with col2:
        available_quarters = list(reports.market_data[selected_city].keys())
        selected_quarter = st.selectbox("Select Quarter", available_quarters)
    
    if st.button("📈 Generate Report", key="generate_report"):
        report = reports.generate_quarterly_report(selected_city, selected_quarter)
        
        if report:
            # Key metrics
            st.subheader("📊 Key Metrics")
            
            metrics = report['metrics']
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Avg Price/sq ft", f"₹{metrics['avg_price_psf']:,}")
            
            with col2:
                st.metric("Price Change", f"{metrics['price_change']:.1f}%", 
                         delta=f"{metrics['price_change']:.1f}%")
            
            with col3:
                st.metric("Inventory (Months)", f"{metrics['inventory_months']}")
            
            with col4:
                st.metric("Absorption Rate", f"{metrics['absorption_rate']}%")
            
            # Market analysis
            st.subheader("📈 Market Analysis")
            st.markdown(report['analysis'])
            
            # Key highlights
            if 'key_highlights' in metrics:
                st.subheader("✨ Key Highlights")
                for highlight in metrics['key_highlights']:
                    st.markdown(f"• {highlight}")
            
            # Visualizations
            dashboard = reports.create_market_dashboard(selected_city)
            if dashboard:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.plotly_chart(dashboard['price_trend'], use_container_width=True)
                
                with col2:
                    st.plotly_chart(dashboard['metrics'], use_container_width=True)
            
            # Forecast and recommendations
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🔮 Forecast")
                forecast = report['forecast']
                st.write(f"**Next Quarter Outlook:** {forecast['next_quarter']['confidence']} confidence")
                st.write(f"**Annual Price Appreciation:** {forecast['annual_outlook']['price_appreciation']:.1f}%")
                st.write(f"**Investment Rating:** {forecast['annual_outlook']['investment_rating']}")
            
            with col2:
                st.subheader("💡 Recommendations")
                for rec in report['recommendations']:
                    st.success(rec)


def render_investment_tips():
    """Render investment tips interface"""
    st.subheader("💡 Investment Tips & Expert Advice")
    
    tips = InvestmentTips()
    
    # Tips by category
    st.subheader("📚 Tips by Category")
    
    category = st.selectbox(
        "Select category:",
        options=list(tips.tip_categories.keys()),
        format_func=lambda x: tips.tip_categories[x]['title']
    )
    
    if category:
        category_data = tips.tip_categories[category]
        
        st.markdown(f"### {category_data['title']}")
        
        for i, tip in enumerate(category_data['tips'], 1):
            with st.expander(f"{i}. {tip['title']} • {tip['importance']} Priority"):
                st.markdown(tip['content'])
                
                col1, col2 = st.columns(2)
                with col1:
                    st.badge(f"Importance: {tip['importance']}")
                with col2:
                    st.badge(f"Difficulty: {tip['difficulty']}")
    
    # Expert articles
    st.subheader("📝 Expert Articles")
    
    for article in tips.expert_articles:
        with st.expander(f"📰 {article['title']} • {article['date']}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Summary:** {article['summary']}")
                st.markdown("**Content:**")
                st.markdown(article['content'])
            
            with col2:
                st.markdown(f"**Author:** {article['author']}")
                st.markdown(f"**Category:** {article['category']}")
                st.markdown(f"**Date:** {article['date']}")


def render_neighborhood_guides():
    """Render neighborhood guides interface"""
    st.subheader("🏘️ Neighborhood Guides")
    
    guides = NeighborhoodGuides()
    
    # Single neighborhood analysis
    st.subheader("📍 Explore Neighborhoods")
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_city = st.selectbox("Select City", list(guides.neighborhood_data.keys()), key="ng_city")
    
    with col2:
        if selected_city:
            neighborhoods = list(guides.neighborhood_data[selected_city].keys())
            selected_area = st.selectbox("Select Area", neighborhoods, key="ng_area")
    
    if selected_city and selected_area:
        area_data = guides.neighborhood_data[selected_city][selected_area]
        score_data = guides.get_neighborhood_score(selected_city, selected_area)
        
        # Overview
        st.markdown(f"### {selected_area}, {selected_city}")
        st.markdown(area_data['overview'])
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Avg Price/sq ft", f"₹{area_data['avg_price_psf']:,}")
        
        with col2:
            st.metric("Locality Type", area_data['locality_type'])
        
        with col3:
            st.metric("Overall Score", f"{score_data['overall_score']}/10")
        
        with col4:
            st.metric("Rating", score_data['rating'])
        
        # Detailed information
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🚇 Connectivity")
            conn = area_data['connectivity']
            st.write(f"**Metro:** {conn['metro']}")
            st.write(f"**Airport:** {conn['airport']}")
            st.write(f"**Highways:** {conn['highways']}")
            
            st.subheader("🏢 Amenities")
            amenities = area_data['amenities']
            
            with st.expander("🏫 Schools"):
                for school in amenities['schools']:
                    st.write(f"• {school}")
            
            with st.expander("🏥 Hospitals"):
                for hospital in amenities['hospitals']:
                    st.write(f"• {hospital}")
        
        with col2:
            st.subheader("📊 Demographics Score")
            demographics = area_data['demographics']
            
            # Create radar chart for demographics
            categories = list(demographics.keys())
            values = list(demographics.values())
            
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name=selected_area
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 10]
                    )),
                showlegend=False,
                title="Neighborhood Scores"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("💰 Investment Outlook")
            investment = area_data['investment_outlook']
            
            for key, value in investment.items():
                st.write(f"**{key.replace('_', ' ').title()}:** {value}")
    
    # Neighborhood comparison
    st.subheader("⚖️ Compare Neighborhoods")
    
    st.markdown("Select up to 3 neighborhoods to compare:")
    
    comparisons = []
    for i in range(3):
        col1, col2 = st.columns(2)
        
        with col1:
            city = st.selectbox(f"City {i+1}", [""] + list(guides.neighborhood_data.keys()), key=f"comp_city_{i}")
        
        with col2:
            if city:
                areas = list(guides.neighborhood_data[city].keys())
                area = st.selectbox(f"Area {i+1}", [""] + areas, key=f"comp_area_{i}")
                
                if area:
                    comparisons.append({"city": city, "area": area})
    
    if len(comparisons) >= 2 and st.button("📊 Compare", key="compare_neighborhoods"):
        comparison_df = guides.compare_neighborhoods(comparisons)
        
        if not comparison_df.empty:
            st.subheader("📈 Comparison Results")
            st.dataframe(comparison_df, use_container_width=True)
            
            # Visualization
            fig = px.bar(
                comparison_df, 
                x='Location', 
                y='Overall Score',
                title='Neighborhood Comparison - Overall Score'
            )
            st.plotly_chart(fig, use_container_width=True)


def render_news_updates():
    """Render news and updates interface"""
    st.subheader("📰 Real Estate News & Market Updates")
    
    news = RealEstateNews()
    
    # Market sentiment
    sentiment = news.get_market_sentiment()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Market Sentiment", sentiment['sentiment'])
    
    with col2:
        st.metric("Sentiment Score", f"{sentiment['score']:.0f}%")
    
    with col3:
        st.metric("News Confidence", sentiment['confidence'])
    
    # News categories
    st.subheader("📺 Latest News")
    
    categories = ["All"] + list(set(article['category'] for article in news.news_articles))
    selected_category = st.selectbox("Filter by category:", categories)
    
    if selected_category == "All":
        filtered_news = news.news_articles
    else:
        filtered_news = news.get_news_by_category(selected_category)
    
    # Display news articles
    for article in filtered_news:
        with st.expander(f"📰 {article['title']} • {article['date']}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**{article['summary']}**")
                st.markdown(article['content'])
            
            with col2:
                st.markdown(f"**Source:** {article['source']}")
                st.markdown(f"**Category:** {article['category']}")
                
                impact_color = "green" if article['impact'] == "Positive" else "red" if article['impact'] == "Negative" else "blue"
                st.markdown(f"**Impact:** :{impact_color}[{article['impact']}]")
                
                st.markdown(f"**Relevance:** {article['relevance']}")
    
    # Weekly market updates
    st.subheader("📊 Weekly Market Highlights")
    
    if news.market_updates['weekly']:
        latest_week = news.market_updates['weekly'][0]
        
        st.markdown(f"### Week of {latest_week['week']}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔥 Key Highlights")
            for highlight in latest_week['highlights']:
                st.markdown(f"• {highlight}")
        
        with col2:
            st.markdown("#### 📈 Market Metrics")
            metrics = latest_week['key_metrics']
            
            st.metric("Total Sales", f"{metrics['total_sales']:,}")
            st.metric("New Launches", f"{metrics['new_launches']:,}")
            st.metric("Price Index", f"{metrics['price_index']}")
            st.metric("Inventory (Months)", f"{metrics['inventory_months']}")


if __name__ == "__main__":
    render_content_system()