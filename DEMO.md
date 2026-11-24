# Valuation Studio

Valuation Studio opens on an illustrative company so the first walkthrough can begin immediately. The sample financials and price are fictional. The company lookup supports market data for real tickers.

## Run the prototype

Use Python 3.13 from the project directory.

```sh
uv sync --locked
uv run python app.py
```

Open [localhost:8050](http://localhost:8050). See DEPLOY.md for the standard pip setup and hosting configuration.

## One-minute walkthrough

1. Open the app on the sample company's base valuation. Point out the model value, sample price, and implied difference.
2. Set the WACC override to 11% and press Tab. Watch the headline valuation and the outlined base cell move together.
3. Move the terminal growth slider. The grid compares each discount-rate and growth-rate combination using the same cash-flow forecast.
4. Open Valuation breakdown to inspect the assumptions and components. Download the CSV to see the snapshot of the current model and projected cash flows.
5. If you want to show a real ticker, analyze AAPL. Use Load sample model to switch back.

For the partner discussion, test a concrete workflow: would someone who values companies pay to get from a ticker to an explainable, exportable scenario faster?
