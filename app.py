"""DCF Calculator - Main Dash Application."""

import os

import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

from dcf_calculator.callbacks import register_callbacks
from dcf_calculator.data.demo_case import DEMO_TICKER, get_demo_cash_flows
from dcf_calculator.layouts.main_content import create_main_content, create_pane_navigation
from dcf_calculator.layouts.sidebar import create_sidebar


app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
    suppress_callback_exceptions=True,
    title="Valuation Studio",
    update_title=None,
)

app.layout = html.Div([
    html.Header(html.Div([
        html.Span(html.I(className="fa-solid fa-chart-simple", **{"aria-hidden": "true"}),
                  className="app-mark"),
        html.H1("Valuation Studio"),
        html.Span("Illustrative data", id="dataset-pill", className="dataset-pill", role="status"),
    ], className="workspace header-inner"), className="site-header"),
    html.Main([
        create_pane_navigation(),
        html.Section(create_main_content(), className="results-panel",
                     **{"aria-label": "Analysis workspace"}),
        html.Section(create_sidebar(), className="input-panel",
                     **{"aria-label": "Company lookup"}),
    ], className="workspace analysis-grid"),
    dcc.Store(id="fcff-data-store", data=get_demo_cash_flows(5)),
    dcc.Store(id="wacc-data-store"),
    dcc.Store(id="ticker-store", data=DEMO_TICKER),
    dcc.Store(id="projection-years", data=5),
    dcc.Store(id="terminal-growth-rate", data=2.5),
    dcc.Store(id="wacc-override", data=None),
    dcc.Download(id="valuation-download"),
])

register_callbacks(app)
server = app.server

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8050)), debug=False)
