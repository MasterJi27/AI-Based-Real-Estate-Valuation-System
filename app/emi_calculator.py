import logging
logger = logging.getLogger(__name__)
import math

class EMICalculator:
    def __init__(self):
        pass
    
    def calculate_emi(self, principal, annual_rate, tenure_years):
        """
        Calculate EMI (Equated Monthly Installment)
        
        Parameters:
        principal: Loan amount in rupees
        annual_rate: Annual interest rate in percentage
        tenure_years: Loan tenure in years
        
        Returns:
        Monthly EMI amount
        """
        try:
            # Input validation
            if not (isinstance(principal, (int, float)) and principal > 0):
                logger.warning("calculate_emi: invalid principal")
                return 0
            if not (isinstance(annual_rate, (int, float)) and annual_rate >= 0):
                logger.warning("calculate_emi: invalid annual_rate")
                return 0
            if not (isinstance(tenure_years, (int, float)) and tenure_years > 0):
                logger.warning("calculate_emi: invalid tenure_years")
                return 0
            # Convert annual rate to monthly and percentage to decimal
            monthly_rate = (annual_rate / 100) / 12
            
            # Convert years to months (must be integer for loop)
            tenure_months = int(round(tenure_years * 12))
            
            if monthly_rate == 0:
                # If no interest rate
                emi = principal / tenure_months
            else:
                # EMI formula: P * r * (1+r)^n / ((1+r)^n - 1)
                emi_numerator = principal * monthly_rate * math.pow(1 + monthly_rate, tenure_months)
                emi_denominator = math.pow(1 + monthly_rate, tenure_months) - 1
                emi = emi_numerator / emi_denominator
            
            if emi <= 0:
                logger.warning("calculate_emi: computed EMI is non-positive")
                return 0
            return round(emi, 2)
        
        except Exception as e:
            logger.exception(f"Error calculating EMI: {str(e)}")
            return 0
    
    def calculate_loan_details(self, principal, annual_rate, tenure_years):
        """
        Calculate comprehensive loan details
        
        Returns:
        Dictionary with EMI, total payment, total interest, etc.
        """
        try:
            emi = self.calculate_emi(principal, annual_rate, tenure_years)
            tenure_months = tenure_years * 12
            total_payment = emi * tenure_months
            total_interest = total_payment - principal
            
            return {
                'emi': emi,
                'total_payment': total_payment,
                'total_interest': total_interest,
                'principal': principal,
                'interest_rate': annual_rate,
                'tenure_years': tenure_years,
                'tenure_months': tenure_months
            }
        
        except Exception as e:
            logger.exception(f"Error calculating loan details: {str(e)}")
            return None
    
    def generate_amortization_schedule(self, principal, annual_rate, tenure_years):
        """
        Generate month-wise amortization schedule
        
        Returns:
        List of dictionaries with monthly breakdown
        """
        try:
            emi = self.calculate_emi(principal, annual_rate, tenure_years)
            monthly_rate = (annual_rate / 100) / 12
            tenure_months = int(round(tenure_years * 12))
            
            schedule = []
            remaining_principal = principal
            
            for month in range(1, tenure_months + 1):
                interest_payment = remaining_principal * monthly_rate
                principal_payment = emi - interest_payment
                remaining_principal -= principal_payment
                
                # Handle final month rounding
                if month == tenure_months:
                    principal_payment += remaining_principal
                    remaining_principal = 0
                
                schedule.append({
                    'month': month,
                    'emi': emi,
                    'principal_payment': round(principal_payment, 2),
                    'interest_payment': round(interest_payment, 2),
                    'remaining_principal': round(max(0, remaining_principal), 2)
                })
            
            return schedule
        
        except Exception as e:
            logger.exception(f"Error generating amortization schedule: {str(e)}")
            return []
    
    def calculate_prepayment_benefit(self, principal, annual_rate, tenure_years, prepayment_amount, prepayment_month):
        """
        Calculate benefits of making a prepayment
        
        Returns:
        Dictionary comparing scenarios with and without prepayment
        """
        try:
            # Original loan details
            original_details = self.calculate_loan_details(principal, annual_rate, tenure_years)
            
            # Generate schedule until prepayment month
            original_schedule = self.generate_amortization_schedule(principal, annual_rate, tenure_years)
            
            if prepayment_month < 1 or prepayment_month > len(original_schedule):
                return None
            
            # Outstanding principal at prepayment month
            outstanding_principal = original_schedule[prepayment_month - 1]['remaining_principal']
            
            # New principal after prepayment
            new_principal = outstanding_principal - prepayment_amount
            
            if new_principal <= 0:
                # Loan fully paid
                return {
                    'loan_closed': True,
                    'total_savings': original_details['total_interest'] - sum([month['interest_payment'] for month in original_schedule[:prepayment_month]]),
                    'months_saved': len(original_schedule) - prepayment_month
                }
            
            # Calculate remaining tenure with same EMI
            remaining_years = max((len(original_schedule) - prepayment_month) / 12, 1/12)
            new_details = self.calculate_loan_details(new_principal, annual_rate, remaining_years)
            
            # Calculate savings
            original_remaining_payment = sum([month['emi'] for month in original_schedule[prepayment_month:]])
            new_remaining_payment = new_details['total_payment']
            total_savings = original_remaining_payment - new_remaining_payment
            
            return {
                'loan_closed': False,
                'new_principal': new_principal,
                'total_savings': total_savings,
                'new_emi': new_details['emi'],
                'original_remaining_payment': original_remaining_payment,
                'new_remaining_payment': new_remaining_payment
            }
        
        except Exception as e:
            logger.exception(f"Error calculating prepayment benefit: {str(e)}")
            return None
