#!/usr/bin/env python3
"""
Buy vs Rent Investment Comparison Calculator

This script compares the financial outcomes of buying a house versus renting
and investing the difference over a 20-year period.
"""

import math


class BuyVsRentCalculator:
    """Calculator for comparing buying vs renting scenarios."""
    
    def __init__(
        self,
        house_price,
        down_payment,
        mortgage_interest_rate_annual,
        etf_monthly_yield,
        house_price_monthly_yield,
        house_maintenance_percent_annual,
        monthly_rent,
        mortgage_term_years=20
    ):
        """
        Initialize the calculator with financial parameters.
        
        Args:
            house_price: Total price of the house
            down_payment: Down payment amount
            mortgage_interest_rate_annual: Annual mortgage interest rate (as decimal, e.g., 0.03 for 3%)
            etf_monthly_yield: Monthly ETF/investment yield (as decimal, e.g., 0.007 for 0.7%)
            house_price_monthly_yield: Monthly house price appreciation (as decimal, e.g., 0.002 for 0.2%)
            house_maintenance_percent_annual: Annual house maintenance cost as % of house price (as decimal)
            monthly_rent: Monthly rent payment
            mortgage_term_years: Mortgage term in years (default: 20)
        """
        self.house_price = house_price
        self.down_payment = down_payment
        self.mortgage_interest_rate_annual = mortgage_interest_rate_annual
        self.mortgage_interest_rate_monthly = mortgage_interest_rate_annual / 12
        self.mortgage_term_years = mortgage_term_years
        self.mortgage_term_months = mortgage_term_years * 12
        self.etf_monthly_yield = etf_monthly_yield
        self.house_price_monthly_yield = house_price_monthly_yield
        self.house_maintenance_percent_annual = house_maintenance_percent_annual
        self.house_maintenance_monthly = (house_price * house_maintenance_percent_annual) / 12
        self.monthly_rent = monthly_rent
        
        # Calculate loan amount
        self.loan_amount = house_price - down_payment
        
        # Calculate monthly mortgage payment using standard mortgage formula
        self.monthly_mortgage_payment = self._calculate_monthly_mortgage_payment()
        
    def _calculate_monthly_mortgage_payment(self):
        """Calculate the fixed monthly mortgage payment."""
        if self.mortgage_interest_rate_monthly == 0:
            return self.loan_amount / self.mortgage_term_months
        
        # Standard mortgage payment formula: M = P * [r(1+r)^n] / [(1+r)^n - 1]
        r = self.mortgage_interest_rate_monthly
        n = self.mortgage_term_months
        p = self.loan_amount
        
        payment = p * (r * math.pow(1 + r, n)) / (math.pow(1 + r, n) - 1)
        return payment
    
    def calculate_buying_scenario(self, months=240):
        """
        Calculate wealth accumulation for buying scenario.
        
        Args:
            months: Number of months to simulate (default: 240 = 20 years)
            
        Returns:
            dict: Contains monthly costs, wealth progression, and final values
        """
        remaining_loan = self.loan_amount
        current_house_value = self.house_price
        wealth_progression = []
        
        for month in range(1, months + 1):
            # Calculate interest and principal for this month
            if remaining_loan > 0 and month <= self.mortgage_term_months:
                monthly_interest = remaining_loan * self.mortgage_interest_rate_monthly
                monthly_principal = self.monthly_mortgage_payment - monthly_interest
                remaining_loan = max(0, remaining_loan - monthly_principal)
                monthly_payment = self.monthly_mortgage_payment
            else:
                monthly_payment = 0
                monthly_interest = 0
                monthly_principal = 0
            
            # Calculate monthly costs
            monthly_maintenance = self.house_maintenance_monthly
            total_monthly_cost = monthly_payment + monthly_maintenance
            
            # Update house value (appreciation)
            current_house_value *= (1 + self.house_price_monthly_yield)
            
            # Calculate net wealth (house equity)
            equity = current_house_value - remaining_loan
            
            wealth_progression.append({
                'month': month,
                'monthly_cost': total_monthly_cost,
                'house_value': current_house_value,
                'remaining_loan': remaining_loan,
                'equity': equity
            })
        
        return {
            'monthly_mortgage_payment': self.monthly_mortgage_payment,
            'monthly_maintenance': self.house_maintenance_monthly,
            'initial_monthly_cost': self.monthly_mortgage_payment + self.house_maintenance_monthly,
            'wealth_progression': wealth_progression,
            'final_house_value': wealth_progression[-1]['house_value'],
            'final_equity': wealth_progression[-1]['equity']
        }
    
    def calculate_renting_scenario(self, months=240):
        """
        Calculate wealth accumulation for renting scenario.
        
        Args:
            months: Number of months to simulate (default: 240 = 20 years)
            
        Returns:
            dict: Contains monthly costs, wealth progression, and final values
        """
        # Initial investment is the down payment that would have been used for buying
        investment_portfolio = self.down_payment
        
        # Calculate what would have been the monthly mortgage payment plus maintenance
        buying_monthly_cost = self.monthly_mortgage_payment + self.house_maintenance_monthly
        
        wealth_progression = []
        
        for month in range(1, months + 1):
            # Monthly investment is the difference between what buying would cost and rent
            if month <= self.mortgage_term_months:
                monthly_investment = buying_monthly_cost - self.monthly_rent
            else:
                # After mortgage is paid off, compare only maintenance to rent
                monthly_investment = self.house_maintenance_monthly - self.monthly_rent
            
            # Add to investment portfolio
            if monthly_investment > 0:
                investment_portfolio += monthly_investment
            
            # Apply ETF yield to the portfolio
            investment_portfolio *= (1 + self.etf_monthly_yield)
            
            wealth_progression.append({
                'month': month,
                'monthly_cost': self.monthly_rent,
                'monthly_investment': monthly_investment,
                'portfolio_value': investment_portfolio
            })
        
        return {
            'monthly_rent': self.monthly_rent,
            'initial_investment': self.down_payment,
            'wealth_progression': wealth_progression,
            'final_portfolio_value': wealth_progression[-1]['portfolio_value']
        }
    
    def compare(self, months=240):
        """
        Compare buying vs renting scenarios.
        
        Args:
            months: Number of months to simulate (default: 240 = 20 years)
            
        Returns:
            dict: Contains both scenarios and comparison results
        """
        buying = self.calculate_buying_scenario(months)
        renting = self.calculate_renting_scenario(months)
        
        # Calculate total costs
        buying_total_cost = sum(w['monthly_cost'] for w in buying['wealth_progression'])
        renting_total_cost = sum(w['monthly_cost'] for w in renting['wealth_progression'])
        
        # Calculate total invested (for renting scenario)
        total_invested = self.down_payment + sum(
            max(0, w['monthly_investment']) for w in renting['wealth_progression']
        )
        
        return {
            'buying': buying,
            'renting': renting,
            'comparison': {
                'buying_total_cost': buying_total_cost,
                'renting_total_cost': renting_total_cost,
                'buying_final_wealth': buying['final_equity'],
                'renting_final_wealth': renting['final_portfolio_value'],
                'wealth_difference': buying['final_equity'] - renting['final_portfolio_value'],
                'total_invested': total_invested,
                'better_option': 'Buying' if buying['final_equity'] > renting['final_portfolio_value'] else 'Renting'
            }
        }


