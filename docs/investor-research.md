# Investor research library

The investor catalog and first-party reading priorities are in `data/investors/`. It covers 50 investors grouped by broad strategy family, with a starting source link and a research caution for each. The descriptions are educational summaries, not performance ratings or investment recommendations.

The Streamlit investor-library page supports name, strategy, and category search. The catalog is structured metadata; it does not yet contain or vectorize the investors' books, memos, letters, interviews, or 13F filings.

## RAG extension plan

- Build source adapters for documents that are publicly accessible and legally usable; keep canonical URLs, publication dates, author, document type, and retrieval timestamps.
- Add investor/entity identifiers only after resolving identity against primary sources. Names alone are ambiguous.
- Index licensed or public text with section-aware chunks, and attach source citations to every retrieved excerpt.
- Treat 13F-HR as delayed quarter-end holdings disclosures. Do not frame them as current positions, insider trades, or proof of an investor's present thesis.
- Keep numeric holdings/filing data in structured tables; use RAG to retrieve and explain the investor's own dated reasoning.
- Respect copyright, API terms, access controls, and rate limits. Storing a URL does not grant permission to download or republish full text.

## Start here

Prioritized original-source links and interpretation caveats are listed in `data/investors/README.md`. The catalog's profile links include secondary references; prefer primary writings and official filings when available.
