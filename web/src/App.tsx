import { useEffect, useState } from 'react';

type RecordItem = {
  record_id: string;
  source_id: string;
  collection: string;
  record_type: string;
  source_name: string;
  source_url: string;
  retrieved_at: string;
  observed_at?: string | null;
  published_at?: string | null;
  entity_name?: string | null;
  ticker?: string | null;
  license_status?: string | null;
  data: Record<string, unknown>;
  metadata: Record<string, unknown>;
};

type Page = { items: RecordItem[]; page: number; page_size: number; total: number };
const API = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000';

export default function App() {
  const [records, setRecords] = useState<RecordItem[]>([]);
  const [ticker, setTicker] = useState('');
  const [query, setQuery] = useState('');
  const [page, setPage] = useState(1);
  const [pageInfo, setPageInfo] = useState<Page | null>(null);
  const [selected, setSelected] = useState<RecordItem | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const controller = new AbortController();
    const timer = window.setTimeout(async () => {
      setLoading(true);
      setError('');
      try {
        const params = new URLSearchParams({ page: String(page), page_size: '25' });
        if (ticker.trim()) params.set('ticker', ticker.trim().toUpperCase());
        if (query.trim()) params.set('q', query.trim());
        const response = await fetch(`${API}/api/records?${params}`, { signal: controller.signal });
        if (!response.ok) throw new Error(response.status === 503 ? 'Evidence database unavailable. Run ingestion first.' : `API request failed (${response.status})`);
        const result: Page = await response.json();
        setRecords(result.items);
        setPageInfo(result);
      } catch (reason) {
        if (reason instanceof DOMException && reason.name === 'AbortError') return;
        setError(reason instanceof Error ? reason.message : 'Unexpected request error');
      } finally {
        setLoading(false);
      }
    }, 180);
    return () => { window.clearTimeout(timer); controller.abort(); };
  }, [ticker, query, page]);

  return (
    <main className="shell">
      <header className="header">
        <div><p className="eyebrow">PUBLIC-SOURCE RESEARCH</p><h1>Market Recon</h1><p className="subtitle">Evidence Explorer</p></div>
        <span className="badge">Research only · Not investment advice</span>
      </header>
      <section className="panel filters" aria-label="Evidence filters">
        <label>Ticker<input value={ticker} onChange={(event) => { setTicker(event.target.value); setPage(1); }} placeholder="e.g. NVDA" /></label>
        <label>Search source, entity, or record type<input value={query} onChange={(event) => { setQuery(event.target.value); setPage(1); }} placeholder="Search indexed records" /></label>
      </section>
      {error && <div className="notice error" role="alert">{error}<p>Start the API with <code>uvicorn api.app:app --reload</code> and configure the SQLite database.</p></div>}
      {loading && <p className="muted" aria-live="polite">Loading evidence…</p>}
      <section className="panel" aria-label="Evidence records">
        <div className="table-heading"><h2>Source records</h2><span>{pageInfo ? `${pageInfo.total} records` : '—'}</span></div>
        {!loading && !error && records.length === 0 && <p className="empty">No records found. Ingest public source records, then refresh.</p>}
        {records.length > 0 && <div className="table-wrap"><table><thead><tr><th>Entity</th><th>Collection</th><th>Observation</th><th>Source</th><th>Evidence</th></tr></thead><tbody>
          {records.map((record) => <tr key={record.record_id}>
            <td><strong>{record.entity_name || record.ticker || 'Unresolved entity'}</strong>{record.ticker && <small>{record.ticker}</small>}</td>
            <td><span className="tag">{record.collection}</span><small>{record.record_type}</small></td>
            <td>{record.observed_at || record.published_at || 'Date unavailable'}</td>
            <td>{record.source_name}<small>Retrieved {record.retrieved_at}</small></td>
            <td><button className="link-button" onClick={() => setSelected(record)}>Inspect record</button></td>
          </tr>)}
        </tbody></table></div>}
        <div className="pagination"><button disabled={page <= 1 || loading} onClick={() => setPage((value) => value - 1)}>Previous</button><span>Page {page}{pageInfo ? ` of ${Math.max(1, Math.ceil(pageInfo.total / pageInfo.page_size))}` : ''}</span><button disabled={!pageInfo || page * pageInfo.page_size >= pageInfo.total || loading} onClick={() => setPage((value) => value + 1)}>Next</button></div>
      </section>
      {selected && <div className="modal-backdrop" role="presentation" onClick={() => setSelected(null)}><section className="modal" role="dialog" aria-modal="true" aria-labelledby="record-title" onClick={(event) => event.stopPropagation()}>
        <button className="close" onClick={() => setSelected(null)} aria-label="Close">×</button>
        <p className="eyebrow">{selected.source_id} / {selected.collection}</p><h2 id="record-title">{selected.entity_name || selected.record_type}</h2>
        <dl><dt>Record ID</dt><dd>{selected.record_id}</dd><dt>Observed</dt><dd>{selected.observed_at || 'Not specified'}</dd><dt>Retrieved</dt><dd>{selected.retrieved_at}</dd><dt>License status</dt><dd>{selected.license_status ?? selected.data.license_status ?? selected.metadata.license_status ?? 'Review source terms'}</dd></dl>
        <p><a href={selected.source_url} target="_blank" rel="noreferrer">Open cited source ↗</a></p>
        <h3>Normalized data</h3><pre>{JSON.stringify(selected.data, null, 2)}</pre>
        <h3>Metadata</h3><pre>{JSON.stringify(selected.metadata, null, 2)}</pre>
      </section></div>}
      <footer>Verify every finding against its original source. Public records can be delayed, incomplete, revised, or misattributed.</footer>
    </main>
  );
}