def print_results(results):
    """Print formatted results of the comparison."""
    print("=" * 80)
    print("BUY VS RENT COMPARISON - 20 YEAR ANALYSIS")
    print("=" * 80)
    
    print("\n--- BUYING SCENARIO ---")
    buying = results['buying']
    print(f"Monthly Mortgage Payment: CHF {buying['monthly_mortgage_payment']:,.2f}")
    print(f"Monthly Maintenance: CHF {buying['monthly_maintenance']:,.2f}")
    print(f"Total Initial Monthly Cost: CHF {buying['initial_monthly_cost']:,.2f}")
    print(f"\nFinal House Value: CHF {buying['final_house_value']:,.2f}")
    print(f"Final Equity (Net Wealth): CHF {buying['final_equity']:,.2f}")
    
    print("\n--- RENTING SCENARIO ---")
    renting = results['renting']
    print(f"Monthly Rent: CHF {renting['monthly_rent']:,.2f}")
    print(f"Initial Investment (Down Payment): CHF {renting['initial_investment']:,.2f}")
    print(f"\nFinal Portfolio Value: CHF {renting['final_portfolio_value']:,.2f}")
    
    print("\n--- COMPARISON ---")
    comp = results['comparison']
    print(f"Total Cost - Buying: CHF {comp['buying_total_cost']:,.2f}")
    print(f"Total Cost - Renting: CHF {comp['renting_total_cost']:,.2f}")
    print(f"Total Amount Invested (Renting): CHF {comp['total_invested']:,.2f}")
    print(f"\nFinal Wealth - Buying: CHF {comp['buying_final_wealth']:,.2f}")
    print(f"Final Wealth - Renting: CHF {comp['renting_final_wealth']:,.2f}")
    print(f"\nWealth Difference: CHF {comp['wealth_difference']:,.2f}")
    print(f"Better Option: {comp['better_option']}")
    
    print("\n" + "=" * 80)


def main():
    """Main function with example parameters for Switzerland."""
    # Example parameters (easily adjustable)
    house_price = 1_000_000  # CHF 1M house
    down_payment = 200_000  # CHF 200K (20% down payment)
    mortgage_interest_rate_annual = 0.03  # 3% annual
    mortgage_term_years = 20  # 20 years
    etf_monthly_yield = 0.007  # 0.7% monthly (approx 8.7% annual)
    house_price_monthly_yield = 0.002  # 0.2% monthly (approx 2.4% annual)
    house_maintenance_percent_annual = 0.01  # 1% of house price annually
    monthly_rent = 2_500  # CHF 2,500 per month
    
    print("\n--- INPUT PARAMETERS ---")
    print(f"House Price: CHF {house_price:,}")
    print(f"Down Payment: CHF {down_payment:,} ({down_payment/house_price*100:.1f}%)")
    print(f"Mortgage Interest Rate: {mortgage_interest_rate_annual*100:.2f}% annual")
    print(f"Mortgage Term: {mortgage_term_years} years")
    print(f"ETF Monthly Yield: {etf_monthly_yield*100:.2f}% ({(math.pow(1+etf_monthly_yield, 12)-1)*100:.2f}% annual)")
    print(f"House Price Monthly Yield: {house_price_monthly_yield*100:.2f}% ({(math.pow(1+house_price_monthly_yield, 12)-1)*100:.2f}% annual)")
    print(f"House Maintenance: {house_maintenance_percent_annual*100:.2f}% of house price annually")
    print(f"Monthly Rent: CHF {monthly_rent:,}")
    
    # Create calculator
    calculator = BuyVsRentCalculator(
        house_price=house_price,
        down_payment=down_payment,
        mortgage_interest_rate_annual=mortgage_interest_rate_annual,
        etf_monthly_yield=etf_monthly_yield,
        house_price_monthly_yield=house_price_monthly_yield,
        house_maintenance_percent_annual=house_maintenance_percent_annual,
        monthly_rent=monthly_rent,
        mortgage_term_years=mortgage_term_years
    )
    
    # Run comparison for 20 years (240 months)
    results = calculator.compare(months=240)
    
    # Print results
    print_results(results)


if __name__ == "__main__":
    main()
