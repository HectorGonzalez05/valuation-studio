"""Build the analysis view for DCF valuation sensitivity."""

from math import isfinite
from typing import Dict, List, Optional, Tuple

from dash import dcc, html
import pandas as pd
import plotly.graph_objects as go

from dcf_calculator.core.dcf_valuation import perform_dcf_valuation


OFFSETS = (-2, -1, 0, 1, 2)
BASE_INDEX = 2


def calculate_sensitivity_grid(
    projected_fcff: pd.DataFrame,
    wacc_data: Dict[str, float],
    terminal_growth: float,
    shares_outstanding: Optional[float],
) -> Tuple[List[float], List[float], List[List[Optional[float]]]]:
    """Calculate per-share valuations on a grid centered on the active model.

    Args:
        projected_fcff: Cash-flow forecast used by the active valuation.
        wacc_data: Discount rate and balance sheet inputs used by the model.
        terminal_growth: Active terminal growth rate expressed as a decimal.
        shares_outstanding: Outstanding shares for the per-share estimate.

    Returns:
        Discount rates, terminal growth rates, and a row-major grid of estimates.
    """
    discount_rates = [wacc_data["wacc"] + offset * 0.01 for offset in OFFSETS]
    growth_rates = [terminal_growth + offset * 0.005 for offset in OFFSETS]
    has_forecast = not projected_fcff.empty and (
        "projected_fcff" in projected_fcff or "fcff" in projected_fcff
    )
    has_shares = shares_outstanding is not None and isfinite(shares_outstanding) and shares_outstanding > 0
    rows = []
    for discount_rate in discount_rates:
        assumptions = {**wacc_data, "wacc": discount_rate}
        row = []
        for growth_rate in growth_rates:
            value = None
            valid_rates = (
                isfinite(discount_rate)
                and isfinite(growth_rate)
                and discount_rate > max(-1, growth_rate)
            )
            if valid_rates and has_forecast and has_shares:
                estimate = perform_dcf_valuation(
                    projected_fcff, assumptions, growth_rate, shares_outstanding
                )["value_per_share"]
                if estimate is not None and isfinite(estimate):
                    value = estimate
            row.append(value)
        rows.append(row)
    return discount_rates, growth_rates, rows


