"""Navigation and overview for the valuation workspace."""

from typing import Optional

from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from dcf_calculator.core.formatting import format_financial_number
from dcf_calculator.data.demo_case import DEMO_LABEL, DEMO_TICKER


PANES = {
    "overview": ("Overview", "fa-border-all", ""),
    "fcff-tab": ("Cash Flow", "fa-chart-line", "Review historical free cash flow and its components."),
    "wacc-tab": ("Cost of Capital", "fa-scale-balanced", "Compare discount rates and cost-of-equity methods."),
    "dcf-tab": ("Scenario Studio", "fa-sliders", "Adjust assumptions and estimate fair value per share."),
}


def create_pane_navigation() -> html.Nav:
    """Return the radio selector for the analysis panes."""
    return html.Nav([
        html.H2("Analysis", className="rail-title"),
        dbc.RadioItems(
            id="main-tabs",
            name="analysis-pane",
            value="dcf-tab",
            options=[
                {
                    "label": html.Span([
                        html.I(className=f"fa-solid {icon}", **{"aria-hidden": "true"}),
                        html.Span(label),
                    ], className="rail-option"),
                    "value": value,
                }
                for value, (label, icon, _) in PANES.items()
            ],
            className="pane-navigation",
            input_class_name="rail-input",
            label_class_name="rail-label",
        ),
    ], className="pane-rail", **{"aria-label": "Analysis panes"})


def create_main_content() -> dcc.Loading:
    """Return the workspace content with loading feedback."""
    return dcc.Loading(
        html.Div(id="tab-content", children=create_empty_pane("dcf-tab")),
        target_components={"tab-content": "children"},
        delay_show=250,
        color="#78e2cb",
        overlay_style={"visibility": "visible", "opacity": 0.5},
    )


def create_overview(
    ticker: Optional[str], cash_flows: Optional[dict[str, dict[str, float]]]
) -> html.Div:
    """Return the overview with historical cash flow and links to each analysis."""
    return html.Div([
        html.Section([
            html.Div([
                html.H2("Valuation overview", className="workspace-title"),
                html.Span(DEMO_LABEL if ticker == DEMO_TICKER else ticker,
                          className="ticker-badge") if ticker else None,
            ], className="overview-heading"),
            _cash_flow_preview(cash_flows) if ticker and cash_flows else _empty_chart(),
        ], className="overview-panel"),
        html.Div([
            html.Button([
                html.Span(html.I(className=f"fa-solid {icon}", **{"aria-hidden": "true"}),
                          className="shortcut-icon"),
                html.Span(label, className="shortcut-title"),
                html.Span(description, className="shortcut-description"),
            ], id={"type": "pane-shortcut", "value": value}, type="button",
                n_clicks=0, className="pane-shortcut")
            for value, (label, icon, description) in PANES.items()
            if value != "overview"
        ], className="shortcut-grid"),
    ], className="overview")


def create_empty_pane(active_pane: str) -> html.Section:
    """Return the chosen pane's introduction before data is loaded."""
    label, icon, description = PANES[active_pane]
    return html.Section([
        html.H2(label, className="workspace-title"),
        html.Div([
            html.I(className=f"fa-solid {icon} empty-icon", **{"aria-hidden": "true"}),
            html.P(description, className="empty-title"),
            html.P("Enter a stock ticker and select Analyze Company to get started.",
                   className="empty-copy"),
        ], className="chart-empty"),
    ], className="overview-panel")


def _empty_chart() -> html.Div:
    return html.Div([
        html.I(className="fa-solid fa-chart-line empty-icon", **{"aria-hidden": "true"}),
        html.H3("Historical free cash flow", className="empty-title"),
        html.P("Enter a stock ticker and select Analyze Company to load its cash-flow history.",
               className="empty-copy"),
    ], className="chart-empty")


def _cash_flow_preview(cash_flows: dict[str, dict[str, float]]) -> html.Div:
    history = sorted(cash_flows.items())
    years = [year for year, _ in history]
    values = [row["fcff"] for _, row in history]
    figure = go.Figure(go.Scatter(
        x=years,
        y=values,
        mode="lines+markers",
        line={"color": "#78e2cb", "width": 3},
        marker={"size": 8, "line": {"width": 2, "color": "#101d2a"}},
        fill="tozeroy",
        fillcolor="rgba(120, 226, 203, 0.12)",
        customdata=[format_financial_number(value) for value in values],
        hovertemplate="%{x} · %{customdata}<extra></extra>",
    ))
    figure.update_layout(
        margin={"t": 12, "r": 16, "b": 30, "l": 12},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "system-ui, sans-serif", "color": "#c2d0dd", "size": 13},
        xaxis={"type": "category", "fixedrange": True, "automargin": True, "showgrid": False},
        yaxis={"tickprefix": "$", "gridcolor": "#2a3b4d", "zerolinecolor": "#64778a",
               "fixedrange": True, "automargin": True},
    )
    return html.Div([
        html.Div([
            html.Div([
                html.H3("Latest free cash flow", className="preview-label"),
                html.P(format_financial_number(values[-1]), className="preview-value"),
                html.P(f"Fiscal year {years[-1]}", className="preview-period"),
            ]),
            html.Div([
                html.H3("Average free cash flow", className="preview-label"),
                html.P(format_financial_number(sum(values) / len(values)), className="preview-value"),
                html.P(f"{len(values)} fiscal {'year' if len(values) == 1 else 'years'}",
                       className="preview-period"),
            ]),
        ], className="preview-metrics"),
        html.Div(
            dcc.Graph(
                figure=figure,
                config={"displayModeBar": False, "scrollZoom": False},
                responsive=True,
            ),
            className="overview-graph",
            role="group",
            **{"aria-label": "Historical free cash flow chart"},
        ),
    ], className="cash-flow-preview")
