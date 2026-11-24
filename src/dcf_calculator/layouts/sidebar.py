"""Company input pane for the DCF Calculator."""

from dash import dcc, html
import dash_bootstrap_components as dbc


def create_sidebar() -> html.Div:
    """Return the ticker, data source, and history inputs."""
    return html.Div([
        html.H2("Company lookup", className="panel-title"),
        dbc.Label("Stock ticker", html_for="ticker-input"),
        dbc.Input(
            id="ticker-input",
            type="text",
            placeholder="e.g., AAPL",
            value="AAPL",
            className="ticker-field",
        ),
        html.Fieldset([
            html.Legend("Data source"),
            dbc.RadioItems(
                id="data-source",
                options=[
                    {"label": "Yahoo Finance", "value": "yahoo"},
                    {"label": "SEC EDGAR", "value": "edgar"},
                ],
                value="yahoo",
            ),
        ], className="input-grouping"),
        html.Fieldset([
            html.Legend("Historical years"),
            dcc.Slider(
                id="historical-years",
                min=3,
                max=10,
                step=1,
                value=5,
                marks={i: str(i) for i in range(3, 11)},
            ),
        ], className="input-grouping history-control"),
        dbc.Button("Analyze Company", id="analyze-button", color="primary", className="w-100"),
        dbc.Button("Load sample model", id="load-demo-button", className="sample-button w-100"),
        html.Div(id="sidebar-status", role="status", className="analysis-status"),
    ])