def create_valuation_sensitivity(
    projected_fcff: pd.DataFrame,
    wacc_data: Dict[str, float],
    terminal_growth: float,
    shares_outstanding: Optional[float],
    currency: str = "USD",
) -> html.Section:
    """Render a chart and accessible table for the active model's sensitivity.

    Args:
        projected_fcff: Cash-flow forecast used by the active valuation.
        wacc_data: Discount rate and balance sheet inputs used by the model.
        terminal_growth: Active terminal growth rate expressed as a decimal.
        shares_outstanding: Outstanding shares for the per-share estimate.
        currency: Currency code for the estimates.

    Returns:
        Sensitivity section with a responsive chart and its underlying data.
    """
    heading = html.H4("Valuation sensitivity", className="h5 mb-0")
    style = "sensitivity-panel card p-3 mb-4"
    discount_rates, growth_rates, values = calculate_sensitivity_grid(
        projected_fcff, wacc_data, terminal_growth, shares_outstanding
    )
    if not any(value is not None for row in values for value in row):
        message = "A valid valuation and share count are required for per-share scenarios."
        return html.Section([heading, html.P(message, className="text-muted mt-2 mb-0")], className=style)

    discount_labels = [f"{rate:.2%}" for rate in discount_rates]
    growth_labels = [f"{rate:.2%}" for rate in growth_rates]
    symbol = "$" if currency == "USD" else ""
    cell_values = [[_format_price(value, symbol) for value in row] for row in values]
    full_values = [[_format_price(value, symbol, precision=2) for value in row] for row in values]
    indices = list(range(len(OFFSETS)))
    hover = [
        [[discount_rate, growth_rate, full_values[r][c]] for c, growth_rate in enumerate(growth_labels)]
        for r, discount_rate in enumerate(discount_labels)
    ]
    figure = go.Figure(go.Heatmap(
        x=indices,
        y=indices,
        z=values,
        text=cell_values,
        texttemplate="%{text}",
        textfont={"size": 11, "color": "#102f37"},
        customdata=hover,
        hovertemplate=(
            "Discount rate: %{customdata[0]}<br>"
            "Terminal growth: %{customdata[1]}<br>"
            "Value per share: %{customdata[2]}<extra></extra>"
        ),
        hoverongaps=False,
        colorscale=[
            [0, "#f2f6fa"],
            [0.42, "#d4e8ee"],
            [0.72, "#a0d6d1"],
            [1, "#68bdb3"],
        ],
        xgap=3,
        ygap=3,
        showscale=False,
    ))
    base_value = values[BASE_INDEX][BASE_INDEX]
    if base_value is not None:
        figure.add_shape(
            type="rect",
            x0=BASE_INDEX - 0.48,
            x1=BASE_INDEX + 0.48,
            y0=BASE_INDEX - 0.48,
            y1=BASE_INDEX + 0.48,
            line={"color": "#125467", "width": 3},
        )
    figure.update_layout(
        margin={"l": 8, "r": 8, "t": 10, "b": 4},
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font={"family": "system-ui, sans-serif", "size": 12, "color": "#3a5367"},
        xaxis={
            "title": {"text": "Terminal growth"},
            "tickmode": "array",
            "tickvals": indices,
            "ticktext": growth_labels,
            "fixedrange": True,
            "automargin": True,
            "showgrid": False,
            "zeroline": False,
        },
        yaxis={
            "title": {"text": "Discount rate (WACC)"},
            "tickmode": "array",
            "tickvals": indices,
            "ticktext": discount_labels,
            "fixedrange": True,
            "automargin": True,
            "showgrid": False,
            "zeroline": False,
            "autorange": "reversed",
        },
    )
    table = html.Table([
        html.Caption(f"Estimated value per share ({currency})"),
        html.Thead(html.Tr([
            html.Th("Discount rate / terminal growth", scope="col"),
            *[html.Th(label, scope="col") for label in growth_labels],
        ])),
        html.Tbody([
            html.Tr([
                html.Th(label, scope="row"),
                *[
                    html.Td(f"{value} (base)" if r == c == BASE_INDEX else value)
                    for c, value in enumerate(full_values[r])
                ],
            ])
            for r, label in enumerate(discount_labels)
        ]),
    ], className="table table-sm mb-0")
    return html.Section([
        html.Div([
            heading,
            html.Span(f"Base {_format_price(base_value, symbol, precision=2)}",
                      className="badge rounded-pill text-bg-light border")
            if base_value is not None else None,
        ], className="d-flex flex-wrap align-items-center justify-content-between gap-2"),
        html.P(
            f"Estimated value per share ({currency}) across discount rates and terminal growth assumptions."
            + (" The outline marks your current model." if base_value is not None else ""),
            className="text-muted small mt-2 mb-1",
        ),
        html.Div(dcc.Graph(
            figure=figure,
            responsive=True,
            config={"displayModeBar": False, "scrollZoom": False},
            style={"height": "100%"},
        ), className="sensitivity-chart", role="group",
            **{"aria-label": "Heatmap of model-implied value per share"}),
        html.Details([
            html.Summary("View scenario values", className="small text-primary"),
            html.Div(table, className="table-responsive mt-2"),
        ], className="mt-1"),
    ], className=style)


def _format_price(value: Optional[float], symbol: str, precision: Optional[int] = None) -> str:
    if value is None:
        return "—"
    decimals = precision if precision is not None else (2 if abs(value) < 20 else 0)
    sign = "−" if value < 0 else ""
    return f"{sign}{symbol}{abs(value):,.{decimals}f}"
