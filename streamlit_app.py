import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Buy vs Rent Calculator", layout="wide")

st.title("🏠 Buy vs Rent Investment Comparison Calculator")
st.markdown(
    """
This calculator compares the financial outcomes of buying a house versus renting
and investing the difference over a configurable time period.
"""
)

# Sidebar for parameters
st.sidebar.header("📊 Configuration Parameters")

# Simulation parameters
st.sidebar.subheader("Simulation")
simulation_years = st.sidebar.number_input(
    "Simulation Years",
    min_value=1,
    max_value=50,
    value=30,
    step=1,
    help="Number of years to simulate",
)

# House parameters
st.sidebar.subheader("🏡 House Parameters")
house_price = st.sidebar.number_input(
    "House Price (CHF)",
    min_value=100000,
    max_value=10000000,
    value=1000000,
    step=50000,
    help="Total price of the house",
)

down_payment = st.sidebar.number_input(
    "Down Payment (CHF)",
    min_value=0,
    max_value=house_price,
    value=200000,
    step=10000,
    help="Initial down payment amount",
)

# Mortgage parameters
st.sidebar.subheader("💰 Mortgage Parameters")
mortgage_interest_rate_annual = (
    st.sidebar.number_input(
        "Mortgage Interest Rate (%)",
        min_value=0.0,
        max_value=20.0,
        value=1.5,
        step=0.1,
        help="Annual mortgage interest rate",
    )
    / 100
)

mortgage_percent = (
    st.sidebar.number_input(
        "Mortgage Amount (% of house price)",
        min_value=0.0,
        max_value=100.0,
        value=67.0,
        step=1.0,
        help="Target mortgage amount as percentage of house price",
    )
    / 100
)

mortgage_amortization_years = st.sidebar.number_input(
    "Mortgage Amortization Period (years)",
    min_value=1,
    max_value=50,
    value=15,
    step=1,
    help="Years to pay down the mortgage to target amount",
)

# Investment parameters
st.sidebar.subheader("📈 Investment Parameters")
etf_annual_yield = (
    st.sidebar.number_input(
        "ETF Annual Yield (%)",
        min_value=0.0,
        max_value=50.0,
        value=10.78,
        step=0.1,
        help="MSCI World 10.78% 2009-2025",
    )
    / 100
)

house_price_annual_yield = (
    st.sidebar.number_input(
        "House Price Annual Appreciation (%)",
        min_value=-10.0,
        max_value=50.0,
        value=3.73,
        step=0.1,
        help="3.73% average from 2017-2025",
    )
    / 100
)

# Maintenance parameters
st.sidebar.subheader("🔧 Maintenance")
house_maintenance_percent_annual = (
    st.sidebar.number_input(
        "House Maintenance (% of house price annually)",
        min_value=0.0,
        max_value=10.0,
        value=1.0,
        step=0.1,
        help="Annual maintenance cost as percentage of house price",
    )
    / 100
)

# Rent parameters
st.sidebar.subheader("🏢 Rent Parameters")
monthly_rent = st.sidebar.number_input(
    "Monthly Rent (CHF)",
    min_value=0,
    max_value=50000,
    value=2500,
    step=100,
    help="CHF 2,075 for a 5 bedroom flat in Winterthur",
)

rent_annual_increase = (
    st.sidebar.number_input(
        "Rent Annual Increase (%)",
        min_value=0.0,
        max_value=20.0,
        value=1.4,
        step=0.1,
        help="1.4% average from 2005-2025",
    )
    / 100
)


