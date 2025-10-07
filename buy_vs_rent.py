#!/usr/bin/env python3
"""
Buy vs Rent Investment Comparison Calculator

This script compares the financial outcomes of buying a house versus renting
and investing the difference over a 20-year period.
"""

import yaml
from pathlib import Path


class BuyVsRentCalculator:
    """Calculator for comparing buying vs renting scenarios."""

    def __init__(
        self,
        house_price,
        down_payment,
        mortgage_interest_rate_annual,
        etf_annual_yield,
        house_price_annual_yield,
        house_maintenance_percent_annual,
        monthly_rent,
        mortgage_term_years=20,
        mortgage_percent=0.67,
        mortgage_amortization_years=15,
        rent_annual_increase=0.03,
    ):
        """
        Initialize the calculator with financial parameters.

        Args:
            house_price: Total price of the house
            down_payment: Down payment amount
            mortgage_interest_rate_annual: Annual mortgage interest rate (as decimal, e.g., 0.03 for 3%)
            etf_annual_yield: Annual ETF/investment yield (as decimal, e.g., 0.115 for 11.5%)
            house_price_annual_yield: Annual house price appreciation (as decimal, e.g., 0.024 for 2.4%)
            house_maintenance_percent_annual: Annual house maintenance cost as % of house price (as decimal)
            monthly_rent: Monthly rent payment
            mortgage_term_years: Mortgage term in years (default: 20)
            mortgage_percent: Mortgage amount as percentage of house price (default: 0.67 for 67%)
            mortgage_amortization_years: Years to pay off the mortgage amount (default: 15)
            rent_annual_increase: Annual rent increase rate (as decimal, e.g., 0.03 for 3%)
        """
        self.house_price = house_price
        self.down_payment = down_payment
        self.mortgage_interest_rate_annual = mortgage_interest_rate_annual
        self.mortgage_interest_rate_monthly = self.annual_to_monthly_rate(
            mortgage_interest_rate_annual
        )
        self.mortgage_percent = mortgage_percent
        self.mortgage_amortization_years = mortgage_amortization_years
        self.mortgage_amortization_months = mortgage_amortization_years * 12

        # Convert annual yields to effective monthly yields
        self.etf_annual_yield = etf_annual_yield
        self.etf_monthly_yield = self.annual_to_monthly_rate(etf_annual_yield)
        self.house_price_annual_yield = house_price_annual_yield
        self.house_price_monthly_yield = self.annual_to_monthly_rate(
            house_price_annual_yield
        )

        self.house_maintenance_percent_annual = house_maintenance_percent_annual
        self.house_maintenance_monthly = self.annual_to_monthly_rate(
            house_maintenance_percent_annual
        )
        self.monthly_rent = monthly_rent
        self.rent_annual_increase = rent_annual_increase
        self.rent_monthly_increase = self.annual_to_monthly_rate(rent_annual_increase)

        # Calculate loan amount based on mortgage percentage
        self.mortgage_amount = house_price * mortgage_percent
        self.loan_amount = house_price - down_payment

        # Calculate the amount to amortize (pay down from loan_amount to mortgage_amount)
        self.amortization_amount = max(0, self.loan_amount - self.mortgage_amount)

        # Calculate monthly mortgage payment using standard mortgage formula
        self.monthly_mortgage_payment = (
            self.loan_amount * self.mortgage_interest_rate_monthly
        )

        # Calculate monthly amortization payment (principal reduction)
        self.monthly_amortization = (
            self.amortization_amount / self.mortgage_amortization_months
            if self.mortgage_amortization_months > 0
            else 0
        )

    def annual_to_monthly_rate(self, annual_rate):
        """Convert an annual interest rate to an effective monthly rate."""
        return (1 + annual_rate) ** (1 / 12) - 1

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
        buy_investment_portfolio = 0  # Track investments when buy costs < rent
        wealth_progression = []

        # Track current rent for comparison
        current_monthly_rent = self.monthly_rent

        for month in range(1, months + 1):
            # Update current rent (for comparison with buy costs)
            if month > 1:
                current_monthly_rent *= 1 + self.rent_monthly_increase

            # Calculate interest payment (always based on current remaining loan)
            monthly_interest = remaining_loan * self.mortgage_interest_rate_monthly

            # Calculate amortization payment (only during amortization period)
            if (
                month <= self.mortgage_amortization_months
                and remaining_loan > self.mortgage_amount
            ):
                monthly_amortization_payment = min(
                    self.monthly_amortization, remaining_loan - self.mortgage_amount
                )
                remaining_loan -= monthly_amortization_payment
            else:
                monthly_amortization_payment = 0

            # Total monthly payment is interest + amortization
            monthly_payment = monthly_interest + monthly_amortization_payment

            # Calculate monthly costs
            monthly_maintenance = self.house_maintenance_monthly
            total_monthly_cost = monthly_payment + monthly_maintenance

            # Calculate investment if buy costs are below rent
            monthly_investment = 0
            if total_monthly_cost < current_monthly_rent:
                monthly_investment = current_monthly_rent - total_monthly_cost
                buy_investment_portfolio += monthly_investment
                # Apply ETF yield to the portfolio
                buy_investment_portfolio *= 1 + self.etf_monthly_yield

            # Update house value (appreciation)
            current_house_value *= 1 + self.house_price_monthly_yield

            # Calculate net wealth (house equity + investment portfolio)
            equity = current_house_value - remaining_loan
            total_wealth = equity + buy_investment_portfolio

            wealth_progression.append(
                {
                    "month": month,
                    "monthly_cost": total_monthly_cost,
                    "house_value": current_house_value,
                    "remaining_loan": remaining_loan,
                    "equity": equity,
                    "monthly_investment": monthly_investment,
                    "investment_portfolio": buy_investment_portfolio,
                    "total_wealth": total_wealth,
                }
            )

        return {
            "monthly_mortgage_payment": self.monthly_mortgage_payment,
            "monthly_maintenance": self.house_maintenance_monthly,
            "initial_monthly_cost": self.monthly_mortgage_payment
            + self.monthly_amortization
            + self.house_maintenance_monthly,
            "wealth_progression": wealth_progression,
            "final_house_value": wealth_progression[-1]["house_value"],
            "final_equity": wealth_progression[-1]["equity"],
            "final_investment_portfolio": wealth_progression[-1][
                "investment_portfolio"
            ],
            "final_total_wealth": wealth_progression[-1]["total_wealth"],
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
        # Add mortgage amortization amount during amortization period

        wealth_progression = []
        current_monthly_rent = self.monthly_rent

        for month in range(1, months + 1):
            if month <= self.mortgage_amortization_months:
                buying_monthly_cost = (
                    self.monthly_mortgage_payment
                    + self.house_maintenance_monthly
                    + self.monthly_amortization
                )
            else:
                buying_monthly_cost = (
                    self.monthly_mortgage_payment + self.house_maintenance_monthly
                )
            # Apply rent increase
            if month > 1:
                current_monthly_rent *= 1 + self.rent_monthly_increase

            if buying_monthly_cost < current_monthly_rent:
                monthly_investment = 0
            else:
                monthly_investment = buying_monthly_cost - current_monthly_rent
                investment_portfolio += monthly_investment

            # Apply ETF yield to the portfolio
            investment_portfolio *= 1 + self.etf_monthly_yield

            wealth_progression.append(
                {
                    "month": month,
                    "monthly_cost": current_monthly_rent,
                    "monthly_investment": monthly_investment,
                    "portfolio_value": investment_portfolio,
                }
            )

        return {
            "monthly_rent": self.monthly_rent,
            "initial_investment": self.down_payment,
            "monthly_amortization": self.monthly_amortization,
            "amortization_months": self.mortgage_amortization_months,
            "wealth_progression": wealth_progression,
            "final_portfolio_value": wealth_progression[-1]["portfolio_value"],
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
        buying_total_cost = sum(w["monthly_cost"] for w in buying["wealth_progression"])
        renting_total_cost = sum(
            w["monthly_cost"] for w in renting["wealth_progression"]
        )

        # Calculate total invested (for both scenarios)
        buying_total_invested = sum(
            w["monthly_investment"] for w in buying["wealth_progression"]
        )
        renting_total_invested = self.down_payment + sum(
            max(0, w["monthly_investment"]) for w in renting["wealth_progression"]
        )

        return {
            "buying": buying,
            "renting": renting,
            "comparison": {
                "buying_total_cost": buying_total_cost,
                "renting_total_cost": renting_total_cost,
                "buying_final_wealth": buying["final_total_wealth"],
                "renting_final_wealth": renting["final_portfolio_value"],
                "wealth_difference": buying["final_total_wealth"]
                - renting["final_portfolio_value"],
                "buying_total_invested": buying_total_invested,
                "renting_total_invested": renting_total_invested,
                "better_option": (
                    "Buying"
                    if buying["final_total_wealth"] > renting["final_portfolio_value"]
                    else "Renting"
                ),
            },
        }


def print_results(results):
    """Print formatted results of the comparison."""
    print("=" * 80)
    print("BUY VS RENT COMPARISON - 20 YEAR ANALYSIS")
    print("=" * 80)

    print("\n--- BUYING SCENARIO ---")
    buying = results["buying"]
    print(f"Monthly Mortgage Payment: CHF {buying['monthly_mortgage_payment']:,.2f}")
    print(f"Monthly Maintenance: CHF {buying['monthly_maintenance']:,.2f}")
    print(f"Total Initial Monthly Cost: CHF {buying['initial_monthly_cost']:,.2f}")
    print(f"\nFinal House Value: CHF {buying['final_house_value']:,.2f}")
    print(f"Final Equity (Net Wealth): CHF {buying['final_equity']:,.2f}")
    print(
        f"Final Investment Portfolio: CHF {buying['final_investment_portfolio']:,.2f}"
    )
    print(f"Final Total Wealth: CHF {buying['final_total_wealth']:,.2f}")

    print("\n--- RENTING SCENARIO ---")
    renting = results["renting"]
    print(f"Monthly Rent: CHF {renting['monthly_rent']:,.2f}")
    print(
        f"Initial Investment (Down Payment): CHF {renting['initial_investment']:,.2f}"
    )
    print(
        f"Monthly Amortization Investment: CHF {renting['monthly_amortization']:,.2f} (for {renting['amortization_months']} months)"
    )
    print(f"\nFinal Portfolio Value: CHF {renting['final_portfolio_value']:,.2f}")

    print("\n--- COMPARISON ---")
    comp = results["comparison"]
    print(f"Total Cost - Buying: CHF {comp['buying_total_cost']:,.2f}")
    print(f"Total Cost - Renting: CHF {comp['renting_total_cost']:,.2f}")
    print(f"Total Amount Invested - Buying: CHF {comp['buying_total_invested']:,.2f}")
    print(f"Total Amount Invested - Renting: CHF {comp['renting_total_invested']:,.2f}")
    print(f"\nFinal Wealth - Buying: CHF {comp['buying_final_wealth']:,.2f}")
    print(f"Final Wealth - Renting: CHF {comp['renting_final_wealth']:,.2f}")
    print(f"\nWealth Difference: CHF {comp['wealth_difference']:,.2f}")
    print(f"Better Option: {comp['better_option']}")

    print("\n" + "=" * 80)


def load_config(config_path="config.yaml"):
    """Load configuration from YAML file."""
    config_file = Path(__file__).parent / config_path
    with open(config_file, "r") as f:
        return yaml.safe_load(f)


def main():
    """Main function with parameters loaded from config file."""
    # Load configuration
    config = load_config()

    simulation_years = config["simulation_years"]
    house_price = config["house_price"]
    down_payment = config["down_payment"]
    mortgage_interest_rate_annual = config["mortgage_interest_rate_annual"]
    mortgage_term_years = config["mortgage_term_years"]
    mortgage_percent = config["mortgage_percent"]
    mortgage_amortization_years = config["mortgage_amortization_years"]
    etf_annual_yield = config["etf_annual_yield"]
    house_price_annual_yield = config["house_price_annual_yield"]
    house_maintenance_percent_annual = config["house_maintenance_percent_annual"]
    monthly_rent = config["monthly_rent"]
    rent_annual_increase = config["rent_annual_increase"]

    print("\n--- INPUT PARAMETERS ---")
    print(f"House Price: CHF {house_price:,}")
    print(f"Down Payment: CHF {down_payment:,} ({down_payment/house_price*100:.1f}%)")
    print(f"Mortgage Interest Rate: {mortgage_interest_rate_annual*100:.2f}% annual")
    print(f"Mortgage Term: {mortgage_term_years} years")
    print(
        f"Mortgage Amount: {mortgage_percent*100:.0f}% of house price (CHF {house_price*mortgage_percent:,.0f})"
    )
    print(f"Mortgage Amortization Period: {mortgage_amortization_years} years")
    print(
        f"Monthly Amortization: CHF {(house_price*mortgage_percent)/(mortgage_amortization_years*12):,.2f}"
    )
    print(f"ETF Annual Yield: {etf_annual_yield*100:.2f}%")
    print(f"House Price Annual Yield: {house_price_annual_yield*100:.2f}%")
    print(
        f"House Maintenance: {house_maintenance_percent_annual*100:.2f}% of house price annually"
    )
    print(f"Monthly Rent: CHF {monthly_rent:,}")
    print(f"Rent Annual Increase: {rent_annual_increase*100:.2f}%")

    # Create calculator
    calculator = BuyVsRentCalculator(
        house_price=house_price,
        down_payment=down_payment,
        mortgage_interest_rate_annual=mortgage_interest_rate_annual,
        etf_annual_yield=etf_annual_yield,
        house_price_annual_yield=house_price_annual_yield,
        house_maintenance_percent_annual=house_maintenance_percent_annual,
        monthly_rent=monthly_rent,
        mortgage_term_years=mortgage_term_years,
        mortgage_percent=mortgage_percent,
        mortgage_amortization_years=mortgage_amortization_years,
        rent_annual_increase=rent_annual_increase,
    )
    results = calculator.compare(months=simulation_years * 12)

    # Print results
    print_results(results)


if __name__ == "__main__":
    main()
