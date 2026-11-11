# Market Recon

Market Recon is a public, open-source stock intelligence platform built for transparent, reproducible market research using only publicly available information.

The goal is to create a free, OSINT-driven workflow for evaluating public companies across pricing, fundamentals, filings, insider activity, institutional ownership, earnings, and technical analysis.

This repository is designed as an educational research toolkit and archival platform. It does not provide investment advice and is not a trading signal engine.

## Mission

Provide retail investors and researchers with a transparent, free, and reproducible system for public market intelligence.

## What the platform covers

- Daily stock tracking and market snapshots
- Fundamentals and valuation analysis
- Technical indicators and trend monitoring
- Insider trade activity and governance signals
- Institutional ownership and 13F monitoring
- Earnings calendars, surprises, and transcript references
- News and event aggregation
- Company, sector, macro, and watchlist research
- Standardized company reports and dashboard views

## Repository structure

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
│   ├── reporting.py
│   └── __pycache__/
├── dashboard/
│   └── app.py
├── scripts/
│   └── generate_sample_data.py
├── data/
│   ├── examples/
│   │   ├── sample_watchlist.json
│   │   └── sample_stock_snapshot.json
│   └── README.md
├── docs/
│   ├── README.md
│   ├── methodology.md
│   ├── data-sources.md
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
│   └── README.md
├── sector-analysis/
│   └── README.md
├── macroeconomics/
│   └── README.md
├── watchlists/
│   └── README.md
├── tools/
│   └── README.md
├── screeners/
│   └/README.md
├── valuation/
│   └── README.md
├── technical-analysis/
│   └── README.md
├── dashboards/
│   └── README.md
└── docs/
```

## Core principles

- Transparency
- Reproducibility
- Open data sources
- Educational research
- Long-term investing
- Risk analysis

## Data sources

This project is intended to use public, verifiable data sources including:

- SEC EDGAR
- Yahoo Finance
- Alpha Vantage
- Financial Modeling Prep
- Stooq
- Nasdaq public datasets
- FRED
- Trading Economics
- Open earnings transcripts
- Investor relations pages

## Automation goals

- Refresh daily prices
- Download filing updates
- Maintain earnings calendars
- Refresh news feeds
- Generate research reports
- Archive source history for reproducibility

## Dashboard requirements

Planned dashboards include:

1. Market overview dashboard
2. Watchlist dashboard
3. Earnings dashboard
4. Insider activity dashboard
5. Valuation dashboard
6. Technical analysis dashboard

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run the example pipeline

```bash
python -m market_recon.cli --symbol AAPL --period 180d --report
```

## Launch the dashboard

```bash
streamlit run dashboard/app.py
```

## Example output

The repository includes example market data and a sample report generator so the project can be explored immediately without needing external credentials or a full data stack.

## Design philosophy

This project follows the vision of a free Bloomberg Terminal for retail investors, powered by public data and open-source tooling.

The work is intentionally focused on:

- Accuracy
- Transparency
- Repeatability
- Educational value

Every dataset should include its source and retrieval method so users can independently verify all conclusions.

## Disclaimer

Market Recon is not a trading signal platform and does not provide investment advice. All information is intended for educational and research use only.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contributing

Contributions are welcome in the areas of:

- Data collectors and validation checks
- Research report templates
- Dashboard UI improvements
- Documentation and methodology
- Technical indicators and analytics
- Screener logic and watchlist workflows
