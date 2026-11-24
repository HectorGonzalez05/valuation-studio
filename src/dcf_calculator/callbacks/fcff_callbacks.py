"""FCFF analysis callbacks for Dash application."""

from dash import Input, Output, State, ctx, html
import dash_bootstrap_components as dbc
from dcf_calculator.core.fcff import convert_api_data_to_dataframe
from dcf_calculator.data.yahoofin_api import get_fcff_dataframe
from dcf_calculator.data.edgar_api import get_edgar_fcff_dataframe
from dcf_calculator.data.demo_case import DEMO_TICKER, get_demo_cash_flows
import logging

logger = logging.getLogger(__name__)


def register_fcff_callbacks(app):
    """Register FCFF-related callbacks.
    
    Args:
        app: Dash application instance
    """
    
    @app.callback(Output("dataset-pill", "children"), Input("ticker-store", "data"))
    def describe_dataset(ticker: str | None) -> str:
        if ticker == DEMO_TICKER:
            return "Illustrative data"
        return f"{ticker} · Market data" if ticker else "No company loaded"

    @app.callback(
        [Output("fcff-data-store", "data"),
         Output("ticker-store", "data"),
         Output("sidebar-status", "children")],
        [Input("analyze-button", "n_clicks"), Input("load-demo-button", "n_clicks")],
        [State("ticker-input", "value"),
         State("data-source", "value"),
         State("historical-years", "value")],
        prevent_initial_call=True,
        running=[
            (Output("analyze-button", "disabled"), True, False),
            (Output("load-demo-button", "disabled"), True, False),
        ],
    )
    def analyze_company(
        n_clicks: int, demo_clicks: int, ticker: str | None, data_source: str, years: int
    ) -> tuple[dict | None, str | None, dbc.Alert | html.P]:
        """Analyze company and fetch FCFF data.
        
        Only runs when the Analyze button is clicked.
        No mystery reruns!
        """
        if ctx.triggered_id == "load-demo-button":
            return get_demo_cash_flows(years), DEMO_TICKER, html.P(
                "Sample model loaded.", className="sample-status"
            )

        ticker = (ticker or "").strip().upper()
        if ticker == DEMO_TICKER:
            return None, None, dbc.Alert("Use Load sample model to open DEMO.", color="warning")
        if not ticker:
            return None, None, dbc.Alert("Enter a stock ticker.", color="warning")
        
        logger.info(f"Analyzing {ticker} from {data_source}")
        
        try:
            # Fetch data based on source
            if data_source == "yahoo":
                raw_data = get_fcff_dataframe(ticker)
                df = convert_api_data_to_dataframe(raw_data, source='yahoo')
            else:  # edgar
                raw_data = get_edgar_fcff_dataframe(ticker, years)
                df = convert_api_data_to_dataframe(raw_data, source='edgar')
            
            if df is not None:
                df = df.dropna(subset=["fcff"]).sort_index().tail(years)

            if df is None or df.empty:
                return None, None, dbc.Alert(
                    f"No complete cash-flow data found for {ticker}.", color="danger"
                )
            
            # Convert DataFrame to dict for storage
            data_dict = df.to_dict('index')
            
            logger.info(f"Successfully loaded {len(df)} years of data for {ticker}")
            
            period = "year" if len(df) == 1 else "years"
            return data_dict, ticker, dbc.Alert(
                f"Loaded {len(df)} {period} of data for {ticker}.", color="success"
            )
                    
        except Exception as e:
            logger.error(f"Error analyzing {ticker}: {e}", exc_info=True)
            return (None, None,
                    dbc.Alert([
                        html.H6("Error loading data"),
                        html.P("Try again shortly or select another data source.", className="mb-0")
                    ], color="danger"))
