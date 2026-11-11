# Market Recon

Market Recon is a public, open-source stock intelligence platform designed to help retail investors, students, and researchers evaluate public equities using transparent, reproducible market research.

The project brings together public financial data, daily market prices, SEC filings, earnings context, insider activity, management and governance signals, institutional ownership, technical indicators, and screening workflows into one research toolkit.

This repository is not a trading signal engine and does not provide investment advice. It is built for educational research, risk analysis, and transparent market intelligence.

## Mission

Offer a free, open-source alternative to fragmented research workflows by aggregating public-market intelligence into a transparent and reproducible platform.

## Major feature areas

- Daily stock price tracking and market snapshots
- Fundamental analysis and valuation context
- Technical indicators and trend monitoring
- Insider activity and governance monitoring
- Institutional ownership overview
- Earnings calendars and surprise analysis
- News and event intelligence
- Company and sector research templates
- Watchlists and investment screens
- Dashboard views for market monitoring

## Repository layout

```text
Market-Recon/
├── README.md
├── LICENSE
├── .gitignore
├── requirements.txt
├── pyproject.toml
├── market_recon/
│   ├── __init__.py
│   ├── cli.py
│   ├── config.py
│   ├── data_sources.py
│   ├── technical_analysis.py
│   ├── fundamentals.py
│   ├── screener.py
│   ├── watchlist.py
│   ├── news.py
│   └── reporting.py
├── dashboard/
│   └── app.py
├── scripts/
│   ├── generate_sample_data.py
│   └── seed_demo_data.py
├── data/
│   ├── README.md
│   ├── examples/
│   │   ├── sample_watchlist.json
│   │   ├── sample_stock_snapshot.json
│   │   ├── sample_fundamentals.json
│   │   ├── sample_news.json
│   │   └── sample_price_history.csv
│   └── outputs/
│       └── .gitkeep
├── docs/
│   ├── README.md
│   ├── methodology.md
│   ├── data-sources.md
│   ├── risk-disclosure.md
│   └── tutorials/
│       └── README.md
├── prices/
│   └── README.md
├── earnings/
│   └── README.md
├── filings/
│   └── README.md
├── insider-trades/
│   └── README.md
├── institutional-holdings/
│   └── README.md
├── news/
│   └── README.md
├── research/
│   └── README.md
├── company-analysis/
│   └/README.md
├── sector-analysis/
│   └── README.md
├── macroeconomics/
│   └── README.md
├── watchlists/
│   └── README.md
├── tools/
│   └── README.md
├── screeners/
│   └── README.md
├── valuation/
│   └── README.md
├── technical-analysis/
│   └── README.md
├── dashboards/
│   └── README.md
└── LICENSE
```

## Data sources and provenance

The platform is built around transparent sourcing. Planned and supported public sources include:

- SEC EDGAR
- Yahoo Finance
- Alpha Vantage
- Financial Modeling Prep
- Stooq
- Nasdaq public datasets
- FRED
- Trading Economics
- Public earnings transcript archives
- Investor relations pages

Each dataset should include a documented source, retrieval method, timestamp, and transformation notes so conclusions can be independently verified.

## Dashboard requirements

This repository includes a starter dashboard covering:

1. Market overview
2. Watchlist management
3. Valuation checklists
4. Technical indicator summaries
5. Public research report output

## Research workflow

1. Pull public data from trusted sources
2. Standardize and validate records
3. Build technical and fundamental context
4. Monitor company and sector catalysts
5. Generate a structured company report
6. Archive the source and transformation trail

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run the CLI

```bash
python -m market_recon.cli --symbol AAPL --period 180d --report
```

## Run the dashboard

```bash
streamlit run dashboard/app.py
```

## Generate demo data

```bash
python scripts/generate_sample_data.py
python scripts/seed_demo_data.py
```

## Example outputs

The project includes sample market, watchlist, fundamentals, and news data so the platform can be explored immediately without external credentials.

## Methodology standards

- Use only public information
- Preserve source provenance
- Separate raw and transformed data
- Distinguish reported data from estimated values
- Publish assumptions and limitations
- Encourage reproducible research

## Risk disclosure

Market Recon is built for educational and research purposes only. It is not designed as a trading recommendation engine or financial advisory service.

## Documentation

Additional guidance can be found in:

- docs/methodology.md
- docs/data-sources.md
- docs/risk-disclosure.md
- docs/tutorials/README.md

## License

This project is distributed under an MIT license. See the LICENSE file for details.

## Contributing

Contributions are welcome in these areas:

- Data collection and validation
- Research templates and analysis notes
- Dashboard design and UX
- Screener logic and watchlist features
- Documentation improvements
- Technical indicators and report generation

Please keep contributions transparent, reproducible, and grounded in public information.
