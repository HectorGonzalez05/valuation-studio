"""Scenario controls and valuation presentation."""

from dash import dcc, html
import dash_bootstrap_components as dbc

from dcf_calculator.core.formatting import format_financial_number


def create_valuation_assumptions(
    projection_years: int, terminal_growth: float, wacc_override: float | None
) -> html.Section:
    """Return the assumption controls for a scenario."""
    return html.Section([
        html.H4("Model assumptions", className="studio-section-title"),
        html.Div([
            html.Fieldset([
                html.Legend("Projection years"),
                dcc.Slider(
                    id="dcf-projection-years-slider", min=3, max=10, step=1,
                    value=projection_years, marks={3: "3", 5: "5", 7: "7", 10: "10"},
                    tooltip={"placement": "bottom"},
                ),
            ]),
            html.Fieldset([
                html.Legend("Terminal growth"),
                dcc.Slider(
                    id="dcf-terminal-growth-slider", min=1.0, max=5.0, step=0.1,
                    value=terminal_growth, marks={i: f"{i}%" for i in range(1, 6)},
                    tooltip={"placement": "bottom", "template": "{value}%"},
                ),
            ]),
            html.Div([
                dbc.Label("WACC override (%)", html_for="dcf-wacc-override-input"),
                dbc.Input(
                    id="dcf-wacc-override-input", type="number",
                    placeholder="Use modeled WACC", value=wacc_override,
                    min=1, max=30, step=0.1, debounce=True,
                ),
            ]),
        ], className="scenario-controls"),
    ], className="studio-card")


def create_valuation_header(
    ticker: str, currency: str, quote_currency: str, fair_value: float | None,
    market_price: float | None, sample: bool,
) -> html.Div:
    """Return the model headline and share-price comparison."""
    currency_label = f" ({currency})" if currency else ""
    quote_label = f" ({quote_currency})" if quote_currency else ""
    difference = None
    if currency == quote_currency and market_price and fair_value is not None:
        difference = (fair_value / market_price - 1) * 100
    gap_style = "gap-positive" if difference is not None and difference > 0 else ""
    if difference is not None and difference < 0:
        gap_style = "gap-negative"
    return html.Div([
        html.Div([
            html.H3("Scenario Studio", className="studio-title"),
            html.Div([
                html.Span(f"{ticker} · {'Sample company' if sample else 'DCF model'}",
                          className="studio-symbol"),
                html.Button([
                    html.I(className="fa-solid fa-download", **{"aria-hidden": "true"}),
                    "Export CSV",
                ], id="export-model-button", type="button", className="studio-export"),
            ], className="studio-actions"),
        ], className="studio-title-row"),
        html.Div([
            html.Div([
                html.H4(f"Fair value per share{currency_label}", className="studio-kpi-label"),
                html.P(_format_price(fair_value, currency), id="fair-value-per-share",
                       className="studio-fair-value"),
            ], className="studio-primary-kpi"),
            html.Div([
                html.H4(f"{'Sample price' if sample else 'Market price'}{quote_label}",
                        className="studio-kpi-label"),
                html.P(_format_price(market_price, quote_currency), className="studio-kpi"),
            ]),
            html.Div([
                html.H4("Implied difference", className="studio-kpi-label"),
                html.P(f"{difference:+.1f}%" if difference is not None else "—",
                       className=f"studio-kpi {gap_style}"),
            ]),
        ], className="studio-kpis"),
    ], className="studio-hero")


def create_valuation_breakdown(
    results: dict, projection_years: int, projection_growth: float, currency: str,
) -> html.Details:
    """Return an expandable summary of the valuation components."""
    values = [
        ("Enterprise value", results["enterprise_value"]),
        ("Equity value", results["equity_value"]),
        ("PV of projected cash flows", results["pv_operating_cash_flows"]),
        ("PV of terminal value", results["pv_terminal_value"]),
        ("Net debt", results["net_debt"]),
    ]
    return html.Details([
        html.Summary("Valuation breakdown"),
        html.Dl([
            html.Div([
                html.Dt(label),
                html.Dd(format_financial_number(value, currency=currency == "USD")),
            ])
            for label, value in values
        ], className="studio-breakdown"),
        html.P(
            f"{projection_years}-year forecast · {projection_growth:.1%} annual cash-flow growth "
            f"· {results['wacc']:.2%} WACC · {results['terminal_growth_rate']:.2%} terminal growth",
            className="studio-note",
        ),
    ], className="studio-card studio-details")


def _format_price(value: float | None, currency: str) -> str:
    if value is None:
        return "—"
    prefix = "$" if currency == "USD" else ""
    return f"{prefix}{value:,.2f}"
