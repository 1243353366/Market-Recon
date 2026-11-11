## Shared data-source adapter layer

Added the exact adapter package layout, a normalized provenance-rich record schema, a common `SourceAdapter` protocol, and logical collections for SEC, FRED, USAspending, and Quiver. SEC/FRED/USAspending wrappers use the existing clients. Quiver is configurable from verified endpoint metadata rather than hard-coding undocumented API routes. See [docs/source-adapters.md](docs/source-adapters.md) and [market_recon/sources/README.md](market_recon/sources/README.md).