# Calculator class
class BuyVsRentCalculator:
    def __init__(
        self,
        house_price,
        down_payment,
        mortgage_interest_rate_annual,
        etf_annual_yield,
        house_price_annual_yield,
        house_maintenance_percent_annual,
        monthly_rent,
        mortgage_percent,
        mortgage_amortization_years,
        rent_annual_increase,
    ):
        self.house_price = house_price
        self.down_payment = down_payment
        self.mortgage_interest_rate_annual = mortgage_interest_rate_annual
        self.mortgage_interest_rate_monthly = self.annual_to_monthly_rate(
            mortgage_interest_rate_annual
        )
        self.mortgage_percent = mortgage_percent
        self.mortgage_amortization_years = mortgage_amortization_years
        self.mortgage_amortization_months = mortgage_amortization_years * 12

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

        self.mortgage_amount = house_price * mortgage_percent
        self.loan_amount = house_price - down_payment
        self.amortization_amount = max(0, self.loan_amount - self.mortgage_amount)
        self.monthly_mortgage_payment = (
            self.loan_amount * self.mortgage_interest_rate_monthly
        )
        self.monthly_amortization = (
            self.amortization_amount / self.mortgage_amortization_months
            if self.mortgage_amortization_months > 0
            else 0
        )

    def annual_to_monthly_rate(self, annual_rate):
        return (1 + annual_rate) ** (1 / 12) - 1

    def calculate_buying_scenario(self, months=240):
        remaining_loan = self.loan_amount
        current_house_value = self.house_price
        buy_investment_portfolio = 0
        wealth_progression = []
        current_monthly_rent = self.monthly_rent

        for month in range(1, months + 1):
            if month > 1:
                current_monthly_rent *= 1 + self.rent_monthly_increase

            monthly_interest = remaining_loan * self.mortgage_interest_rate_monthly

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

            monthly_payment = monthly_interest + monthly_amortization_payment
            monthly_maintenance = self.house_maintenance_monthly
            total_monthly_cost = monthly_payment + monthly_maintenance

            monthly_investment = 0
            if total_monthly_cost < current_monthly_rent:
                monthly_investment = current_monthly_rent - total_monthly_cost
                buy_investment_portfolio += monthly_investment
                buy_investment_portfolio *= 1 + self.etf_monthly_yield

            current_house_value *= 1 + self.house_price_monthly_yield
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
        investment_portfolio = self.down_payment
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

            if month > 1:
                current_monthly_rent *= 1 + self.rent_monthly_increase

            if buying_monthly_cost < current_monthly_rent:
                monthly_investment = 0
            else:
                monthly_investment = buying_monthly_cost - current_monthly_rent
                investment_portfolio += monthly_investment

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
        buying = self.calculate_buying_scenario(months)
        renting = self.calculate_renting_scenario(months)

        buying_total_cost = sum(w["monthly_cost"] for w in buying["wealth_progression"])
        renting_total_cost = sum(
            w["monthly_cost"] for w in renting["wealth_progression"]
        )

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


# Run calculation
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

results = calculator.compare(months=simulation_years * 12)

# Display results
st.header("📈 Results Summary")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Final Wealth - Buying",
        f"CHF {results['comparison']['buying_final_wealth']:,.0f}",
    )
    st.caption(
        f"Total Invested: CHF {results['comparison']['buying_total_invested']:,.0f}"
    )

with col2:
    st.metric(
        "Final Wealth - Renting",
        f"CHF {results['comparison']['renting_final_wealth']:,.0f}",
    )
    st.caption(
        f"Total Invested: CHF {results['comparison']['renting_total_invested']:,.0f}"
    )

with col3:
    wealth_diff = results["comparison"]["wealth_difference"]
    st.metric(
        "Wealth Difference",
        f"CHF {abs(wealth_diff):,.0f}",
        delta=f"{results['comparison']['better_option']} is better",
        delta_color="normal" if wealth_diff > 0 else "inverse",
    )

# Detailed results
with st.expander("📊 Detailed Results"):
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Buying Scenario")
        buying = results["buying"]
        st.write(
            f"**Monthly Mortgage Payment:** CHF {buying['monthly_mortgage_payment']:,.2f}"
        )
        st.write(f"**Monthly Maintenance:** CHF {buying['monthly_maintenance']:,.2f}")
        st.write(f"**Initial Monthly Cost:** CHF {buying['initial_monthly_cost']:,.2f}")
        st.write(f"**Final House Value:** CHF {buying['final_house_value']:,.2f}")
        st.write(f"**Final Equity:** CHF {buying['final_equity']:,.2f}")
        st.write(
            f"**Final Investment Portfolio:** CHF {buying['final_investment_portfolio']:,.2f}"
        )
        st.write(
            f"**Total Cost:** CHF {results['comparison']['buying_total_cost']:,.2f}"
        )

    with col2:
        st.subheader("Renting Scenario")
        renting = results["renting"]
        st.write(f"**Monthly Rent:** CHF {renting['monthly_rent']:,.2f}")
        st.write(f"**Initial Investment:** CHF {renting['initial_investment']:,.2f}")
        st.write(
            f"**Monthly Amortization Investment:** CHF {renting['monthly_amortization']:,.2f}"
        )
        st.write(f"**Amortization Period:** {renting['amortization_months']} months")
        st.write(
            f"**Final Portfolio Value:** CHF {renting['final_portfolio_value']:,.2f}"
        )
        st.write(
            f"**Total Cost:** CHF {results['comparison']['renting_total_cost']:,.2f}"
        )

