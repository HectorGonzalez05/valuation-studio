# Run and deploy the DCF Calculator

Start from the repository root using Python 3.13.

```sh
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install .
python app.py
```

Open http://localhost:8050. You can also run `uv sync --locked` followed by `uv run python app.py`.

## Render

Push this source to a GitHub repository you control. In Render, create a Python Web Service and connect that repository. Use the repository root and the following settings.

- Python version: 3.13, as specified in `.python-version`
- Build command: `pip install .`
- Start command: `gunicorn app:server --bind 0.0.0.0:$PORT --timeout 120`

Keep provider credentials in the hosting service's environment settings. The optional SEC EDGAR LLM parser reads `ANTHROPIC_API_KEY`. Try Yahoo Finance first to verify the default path.

Before sharing the URL, run an analysis for AAPL, visit each analysis tab, change a valuation assumption, and repeat on a narrow screen. Verify that invalid tickers and provider failures show a readable message.
