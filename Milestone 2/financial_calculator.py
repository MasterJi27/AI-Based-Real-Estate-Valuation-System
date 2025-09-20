"""
Financial Calculator Module for Real Estate AI Application
Includes: Loan Eligibility, Tax Calculator, Registration Costs, 
Insurance Calculator, Maintenance Estimator, and Property Appreciation Tracker
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import math


class LoanEligibilityCalculator:
    """Bank-specific loan eligibility calculator"""
    
    def __init__(self):
        self.bank_criteria = {
            'SBI': {
                'max_ltv': 0.80,  # Loan to Value ratio
                'max_emi_ratio': 0.50,  # EMI to income ratio
                'min_income': 25000,
                'processing_fee': 0.0035,  # 0.35%
                'interest_rate': 8.50
            },
            'HDFC': {
                'max_ltv': 0.85,
                'max_emi_ratio': 0.55,
                'min_income': 30000,
                'processing_fee': 0.005,  # 0.5%
                'interest_rate': 8.75
            },
            'ICICI': {
                'max_ltv': 0.80,
                'max_emi_ratio': 0.50,
                'min_income': 25000,
                'processing_fee': 0.004,  # 0.4%
                'interest_rate': 8.65
            },
            'Axis Bank': {
                'max_ltv': 0.80,
                'max_emi_ratio': 0.55,
                'min_income': 30000,
                'processing_fee': 0.005,
                'interest_rate': 8.80
            },
            'PNB': {
                'max_ltv': 0.80,
                'max_emi_ratio': 0.50,
                'min_income': 20000,
                'processing_fee': 0.003,
                'interest_rate': 8.40
            }
        }
    
    def calculate_emi(self, principal, interest_rate, tenure_years):
        """Calculate EMI using formula"""
        monthly_rate = interest_rate / (12 * 100)
        tenure_months = tenure_years * 12
        
        if monthly_rate == 0:
            return principal / tenure_months if tenure_months > 0 else 0
        
        emi = principal * monthly_rate * (1 + monthly_rate)**tenure_months / ((1 + monthly_rate)**tenure_months - 1)
        return emi
    
    def check_eligibility(self, property_value, monthly_income, existing_emi, tenure_years, 
                         bank_name, applicant_age, employment_type, credit_score):
        """Check loan eligibility for specific bank"""
        
        criteria = self.bank_criteria.get(bank_name, self.bank_criteria['SBI'])
        
        # Calculate maximum eligible loan amount
        max_loan_by_ltv = property_value * criteria['max_ltv']
        
        # Calculate maximum loan by income
        available_income = monthly_income - existing_emi
        max_emi_allowed = available_income * criteria['max_emi_ratio']
        
        # Calculate maximum principal for this EMI
        max_loan_by_income = self.calculate_principal_from_emi(
            max_emi_allowed, criteria['interest_rate'], tenure_years
        )
        
        # Final eligible amount is minimum of both
        eligible_amount = min(max_loan_by_ltv, max_loan_by_income)
        
        # Apply additional criteria
        eligibility_factors = self.check_additional_criteria(
            monthly_income, applicant_age, employment_type, credit_score, criteria
        )
        
        # Adjust eligible amount based on factors
        for factor, multiplier in eligibility_factors.items():
            if multiplier < 1.0:
                eligible_amount *= multiplier
        
        # Calculate EMI for eligible amount
        actual_emi = self.calculate_emi(eligible_amount, criteria['interest_rate'], tenure_years)
        processing_fee = eligible_amount * criteria['processing_fee']
        
        return {
            'eligible_amount': max(0, eligible_amount),
            'max_loan_by_ltv': max_loan_by_ltv,
            'max_loan_by_income': max_loan_by_income,
            'monthly_emi': actual_emi,
            'processing_fee': processing_fee,
            'interest_rate': criteria['interest_rate'],
            'eligibility_factors': eligibility_factors,
            'down_payment': property_value - eligible_amount,
            'total_payment': actual_emi * tenure_years * 12,
            'total_interest': (actual_emi * tenure_years * 12) - eligible_amount
        }
    
    def calculate_principal_from_emi(self, emi, interest_rate, tenure_years):
        """Calculate principal amount from EMI"""
        monthly_rate = interest_rate / (12 * 100)
        tenure_months = tenure_years * 12
        
        if monthly_rate == 0:
            return emi * tenure_months
        
        principal = emi * ((1 + monthly_rate)**tenure_months - 1) / (monthly_rate * (1 + monthly_rate)**tenure_months)
        return principal
    
    def check_additional_criteria(self, monthly_income, age, employment_type, credit_score, criteria):
        """Check additional eligibility factors"""
        factors = {}
        
        # Income criteria
        if monthly_income < criteria['min_income']:
            factors['Low Income'] = 0.8
        elif monthly_income > 100000:
            factors['High Income'] = 1.1
        
        # Age criteria
        if age < 25:
            factors['Young Age'] = 0.9
        elif age > 55:
            factors['Senior Age'] = 0.85
        
        # Employment type
        if employment_type == 'Self-employed':
            factors['Self-employed'] = 0.9
        elif employment_type == 'Government':
            factors['Government Job'] = 1.05
        
        # Credit score
        if credit_score < 650:
            factors['Low Credit Score'] = 0.7
        elif credit_score > 750:
            factors['Excellent Credit'] = 1.1
        
        return factors


class TaxCalculator:
    """Property tax calculator for different states"""
    
    def __init__(self):
        self.tax_rates = {
            'Maharashtra': {
                'property_tax_rate': 0.02,  # 2% of annual rental value
                'professional_tax': 2500,
                'additional_charges': 0.001
            },
            'Delhi': {
                'property_tax_rate': 0.015,  # 1.5%
                'professional_tax': 2500,
                'additional_charges': 0.0008
            },
            'Karnataka': {
                'property_tax_rate': 0.018,
                'professional_tax': 2400,
                'additional_charges': 0.0009
            },
            'Haryana': {
                'property_tax_rate': 0.016,
                'professional_tax': 2500,
                'additional_charges': 0.0007
            },
            'Uttar Pradesh': {
                'property_tax_rate': 0.014,
                'professional_tax': 2500,
                'additional_charges': 0.0006
            }
        }
    
    def calculate_property_tax(self, property_value, state, property_type, built_up_area):
        """Calculate annual property tax"""
        
        tax_config = self.tax_rates.get(state, self.tax_rates['Maharashtra'])
        
        # Calculate Annual Rental Value (ARV)
        arv = property_value * 0.08  # Assuming 8% of market value as rental value
        
        # Base property tax
        base_tax = arv * tax_config['property_tax_rate']
        
        # Additional charges based on area
        additional_charges = property_value * tax_config['additional_charges']
        
        # Property type multiplier
        type_multipliers = {
            'Residential': 1.0,
            'Commercial': 1.5,
            'Industrial': 2.0
        }
        
        multiplier = type_multipliers.get(property_type, 1.0)
        total_tax = (base_tax + additional_charges) * multiplier
        
        # Calculate other taxes
        wealth_tax = self.calculate_wealth_tax(property_value)
        capital_gains_tax = self.calculate_capital_gains_potential(property_value)
        
        return {
            'annual_property_tax': total_tax,
            'monthly_property_tax': total_tax / 12,
            'annual_rental_value': arv,
            'wealth_tax': wealth_tax,
            'capital_gains_potential': capital_gains_tax,
            'total_annual_tax_liability': total_tax + wealth_tax,
            'tax_breakdown': {
                'Base Property Tax': base_tax,
                'Additional Charges': additional_charges,
                'Type Multiplier': f"{multiplier}x for {property_type}"
            }
        }
    
    def calculate_wealth_tax(self, property_value):
        """Calculate wealth tax (if applicable)"""
        # Wealth tax was abolished in India in 2015, but keeping for reference
        if property_value > 3000000:  # 30 lakhs
            return 0  # Currently 0 in India
        return 0
    
    def calculate_capital_gains_potential(self, property_value):
        """Calculate potential capital gains tax"""
        # Short term (< 2 years): As per income tax slab
        # Long term (> 2 years): 20% with indexation
        
        return {
            'short_term_rate': '30%',  # As per income tax slab
            'long_term_rate': '20%',   # With indexation benefit
            'exemption_limit': 'None',
            'indexation_benefit': 'Available for long-term'
        }


class RegistrationCostCalculator:
    """Stamp duty and registration fees calculator"""
    
    def __init__(self):
        self.stamp_duty_rates = {
            'Maharashtra': {
                'male': 0.05,      # 5%
                'female': 0.04,    # 4%
                'joint': 0.04,     # 4%
                'registration': 0.01  # 1%
            },
            'Delhi': {
                'male': 0.06,
                'female': 0.04,
                'joint': 0.04,
                'registration': 0.01
            },
            'Karnataka': {
                'male': 0.055,
                'female': 0.045,
                'joint': 0.045,
                'registration': 0.01
            },
            'Haryana': {
                'male': 0.06,
                'female': 0.04,
                'joint': 0.04,
                'registration': 0.01
            },
            'Uttar Pradesh': {
                'male': 0.07,
                'female': 0.06,
                'joint': 0.06,
                'registration': 0.01
            }
        }
    
    def calculate_registration_costs(self, property_value, state, buyer_gender, 
                                   property_type, is_first_property=True):
        """Calculate total registration costs"""
        
        rates = self.stamp_duty_rates.get(state, self.stamp_duty_rates['Maharashtra'])
        
        # Calculate stamp duty
        stamp_duty = property_value * rates[buyer_gender]
        
        # Registration fee
        registration_fee = property_value * rates['registration']
        
        # Additional charges
        additional_costs = self.calculate_additional_costs(property_value, state, is_first_property)
        
        # Legal and documentation charges
        legal_charges = property_value * 0.005  # 0.5% for legal verification
        
        total_cost = stamp_duty + registration_fee + sum(additional_costs.values()) + legal_charges
        
        return {
            'stamp_duty': stamp_duty,
            'registration_fee': registration_fee,
            'legal_charges': legal_charges,
            'additional_costs': additional_costs,
            'total_registration_cost': total_cost,
            'percentage_of_property_value': (total_cost / property_value) * 100 if property_value > 0 else 0,
            'cost_breakdown': {
                'Stamp Duty': stamp_duty,
                'Registration Fee': registration_fee,
                'Legal Charges': legal_charges,
                **additional_costs
            }
        }
    
    def calculate_additional_costs(self, property_value, state, is_first_property):
        """Calculate additional registration costs"""
        costs = {}
        
        # Documentation charges
        costs['Documentation Charges'] = min(10000, property_value * 0.001)
        
        # Valuation charges
        costs['Property Valuation'] = min(5000, property_value * 0.0005)
        
        # Search charges
        costs['Title Search'] = 2000
        
        # First-time buyer benefits
        if is_first_property and state in ['Maharashtra', 'Delhi']:
            costs['First Buyer Discount'] = -5000  # Discount
        
        # Processing charges
        costs['Processing Charges'] = 3000
        
        return costs


class HomeInsuranceCalculator:
    """Home insurance premium calculator"""
    
    def __init__(self):
        self.insurance_rates = {
            'structure': 0.001,    # 0.1% of property value
            'contents': 0.002,     # 0.2% of contents value
            'third_party': 0.0005  # 0.05% for third party liability
        }
        
        self.risk_factors = {
            'location_risk': {
                'Mumbai': 1.2,     # High risk (floods, earthquakes)
                'Delhi': 1.1,      # Medium-high risk
                'Bangalore': 0.9,  # Low risk
                'Gurugram': 1.0,   # Medium risk
                'Noida': 1.0       # Medium risk
            },
            'building_age': {
                'new': 0.8,        # 0-5 years
                'medium': 1.0,     # 5-15 years
                'old': 1.3         # 15+ years
            },
            'security_features': {
                'basic': 1.0,
                'moderate': 0.9,   # CCTV, Security guard
                'high': 0.8        # Gated community, 24x7 security
            }
        }
    
    def calculate_insurance_premium(self, property_value, contents_value, location, 
                                  building_age, security_level, coverage_type='comprehensive'):
        """Calculate annual insurance premium"""
        
        # Base premium calculation
        structure_premium = property_value * self.insurance_rates['structure']
        contents_premium = contents_value * self.insurance_rates['contents']
        liability_premium = property_value * self.insurance_rates['third_party']
        
        base_premium = structure_premium + contents_premium + liability_premium
        
        # Apply risk factors
        location_multiplier = self.risk_factors['location_risk'].get(location, 1.0)
        age_multiplier = self.risk_factors['building_age'].get(building_age, 1.0)
        security_multiplier = self.risk_factors['security_features'].get(security_level, 1.0)
        
        total_multiplier = location_multiplier * age_multiplier * security_multiplier
        
        # Coverage type adjustment
        coverage_multipliers = {
            'basic': 0.7,
            'standard': 1.0,
            'comprehensive': 1.3,
            'premium': 1.6
        }
        
        coverage_multiplier = coverage_multipliers.get(coverage_type, 1.0)
        
        final_premium = base_premium * total_multiplier * coverage_multiplier
        
        # Calculate different payment options
        monthly_premium = final_premium / 12 * 1.05  # 5% extra for monthly payments
        quarterly_premium = final_premium / 4 * 1.02  # 2% extra for quarterly
        
        return {
            'annual_premium': final_premium,
            'monthly_premium': monthly_premium,
            'quarterly_premium': quarterly_premium,
            'coverage_amount': property_value + contents_value,
            'premium_breakdown': {
                'Structure Insurance': structure_premium * total_multiplier * coverage_multiplier,
                'Contents Insurance': contents_premium * total_multiplier * coverage_multiplier,
                'Third Party Liability': liability_premium * total_multiplier * coverage_multiplier
            },
            'risk_factors': {
                'Location Risk': f"{location_multiplier}x",
                'Building Age': f"{age_multiplier}x",
                'Security Level': f"{security_multiplier}x",
                'Coverage Type': f"{coverage_multiplier}x"
            },
            'premium_percentage': (final_premium / property_value) * 100 if property_value > 0 else 0
        }


class MaintenanceCostEstimator:
    """Annual property maintenance cost estimator"""
    
    def __init__(self):
        self.maintenance_rates = {
            'Apartment': {
                'base_rate': 0.015,  # 1.5% of property value
                'age_factor': {
                    'new': 0.8,      # 0-5 years
                    'medium': 1.0,   # 5-15 years
                    'old': 1.5       # 15+ years
                }
            },
            'Villa': {
                'base_rate': 0.025,  # 2.5% of property value
                'age_factor': {
                    'new': 0.8,
                    'medium': 1.0,
                    'old': 1.6
                }
            },
            'Penthouse': {
                'base_rate': 0.02,   # 2% of property value
                'age_factor': {
                    'new': 0.9,
                    'medium': 1.1,
                    'old': 1.4
                }
            }
        }
    
    def calculate_maintenance_costs(self, property_value, property_type, property_age, 
                                  area_sqft, amenities_count, location):
        """Calculate annual maintenance costs"""
        
        # Base maintenance cost
        rates = self.maintenance_rates.get(property_type, self.maintenance_rates['Apartment'])
        base_cost = property_value * rates['base_rate']
        
        # Age factor
        if property_age <= 5:
            age_category = 'new'
        elif property_age <= 15:
            age_category = 'medium'
        else:
            age_category = 'old'
        
        age_multiplier = rates['age_factor'][age_category]
        
        # Area-based costs
        area_cost = area_sqft * 50  # ₹50 per sq ft for general maintenance
        
        # Amenities maintenance
        amenity_cost = amenities_count * 2000  # ₹2000 per amenity annually
        
        # Location factor (higher costs in metro cities)
        location_multipliers = {
            'Mumbai': 1.3,
            'Delhi': 1.2,
            'Bangalore': 1.1,
            'Gurugram': 1.15,
            'Noida': 1.05
        }
        
        location_multiplier = location_multipliers.get(location, 1.0)
        
        # Calculate total maintenance cost
        total_cost = (base_cost * age_multiplier + area_cost + amenity_cost) * location_multiplier
        
        # Break down into categories
        maintenance_breakdown = self.get_maintenance_breakdown(total_cost)
        
        return {
            'annual_maintenance_cost': total_cost,
            'monthly_maintenance_cost': total_cost / 12,
            'cost_per_sqft': total_cost / area_sqft if area_sqft > 0 else 0,
            'percentage_of_property_value': (total_cost / property_value) * 100 if property_value > 0 else 0,
            'maintenance_breakdown': maintenance_breakdown,
            'factors': {
                'Property Age': f"{age_multiplier}x ({age_category})",
                'Location': f"{location_multiplier}x ({location})",
                'Amenities': f"₹{amenity_cost:,.0f} ({amenities_count} amenities)"
            }
        }
    
    def get_maintenance_breakdown(self, total_cost):
        """Break down maintenance costs by category"""
        return {
            'Plumbing & Electrical': total_cost * 0.25,
            'Painting & Repairs': total_cost * 0.20,
            'Cleaning & Housekeeping': total_cost * 0.15,
            'Security & Utilities': total_cost * 0.15,
            'Gardening & Landscaping': total_cost * 0.10,
            'Elevator & Common Areas': total_cost * 0.10,
            'Miscellaneous': total_cost * 0.05
        }


class PropertyAppreciationTracker:
    """Property value growth and appreciation tracker"""
    
    def __init__(self):
        self.historical_appreciation = {
            'Mumbai': [8.5, 7.2, 9.1, 6.8, 8.9, 7.5, 8.2],  # Last 7 years
            'Delhi': [7.8, 6.9, 8.3, 6.2, 7.9, 7.1, 7.6],
            'Bangalore': [9.2, 8.5, 10.1, 7.9, 9.5, 8.8, 9.0],
            'Gurugram': [6.8, 5.9, 7.2, 5.5, 6.9, 6.2, 6.5],
            'Noida': [5.9, 5.2, 6.5, 4.8, 6.1, 5.5, 5.8]
        }
    
    def calculate_appreciation_forecast(self, current_value, location, forecast_years=10):
        """Calculate property appreciation forecast"""
        
        # Get historical data
        historical_rates = self.historical_appreciation.get(location, [7.0] * 7)
        avg_appreciation = np.mean(historical_rates)
        volatility = np.std(historical_rates)
        
        # Create forecast scenarios
        forecasts = {
            'conservative': avg_appreciation - volatility,
            'realistic': avg_appreciation,
            'optimistic': avg_appreciation + volatility
        }
        
        # Calculate year-by-year projections
        projections = {}
        for scenario, rate in forecasts.items():
            yearly_values = []
            value = current_value
            
            for year in range(1, forecast_years + 1):
                # Add some randomness for realistic projections
                annual_rate = rate + np.random.normal(0, volatility * 0.3)
                value = value * (1 + annual_rate / 100)
                yearly_values.append({
                    'year': year,
                    'value': value,
                    'appreciation': ((value - current_value) / current_value) * 100 if current_value > 0 else 0
                })
            
            projections[scenario] = yearly_values
        
        return {
            'current_value': current_value,
            'historical_avg_appreciation': avg_appreciation,
            'forecasts': projections,
            'market_insights': self.get_market_insights(location, avg_appreciation)
        }
    
    def get_market_insights(self, location, avg_appreciation):
        """Get market insights and trends"""
        insights = {
            'market_trend': 'Bullish' if avg_appreciation > 7 else 'Stable' if avg_appreciation > 5 else 'Bearish',
            'investment_grade': 'A+' if avg_appreciation > 8 else 'A' if avg_appreciation > 6 else 'B+',
            'risk_level': 'Low' if avg_appreciation > 7 else 'Medium',
            'recommendation': 'Strong Buy' if avg_appreciation > 8 else 'Buy' if avg_appreciation > 6 else 'Hold'
        }
        
        # Location-specific insights
        location_insights = {
            'Mumbai': 'Stable demand, premium location, good liquidity',
            'Delhi': 'Government policies impact, metro connectivity advantage',
            'Bangalore': 'IT hub growth, young demographic, high demand',
            'Gurugram': 'Corporate hub, infrastructure development ongoing',
            'Noida': 'Affordable pricing, metro expansion planned'
        }
        
        insights['location_factor'] = location_insights.get(location, 'General market conditions apply')
        
        return insights
    
    def create_appreciation_chart(self, projections, current_value):
        """Create visualization chart for appreciation"""
        fig = go.Figure()
        
        years = list(range(1, len(projections['realistic']) + 1))
        
        # Add traces for each scenario
        for scenario, color in [('conservative', 'red'), ('realistic', 'blue'), ('optimistic', 'green')]:
            values = [proj['value'] for proj in projections[scenario]]
            fig.add_trace(go.Scatter(
                x=years,
                y=values,
                mode='lines+markers',
                name=scenario.title(),
                line=dict(color=color, width=2),
                marker=dict(size=6)
            ))
        
        # Add current value as starting point
        fig.add_trace(go.Scatter(
            x=[0],
            y=[current_value],
            mode='markers',
            name='Current Value',
            marker=dict(color='black', size=10, symbol='diamond')
        ))
        
        fig.update_layout(
            title='Property Value Appreciation Forecast',
            xaxis_title='Years',
            yaxis_title='Property Value (₹)',
            hovermode='x unified',
            showlegend=True
        )
        
        return fig


def render_financial_tools():
    """Main function to render all financial tools"""
    st.header("💰 Financial Planning Tools")
    
    # Create tabs for different calculators
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🏦 Loan Eligibility", 
        "💸 Tax Calculator", 
        "📋 Registration Costs", 
        "🛡️ Insurance Calculator",
        "🔧 Maintenance Estimator",
        "📈 Appreciation Tracker"
    ])
    
    with tab1:
        render_loan_eligibility()
    
    with tab2:
        render_tax_calculator()
    
    with tab3:
        render_registration_calculator()
    
    with tab4:
        render_insurance_calculator()
    
    with tab5:
        render_maintenance_estimator()
    
    with tab6:
        render_appreciation_tracker()


def render_loan_eligibility():
    """Render loan eligibility calculator"""
    st.subheader("🏦 Bank-Specific Loan Eligibility Calculator")
    
    calculator = LoanEligibilityCalculator()
    
    col1, col2 = st.columns(2)
    
    with col1:
        property_value = st.number_input("Property Value (₹)", min_value=1000000, value=5000000, step=100000)
        monthly_income = st.number_input("Monthly Income (₹)", min_value=20000, value=75000, step=5000)
        existing_emi = st.number_input("Existing EMI (₹)", min_value=0, value=0, step=1000)
        tenure_years = st.selectbox("Loan Tenure (Years)", [10, 15, 20, 25, 30], index=3)
    
    with col2:
        bank_name = st.selectbox("Select Bank", list(calculator.bank_criteria.keys()))
        applicant_age = st.number_input("Applicant Age", min_value=21, max_value=65, value=35)
        employment_type = st.selectbox("Employment Type", ['Salaried', 'Self-employed', 'Government', 'Business'])
        credit_score = st.number_input("Credit Score", min_value=300, max_value=900, value=750)
    
    if st.button("Calculate Loan Eligibility", key="loan_calc"):
        result = calculator.check_eligibility(
            property_value, monthly_income, existing_emi, tenure_years,
            bank_name, applicant_age, employment_type, credit_score
        )
        
        if result['eligible_amount'] > 0:
            st.success(f"✅ You are eligible for a loan from {bank_name}!")
            
            # Display key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Eligible Loan Amount", f"₹{result['eligible_amount']:,.0f}")
            
            with col2:
                st.metric("Monthly EMI", f"₹{result['monthly_emi']:,.0f}")
            
            with col3:
                st.metric("Down Payment", f"₹{result['down_payment']:,.0f}")
            
            with col4:
                st.metric("Processing Fee", f"₹{result['processing_fee']:,.0f}")
            
            # Detailed breakdown
            st.subheader("Loan Details")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Loan Breakdown:**")
                st.write(f"• Interest Rate: {result['interest_rate']}%")
                st.write(f"• Total Payment: ₹{result['total_payment']:,.0f}")
                st.write(f"• Total Interest: ₹{result['total_interest']:,.0f}")
                st.write(f"• Loan-to-Value Ratio: {(result['eligible_amount']/property_value)*100:.1f}%" if property_value > 0 else "• Loan-to-Value Ratio: 0.0%")
            
            with col2:
                if result['eligibility_factors']:
                    st.write("**Eligibility Factors:**")
                    for factor, multiplier in result['eligibility_factors'].items():
                        color = "green" if multiplier > 1.0 else "red" if multiplier < 1.0 else "blue"
                        st.write(f"• {factor}: {multiplier:.1f}x", unsafe_allow_html=True)
            
            # EMI vs Income chart
            fig = go.Figure(data=[
                go.Bar(name='Available Income', x=[bank_name], y=[monthly_income - existing_emi]),
                go.Bar(name='Required EMI', x=[bank_name], y=[result['monthly_emi']])
            ])
            fig.update_layout(title='Income vs EMI Analysis', yaxis_title='Amount (₹)')
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.error(f"❌ You are not eligible for a loan from {bank_name}")
            st.write("**Possible reasons:**")
            st.write("• Insufficient income")
            st.write("• High existing EMI burden")
            st.write("• Low credit score")
            st.write("• Property value too high for income level")


def render_tax_calculator():
    """Render tax calculator"""
    st.subheader("💸 Property Tax Calculator")
    
    calculator = TaxCalculator()
    
    col1, col2 = st.columns(2)
    
    with col1:
        property_value = st.number_input("Property Value (₹)", min_value=1000000, value=5000000, step=100000, key="tax_prop_val")
        state = st.selectbox("State", list(calculator.tax_rates.keys()), key="tax_state")
        property_type = st.selectbox("Property Type", ['Residential', 'Commercial', 'Industrial'], key="tax_prop_type")
    
    with col2:
        built_up_area = st.number_input("Built-up Area (sq ft)", min_value=500, value=1200, key="tax_area")
        
    if st.button("Calculate Tax", key="tax_calc"):
        result = calculator.calculate_property_tax(property_value, state, property_type, built_up_area)
        
        st.success("Tax calculation completed!")
        
        # Display key metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Annual Property Tax", f"₹{result['annual_property_tax']:,.0f}")
        
        with col2:
            st.metric("Monthly Property Tax", f"₹{result['monthly_property_tax']:,.0f}")
        
        with col3:
            st.metric("Annual Rental Value", f"₹{result['annual_rental_value']:,.0f}")
        
        # Tax breakdown
        st.subheader("Tax Breakdown")
        
        breakdown_df = pd.DataFrame(list(result['tax_breakdown'].items()), columns=['Tax Component', 'Amount'])
        breakdown_df['Amount'] = breakdown_df['Amount'].apply(lambda x: f"₹{x:,.0f}" if isinstance(x, (int, float)) else x)
        st.table(breakdown_df)
        
        # Capital gains information
        st.subheader("Capital Gains Tax Information")
        st.info("**Short-term Capital Gains (< 2 years):** Taxed as per your income tax slab")
        st.info("**Long-term Capital Gains (> 2 years):** 20% with indexation benefit")


def render_registration_calculator():
    """Render registration cost calculator"""
    st.subheader("📋 Registration Cost Calculator")
    
    calculator = RegistrationCostCalculator()
    
    col1, col2 = st.columns(2)
    
    with col1:
        property_value = st.number_input("Property Value (₹)", min_value=1000000, value=5000000, step=100000, key="reg_prop_val")
        state = st.selectbox("State", list(calculator.stamp_duty_rates.keys()), key="reg_state")
        buyer_gender = st.selectbox("Buyer Gender", ['male', 'female', 'joint'], key="reg_gender")
    
    with col2:
        property_type = st.selectbox("Property Type", ['Residential', 'Commercial'], key="reg_prop_type")
        is_first_property = st.checkbox("First Property Purchase", value=True, key="reg_first")
    
    if st.button("Calculate Registration Costs", key="reg_calc"):
        result = calculator.calculate_registration_costs(
            property_value, state, buyer_gender, property_type, is_first_property
        )
        
        st.success("Registration cost calculation completed!")
        
        # Display key metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Registration Cost", f"₹{result['total_registration_cost']:,.0f}")
        
        with col2:
            st.metric("Stamp Duty", f"₹{result['stamp_duty']:,.0f}")
        
        with col3:
            st.metric("% of Property Value", f"{result['percentage_of_property_value']:.2f}%")
        
        # Cost breakdown
        st.subheader("Cost Breakdown")
        
        breakdown_df = pd.DataFrame(list(result['cost_breakdown'].items()), columns=['Cost Component', 'Amount (₹)'])
        breakdown_df['Amount (₹)'] = breakdown_df['Amount (₹)'].apply(lambda x: f"{x:,.0f}")
        
        # Create pie chart
        fig = px.pie(
            values=list(result['cost_breakdown'].values()),
            names=list(result['cost_breakdown'].keys()),
            title="Registration Cost Breakdown"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.table(breakdown_df)


def render_insurance_calculator():
    """Render insurance calculator"""
    st.subheader("🛡️ Home Insurance Calculator")
    
    calculator = HomeInsuranceCalculator()
    
    col1, col2 = st.columns(2)
    
    with col1:
        property_value = st.number_input("Property Value (₹)", min_value=1000000, value=5000000, step=100000, key="ins_prop_val")
        contents_value = st.number_input("Contents Value (₹)", min_value=100000, value=1000000, step=50000, key="ins_contents")
        location = st.selectbox("Location", list(calculator.risk_factors['location_risk'].keys()), key="ins_location")
    
    with col2:
        building_age = st.selectbox("Building Age", ['new', 'medium', 'old'], 
                                   format_func=lambda x: {'new': '0-5 years', 'medium': '5-15 years', 'old': '15+ years'}[x],
                                   key="ins_age")
        security_level = st.selectbox("Security Level", ['basic', 'moderate', 'high'], key="ins_security")
        coverage_type = st.selectbox("Coverage Type", ['basic', 'standard', 'comprehensive', 'premium'], key="ins_coverage")
    
    if st.button("Calculate Insurance Premium", key="ins_calc"):
        result = calculator.calculate_insurance_premium(
            property_value, contents_value, location, building_age, security_level, coverage_type
        )
        
        st.success("Insurance premium calculation completed!")
        
        # Display key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Annual Premium", f"₹{result['annual_premium']:,.0f}")
        
        with col2:
            st.metric("Monthly Premium", f"₹{result['monthly_premium']:,.0f}")
        
        with col3:
            st.metric("Coverage Amount", f"₹{result['coverage_amount']:,.0f}")
        
        with col4:
            st.metric("Premium %", f"{result['premium_percentage']:.3f}%")
        
        # Premium breakdown
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Premium Breakdown")
            breakdown_df = pd.DataFrame(list(result['premium_breakdown'].items()), columns=['Coverage Type', 'Premium (₹)'])
            breakdown_df['Premium (₹)'] = breakdown_df['Premium (₹)'].apply(lambda x: f"{x:,.0f}")
            st.table(breakdown_df)
        
        with col2:
            st.subheader("Risk Factors")
            factors_df = pd.DataFrame(list(result['risk_factors'].items()), columns=['Factor', 'Multiplier'])
            st.table(factors_df)


def render_maintenance_estimator():
    """Render maintenance cost estimator"""
    st.subheader("🔧 Maintenance Cost Estimator")
    
    calculator = MaintenanceCostEstimator()
    
    col1, col2 = st.columns(2)
    
    with col1:
        property_value = st.number_input("Property Value (₹)", min_value=1000000, value=5000000, step=100000, key="maint_prop_val")
        property_type = st.selectbox("Property Type", list(calculator.maintenance_rates.keys()), key="maint_type")
        property_age = st.number_input("Property Age (Years)", min_value=0, max_value=50, value=10, key="maint_age")
    
    with col2:
        area_sqft = st.number_input("Area (sq ft)", min_value=500, value=1200, key="maint_area")
        amenities_count = st.number_input("Number of Amenities", min_value=0, max_value=20, value=5, key="maint_amenities")
        location = st.selectbox("Location", ['Mumbai', 'Delhi', 'Bangalore', 'Gurugram', 'Noida'], key="maint_location")
    
    if st.button("Calculate Maintenance Costs", key="maint_calc"):
        result = calculator.calculate_maintenance_costs(
            property_value, property_type, property_age, area_sqft, amenities_count, location
        )
        
        st.success("Maintenance cost calculation completed!")
        
        # Display key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Annual Cost", f"₹{result['annual_maintenance_cost']:,.0f}")
        
        with col2:
            st.metric("Monthly Cost", f"₹{result['monthly_maintenance_cost']:,.0f}")
        
        with col3:
            st.metric("Cost per sq ft", f"₹{result['cost_per_sqft']:,.0f}")
        
        with col4:
            st.metric("% of Property Value", f"{result['percentage_of_property_value']:.2f}%")
        
        # Maintenance breakdown
        st.subheader("Maintenance Cost Breakdown")
        
        # Create pie chart
        fig = px.pie(
            values=list(result['maintenance_breakdown'].values()),
            names=list(result['maintenance_breakdown'].keys()),
            title="Annual Maintenance Cost Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Factors affecting cost
        st.subheader("Cost Factors")
        factors_df = pd.DataFrame(list(result['factors'].items()), columns=['Factor', 'Impact'])
        st.table(factors_df)


def render_appreciation_tracker():
    """Render property appreciation tracker"""
    st.subheader("📈 Property Appreciation Tracker")
    
    calculator = PropertyAppreciationTracker()
    
    col1, col2 = st.columns(2)
    
    with col1:
        current_value = st.number_input("Current Property Value (₹)", min_value=1000000, value=5000000, step=100000, key="appr_val")
        location = st.selectbox("Location", list(calculator.historical_appreciation.keys()), key="appr_location")
    
    with col2:
        forecast_years = st.selectbox("Forecast Period (Years)", [5, 10, 15, 20], index=1, key="appr_years")
    
    if st.button("Calculate Appreciation Forecast", key="appr_calc"):
        result = calculator.calculate_appreciation_forecast(current_value, location, forecast_years)
        
        st.success("Property appreciation forecast completed!")
        
        # Display key insights
        insights = result['market_insights']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Historical Avg", f"{result['historical_avg_appreciation']:.1f}%")
        
        with col2:
            color = "green" if insights['market_trend'] == 'Bullish' else "orange" if insights['market_trend'] == 'Stable' else "red"
            st.metric("Market Trend", insights['market_trend'])
        
        with col3:
            st.metric("Investment Grade", insights['investment_grade'])
        
        with col4:
            st.metric("Recommendation", insights['recommendation'])
        
        # Create appreciation chart
        fig = calculator.create_appreciation_chart(result['forecasts'], current_value)
        st.plotly_chart(fig, use_container_width=True)
        
        # Forecast table
        st.subheader("Detailed Forecast")
        
        # Create comparison table
        forecast_data = []
        for year in range(1, min(forecast_years + 1, 6)):  # Show first 5 years
            conservative = result['forecasts']['conservative'][year-1]
            realistic = result['forecasts']['realistic'][year-1]
            optimistic = result['forecasts']['optimistic'][year-1]
            
            forecast_data.append({
                'Year': year,
                'Conservative': f"₹{conservative['value']:,.0f}",
                'Realistic': f"₹{realistic['value']:,.0f}",
                'Optimistic': f"₹{optimistic['value']:,.0f}",
                'Realistic ROI': f"{realistic['appreciation']:.1f}%"
            })
        
        forecast_df = pd.DataFrame(forecast_data)
        st.table(forecast_df)
        
        # Market insights
        st.subheader("Market Insights")
        st.info(f"**Location Factor:** {insights['location_factor']}")
        st.info(f"**Risk Level:** {insights['risk_level']}")


if __name__ == "__main__":
    render_financial_tools()