"""Fictional USD financial data for the calculator's offline example."""

from typing import Dict

from dcf_calculator.core.fcff import calculate_fcff_single_year

DEMO_TICKER = "@DEMO"
DEMO_LABEL = "DEMO"
DEMO_QUOTE = {
    "symbol": DEMO_LABEL,
    "currency": "USD",
    "currentPrice": 119.50,
    "sharesOutstanding": 500_000_000,
}
DEMO_FINANCIALS = {
    "market_cap": DEMO_QUOTE["currentPrice"] * DEMO_QUOTE["sharesOutstanding"],
    "total_debt": 8_700_000_000,
    "cash": 4_500_000_000,
    "interest_expense": 470_000_000,
}
DEMO_CAPM = {
    "risk_free_rate": 0.041,
    "market_risk_premium": 0.056,
    "beta": 1.08,
}

_FCFF_COMPONENTS = (
    "ebit",
    "tax_expense",
    "depreciation_amortization",
    "capital_expenditures",
    "working_capital_change",
)
_STATEMENTS_IN_MILLIONS = (
    ("2016", (3150, 680, 340, 500, 105)),
    ("2017", (3330, 700, 350, 530, 115)),
    ("2018", (3570, 735, 368, 555, 128)),
    ("2019", (3850, 795, 390, 604, 135)),
    ("2020", (3770, 760, 405, 590, 115)),
    ("2021", (4320, 910, 475, 640, 145)),
    ("2022", (4480, 942, 510, 685, 155)),
    ("2023", (4710, 989, 560, 725, 175)),
    ("2024", (5020, 1050, 595, 800, 175)),
    ("2025", (5310, 1115, 630, 840, 185)),
)


def get_demo_cash_flows(years: int) -> Dict[str, Dict[str, float]]:
    """Return a fresh set of fictional cash-flow rows in dollars.

    Args:
        years: Number of recent fiscal years to include.

    Returns:
        Rows keyed by fiscal year with FCFF and its component line items.
    """
    if years <= 0:
        return {}

    history = {}
    for year, statement in _STATEMENTS_IN_MILLIONS[-years:]:
        row = {
            component: float(amount * 1_000_000)
            for component, amount in zip(_FCFF_COMPONENTS, statement)
        }
        row["fcff"] = calculate_fcff_single_year(**row)
        history[year] = row
    return history
