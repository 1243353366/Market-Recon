# Market Recon

Market Recon is a public, open-source stock intelligence platform for retail investors, researchers, and students who want transparent, reproducible market research built around publicly available data.

The project aggregates public financial information, daily market prices, SEC filings, earnings reports, insider transactions, institutional holdings, market news, analyst sentiment, and technical indicators into a single research workflow.

This repository is designed as an educational research toolkit and public market intelligence archive. It does not provide investment advice or trading signals.

## Mission

Provide free, high-quality market intelligence using only public data sources and transparent research methodology.

## Principles

- Transparency
- Reproducibility
- Open data sources
- Educational research
- Long-term investing
- Risk analysis

## What this platform tracks

- Daily stock prices and market data
- Fundamental metrics and valuation signals
- Technical indicators and risk measures
- Insider transactions and governance activity
- Institutional ownership changes
- Earnings calendar and transcript intelligence
- Company, sector, and macroeconomic research
- News and event monitoring

## Supported data sources

- SEC EDGAR
- Yahoo Finance
- Alpha Vantage
- Financial Modeling Prep
- Stooq
- Nasdaq public datasets
- FRED
- Trading Economics
- Public earnings transcript sources
- Investor relations pages

## Research workflow

1. Collect raw public source data
2. Normalize values and source metadata
3. Validate data quality and provenance
4. Compute research metrics and indicators
5. Generate structured company reports
6. Publish dashboards and watchlists
7. Archive source snapshots and methodology notes

## Repository structure

```text
Market-Recon/
├── README.md
├── .gitignore
├── docs/
│   ├── README.md
│   ├── methodology.md
│   ├── data-sources.md
│   └── tutorials/
│       └── README.md
├── data/
│   └── README.md
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
│   └── README.md
├── valuation/
│   └── README.md
├── technical-analysis/
│   └── README.md
├── dashboards/
│   └── README.md
└── LICENSE
```

## Core feature areas

### Daily stock tracking

For each tracked stock, capture:

- Ticker
- Company name
- Sector and industry
- Market cap
- Daily open, high, low, close, volume
- 52-week high and low

### Fundamental analysis

Track:

- Revenue growth
- Earnings growth
- Cash flow
- Debt levels
- Margins
- ROE and ROA
- Free cash flow
- Valuation multiples

### Technical analysis

Compute:

- SMA
- EMA
- RSI
- MACD
- ATR
- VWAP
- Volume profiles
- Support and resistance levels

### Insider activity

Track:

- Insider buys
- Insider sales
- Director purchases
- Executive transactions

### Institutional ownership

Monitor:

- 13F filings
- New positions
- Position changes
- Major shareholders
- Fund concentration

### Earnings intelligence

Monitor:

- Upcoming earnings dates
- Historical earnings
- Revenue surprises
- EPS surprises
- Call transcripts

### News intelligence

Aggregate:

- Company, sector, and regulatory news
- M&A activity
- Product launches
- Executive changes

## Research templates

Generate standardized company reports with:

- Business overview
- Financial health
- Valuation analysis
- Technical position
- Investment thesis

## Dashboard requirements

Planned dashboards include:

1. Market overview dashboard
2. Watchlist dashboard
3. Earnings dashboard
4. Insider activity dashboard
5. Valuation dashboard
6. Technical analysis dashboard

## Automation goals

- Refresh daily prices
- Download new filings
- Update earnings calendars
- Refresh news feeds
- Generate research reports
- Maintain historical archives

## Documentation goals

This repository will include documentation for:

- Setup
- Data collection
- Data validation
- Research methodology
- Risk disclosures
- Contribution guidelines

## Design philosophy

This project is intentionally built to feel like a free Bloomberg Terminal for retail investors, powered by open-source tools and publicly available information.

It emphasizes:

- Accuracy
- Transparency
- Repeatability
- Educational value

Every dataset should include its source and retrieval method so users can independently verify conclusions.

## Disclaimer

Market Recon is not a trading signal platform and does not provide investment advice. All information is for educational and research purposes only.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contributing

Contributions are welcome in the form of:

- Data pipeline improvements
- Documentation
- Research templates
- Data validation logic
- Dashboard prototypes
- Quality-of-data checks

Please contribute with a focus on transparency, reproducibility, and open-source best practices.

## Status

This repository is in its initial scaffolding phase. The structure is set up to support a long-term data collection and research platform for public market intelligence.