# Create plots
st.header("📊 Visualizations")

buying = results["buying"]
renting = results["renting"]
months = simulation_years * 12

months_array = np.arange(1, months + 1)
years_array = months_array / 12

buying_equity = [w["equity"] for w in buying["wealth_progression"]]
buying_house_value = [w["house_value"] for w in buying["wealth_progression"]]
buying_monthly_cost = [w["monthly_cost"] for w in buying["wealth_progression"]]
buying_remaining_loan = [w["remaining_loan"] for w in buying["wealth_progression"]]
buying_monthly_investment = [
    w["monthly_investment"] for w in buying["wealth_progression"]
]
buying_total_wealth = [w["total_wealth"] for w in buying["wealth_progression"]]

renting_portfolio = [w["portfolio_value"] for w in renting["wealth_progression"]]
renting_monthly_cost = [w["monthly_cost"] for w in renting["wealth_progression"]]
renting_monthly_investment = [
    w["monthly_investment"] for w in renting["wealth_progression"]
]

buying_cumulative_cost = np.cumsum(buying_monthly_cost)
renting_cumulative_cost = np.cumsum(renting_monthly_cost)

# Create 2x2 plot
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle(
    f"Buy vs Rent Comparison - {simulation_years} Year Analysis",
    fontsize=16,
    fontweight="bold",
)

# Plot 1: Wealth/Equity Over Time
ax1 = axes[0, 0]
ax1.plot(
    years_array,
    np.array(buying_total_wealth) / 1000,
    label="Buying (Total Wealth)",
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

# Plot 4: Monthly Investment (Both Scenarios)
ax4 = axes[1, 1]
ax4.plot(
    years_array,
    buying_monthly_investment,
    label="Buying - Monthly Investment",
    linewidth=2,
    color="blue",
)
ax4.plot(
    years_array,
    renting_monthly_investment,
    label="Renting - Monthly Investment",
    linewidth=2,
    color="green",
)
ax4.axhline(y=0, color="red", linestyle="--", linewidth=1, alpha=0.5)
ax4.set_xlabel("Years", fontsize=12)
ax4.set_ylabel("Monthly Investment (CHF)", fontsize=12)
ax4.set_title(
    "Monthly Investment Amounts (Both Scenarios)", fontsize=14, fontweight="bold"
)
ax4.legend(loc="upper right")
ax4.grid(True, alpha=0.3)

plt.tight_layout()
st.pyplot(fig)

# Footer
st.markdown("---")
st.markdown(
    """
### Data Sources
- **ETF Yield:** MSCI World 10.78% (2009-2025) - [iShares](https://www.ishares.com/ch/privatkunden/de/produkte/251882/ishares-msci-world-ucits-etf-acc-fund)
- **House Price Appreciation:** 3.73% average (2017-2025) - [Swiss Federal Statistical Office](https://www.bfs.admin.ch/bfs/de/home/statistiken/preise/immobilienpreise.html)
- **Rent:** CHF 2,075 for 5 bedroom flat in Winterthur - [Swiss Federal Statistical Office](https://www.bfs.admin.ch/bfs/de/home/statistiken/bau-wohnungswesen/wohnungen.html)
- **Rent Increase:** 1.4% average (2005-2025) - [Swiss Federal Statistical Office](https://www.bfs.admin.ch/bfs/de/home/statistiken/preise/mieten/index.html)
"""
)
