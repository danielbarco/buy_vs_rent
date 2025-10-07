#!/usr/bin/env python3
"""
Plot Buy vs Rent Comparison

This script creates visualizations comparing the buy vs rent scenarios over time.
"""

import matplotlib.pyplot as plt
import numpy as np
from buy_vs_rent import BuyVsRentCalculator, load_config, print_results


def plot_comparison(results, months=240):
    """
    Create visualization plots for buy vs rent comparison.

    Args:
        results: Results dictionary from BuyVsRentCalculator.compare()
        months: Number of months simulated
    """
    buying = results["buying"]
    renting = results["renting"]

    # Extract data from wealth progression
    months_array = np.arange(1, months + 1)
    years_array = months_array / 12

    # Buying scenario data
    buying_equity = [w["equity"] for w in buying["wealth_progression"]]
    buying_house_value = [w["house_value"] for w in buying["wealth_progression"]]
    buying_monthly_cost = [w["monthly_cost"] for w in buying["wealth_progression"]]
    buying_remaining_loan = [w["remaining_loan"] for w in buying["wealth_progression"]]

    # Renting scenario data
    renting_portfolio = [w["portfolio_value"] for w in renting["wealth_progression"]]
    renting_monthly_cost = [w["monthly_cost"] for w in renting["wealth_progression"]]
    renting_monthly_investment = [
        w["monthly_investment"] for w in renting["wealth_progression"]
    ]

    # Calculate cumulative costs
    buying_cumulative_cost = np.cumsum(buying_monthly_cost)
    renting_cumulative_cost = np.cumsum(renting_monthly_cost)

    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle(
        "Buy vs Rent Comparison - 20 Year Analysis", fontsize=16, fontweight="bold"
    )

    # Plot 1: Wealth/Equity Over Time
    ax1 = axes[0, 0]
    ax1.plot(
        years_array,
        np.array(buying_equity) / 1000,
        label="Buying (Equity)",
        linewidth=2,
        color="blue",
    )
    ax1.plot(
        years_array,
        np.array(renting_portfolio) / 1000,
        label="Renting (Portfolio)",
        linewidth=2,
        color="green",
    )
    ax1.fill_between(
        years_array,
        0,
        np.array(buying_house_value) / 1000,
        alpha=0.1,
        color="blue",
        label="House Value",
    )
    ax1.fill_between(
        years_array,
        0,
        np.array(buying_remaining_loan) / 1000,
        alpha=0.2,
        color="red",
        label="Remaining Loan",
    )
    ax1.set_xlabel("Years", fontsize=12)
    ax1.set_ylabel("Value (CHF 1000s)", fontsize=12)
    ax1.set_title("Net Wealth Over Time", fontsize=14, fontweight="bold")
    ax1.legend(loc="upper left")
    ax1.grid(True, alpha=0.3)

    # Plot 2: Monthly Costs Over Time
    ax2 = axes[0, 1]
    ax2.plot(
        years_array,
        buying_monthly_cost,
        label="Buying (Mortgage + Maintenance)",
        linewidth=2,
        color="blue",
    )
    ax2.plot(
        years_array,
        renting_monthly_cost,
        label="Renting (Rent)",
        linewidth=2,
        color="green",
    )
    ax2.set_xlabel("Years", fontsize=12)
    ax2.set_ylabel("Monthly Cost (CHF)", fontsize=12)
    ax2.set_title("Monthly Costs Over Time", fontsize=14, fontweight="bold")
    ax2.legend(loc="upper left")
    ax2.grid(True, alpha=0.3)

    # Plot 3: Cumulative Costs Over Time
    ax3 = axes[1, 0]
    ax3.plot(
        years_array,
        buying_cumulative_cost / 1000,
        label="Buying (Total Paid)",
        linewidth=2,
        color="blue",
    )
    ax3.plot(
        years_array,
        renting_cumulative_cost / 1000,
        label="Renting (Total Rent)",
        linewidth=2,
        color="green",
    )
    ax3.set_xlabel("Years", fontsize=12)
    ax3.set_ylabel("Cumulative Cost (CHF 1000s)", fontsize=12)
    ax3.set_title("Cumulative Costs Over Time", fontsize=14, fontweight="bold")
    ax3.legend(loc="upper left")
    ax3.grid(True, alpha=0.3)

    # Plot 4: Monthly Investment (Renting Scenario)
    ax4 = axes[1, 1]
    ax4.plot(
        years_array,
        renting_monthly_investment,
        label="Monthly Investment",
        linewidth=2,
        color="green",
    )
    ax4.axhline(y=0, color="red", linestyle="--", linewidth=1, alpha=0.5)
    ax4.set_xlabel("Years", fontsize=12)
    ax4.set_ylabel("Monthly Investment (CHF)", fontsize=12)
    ax4.set_title(
        "Monthly Investment Amount (Renting Scenario)", fontsize=14, fontweight="bold"
    )
    ax4.legend(loc="upper right")
    ax4.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig


def main():
    """Main function to run the calculator and create plots."""
    # Load configuration
    config = load_config()

    simulation_years = config["simulation_years"]
    house_price = config["house_price"]
    down_payment = config["down_payment"]
    mortgage_interest_rate_annual = config["mortgage_interest_rate_annual"]
    mortgage_percent = config["mortgage_percent"]
    mortgage_amortization_years = config["mortgage_amortization_years"]
    etf_annual_yield = config["etf_annual_yield"]
    house_price_annual_yield = config["house_price_annual_yield"]
    house_maintenance_percent_annual = config["house_maintenance_percent_annual"]
    monthly_rent = config["monthly_rent"]
    rent_annual_increase = config["rent_annual_increase"]

    print("Running Buy vs Rent Calculator...")

    # Create calculator
    calculator = BuyVsRentCalculator(
        house_price=house_price,
        down_payment=down_payment,
        mortgage_interest_rate_annual=mortgage_interest_rate_annual,
        etf_annual_yield=etf_annual_yield,
        house_price_annual_yield=house_price_annual_yield,
        house_maintenance_percent_annual=house_maintenance_percent_annual,
        monthly_rent=monthly_rent,
        mortgage_percent=mortgage_percent,
        mortgage_amortization_years=mortgage_amortization_years,
        rent_annual_increase=rent_annual_increase,
    )

    # Run comparison
    results = calculator.compare(months=simulation_years * 12)

    # Print summary
    comp = results["comparison"]
    print(f"\n=== SUMMARY ===")
    print(f"Final Wealth - Buying: CHF {comp['buying_final_wealth']:,.2f}")
    print(f"Final Wealth - Renting: CHF {comp['renting_final_wealth']:,.2f}")
    print(f"Wealth Difference: CHF {comp['wealth_difference']:,.2f}")
    print(f"Better Option: {comp['better_option']}")
    print_results(results)

    # Create and show plots
    print("\nGenerating plots...")
    fig = plot_comparison(results, months=simulation_years * 12)
    plt.savefig("buy_vs_rent_comparison.png", dpi=300, bbox_inches="tight")
    print("Plot saved as 'buy_vs_rent_comparison.png'")
    plt.show()


if __name__ == "__main__":
    main()
