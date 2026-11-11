# Public Signal Intelligence: Engineering, Research, Standards, Permits, and Regulation

Market Recon models public information as source-linked observations and supports deterministic review of changes across independent datasets. The aim is faster synthesis of lawful public information—not access to hidden or accidentally exposed data.

## New evidence domains

The signal schema now includes these additional categories:

| Domain | Signal kinds | Potential public sources | Key caveats |
|---|---|---|---|
| Engineering footprints | `open_source_activity`, `package_activity`, `cve_disclosure`, `technical_presentation` | GitHub, PyPI, npm, OSV, public conference programs/slides | Repository attribution can be wrong; downloads are not unique users or customers; CVEs describe vulnerabilities, not product momentum. |
| Academic-to-commercial research | `academic_research`, `university_licensing`, `patent_activity` | arXiv, SSRN, university technology-transfer pages, patent databases | Author affiliation and company linkage are uncertain; publication is not commercialization. Respect full-text licenses. |
| Standards | `standards_publication` | IEEE, W3C, IETF, consortium/public working-group records | Participation is not proof of control, adoption, or future revenue; distinguish drafts from approved standards. |
| Procurement and permitting | `permit_activity`, `local_agenda`, `government_award` | Local building/environmental permit portals, council agendas, USAspending, SAM.gov | Data schemas and update cadence vary by jurisdiction; permits and awards are not completed capacity or recognized revenue. |
| Regulatory mapping | `regulatory_comment`, `agency_docket`, `regulatory_action` | Regulations.gov, agency dockets, SEC/FDA/FCC/EPA/FERC releases | Clearly label proposed, active, final, stayed, and withdrawn actions; do not infer a beneficiary without evidence. |
| Litigation | `litigation_event` | Official court records and public case indexes | Dockets may be incomplete, delayed, or misattributed; filing allegations are not findings of fact. |
| Governance | `board_change` | SEC proxy statements and 8-Ks | Disclosures can be delayed; distinguish proposed nominees, elected directors, and departures. |

`market_recon/intelligence/sources.py` lists candidate sources and whether an adapter exists. A `planned_adapter` or terms-review entry does not imply that Market Recon currently collects that source.

## Evidence model and interpretation

Every `PublicSignal` requires a resolved entity ID, observed date, source name, and HTTPS citation URL. Include a baseline and period for any claimed increase/decrease. Keep raw source records separate from derived observations and retain the extraction method.

“Activity” should be operationalized per dataset rather than collapsed into an opaque score. Examples:

- Git commits: compare a documented time window and repository set; exclude mirrors, bots, forks, and unrelated projects where possible.
- Package downloads: compare provider-reported counts with the same endpoint and time windows; do not call downloads users or demand.
- Hiring: deduplicate roles, capture snapshots, and account for expired/syndicated postings.
- Permits and contracts: distinguish application, award, obligation, modification, construction, and completed capacity.
- Academic work: show author, institution, publication date, and explicit affiliation evidence.
- Standards: cite the public draft/meeting artifact and state its status at retrieval time.

## Cross-source research question

A query such as “Which firms have rising activity across several independent public indicators?” should return an evidence table, not a company ranking. Show each indicator, source, timestamp, baseline, entity-match method, confidence, and limitations. Count source families rather than duplicate feeds: five aggregators repeating one press release are one underlying event, not five independent confirmations.

The existing divergence detector finds mixed positive/negative observations; it is not an activity-growth detector or causal model. Before any “accelerating activity” workflow is considered, define each measure, comparison period, missing-data policy, entity-resolution confidence, independence rules, and validation set. Do not equate unusual activity with investment merit.

## Legal and ethical boundaries

Use documented APIs, official open data, licensed feeds, and genuinely public records. Respect provider terms, copyright, rate limits, privacy requirements, and retention limits. Do not search or ingest leaked documents, exposed cloud buckets, private-system artifacts, credentials, or data that appear accidentally public. Do not bypass login or access controls.

The output is for research and education only. It must not claim non-public knowledge, infer intent from a single indicator, or provide individualized investment recommendations.
