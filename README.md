# buy_vs_rent
Investment yield of buying a house in Switzerland compared to renting

## Description

This Python script compares the financial outcomes of buying a house versus renting and investing the difference over a 20-year period. It calculates monthly costs and wealth accumulation for both scenarios.

## Features

- **Configurable Parameters**: All key financial parameters can be easily adjusted
- **Monthly Cost Calculation**: Detailed breakdown of monthly costs for both scenarios
- **Wealth Accumulation**: Tracks wealth buildup over 20 years
- **Comprehensive Comparison**: Side-by-side comparison with clear results

## Usage

Simply run the script:

```bash
python3 buy_vs_rent.py
```

## Parameters

The following parameters can be adjusted in the `main()` function:

- **house_price**: Total price of the house (CHF)
- **down_payment**: Down payment amount (CHF)
- **mortgage_interest_rate_annual**: Annual mortgage interest rate (as decimal, e.g., 0.03 for 3%)
- **mortgage_term_years**: Mortgage term in years (default: 20)
- **etf_monthly_yield**: Monthly ETF/investment yield (as decimal, e.g., 0.007 for 0.7%)
- **house_price_monthly_yield**: Monthly house price appreciation (as decimal, e.g., 0.002 for 0.2%)
- **house_maintenance_percent_annual**: Annual house maintenance cost as % of house price (as decimal, e.g., 0.01 for 1%)
- **monthly_rent**: Monthly rent payment (CHF)

## Example Output

The script provides a comprehensive analysis including:
- Input parameters summary
- Monthly costs for buying (mortgage + maintenance)
- Monthly costs for renting
- Final house value and equity after 20 years
- Final investment portfolio value after 20 years
- Comparison showing which option results in greater wealth

## Customization

To modify the parameters, edit the values in the `main()` function of `buy_vs_rent.py`:

```python
house_price = 1_000_000  # CHF 1M house
down_payment = 200_000  # CHF 200K (20% down payment)
mortgage_interest_rate_annual = 0.03  # 3% annual
# ... etc
```

## Methodology

### Buying Scenario
- Calculates fixed monthly mortgage payment using standard amortization formula
- Adds monthly maintenance costs (percentage of house value)
- Tracks house value appreciation over time
- Final wealth = house value - remaining mortgage balance

### Renting Scenario
- Uses down payment as initial investment
- Invests the difference between buying costs and rent each month
- Applies monthly ETF yield to growing portfolio
- Final wealth = investment portfolio value

## Requirements

- Python 3.6 or higher
- No external dependencies (uses only Python standard library)

# Buy vs Rent Calculator

A comprehensive calculator comparing the financial outcomes of buying a house versus renting and investing the difference.

## Features

- Compare buying vs renting scenarios over customizable time periods
- Track wealth accumulation including home equity and investment portfolios
- Interactive visualizations showing costs, wealth, and investments over time
- All parameters configurable through the UI

## Web App (GitHub Pages)

The calculator is available as a static web app that can be hosted on GitHub Pages using stlite.

### Deployment Instructions

1. Copy `index.html` and `streamlit_app.py` to your repository
2. Enable GitHub Pages in your repository settings
3. Select the branch and root folder containing `index.html`
4. Access your app at `https://yourusername.github.io/your-repo-name/`

### Local Development

To test the web app locally:

1. Start a simple HTTP server:
   ```bash
   python -m http.server 8000
   ```

2. Open your browser to `http://localhost:8000`

## Python Scripts

### Installation

```bash
pip install pyyaml matplotlib numpy
```

### Usage

Run the calculator:
```bash
python buy_vs_rent.py
```

Generate plots:
```bash
python plot_buy_vs_rent.py
```

### Configuration

Edit `config.yaml` to adjust default parameters:
- Simulation period
- House price and down payment
- Mortgage terms and interest rates
- Investment returns
- Maintenance costs
- Rent and rent increases

## Data Sources

- **ETF Yield:** MSCI World 10.78% (2009-2025)
- **House Price Appreciation:** 3.73% average (2017-2025) from Swiss Federal Statistical Office
- **Rent Increase:** 1.4% average (2005-2025) from Swiss Federal Statistical Office
