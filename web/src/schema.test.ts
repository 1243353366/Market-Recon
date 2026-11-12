import test from 'node:test';
import assert from 'node:assert/strict';

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

function resolveLicenseStatus(record: Partial<RecordItem>): string {
  const candidate = record.license_status ?? record.data?.license_status ?? record.metadata?.license_status ?? 'Review source terms';
  return String(candidate);
}

function buildSearchParams(options: { ticker?: string; query?: string; page: number; pageSize: number }): URLSearchParams {
  const params = new URLSearchParams({ page: String(options.page), page_size: String(options.pageSize) });
  if (options.ticker && options.ticker.trim()) {
    params.set('ticker', options.ticker.trim().toUpperCase());
  }
  if (options.query && options.query.trim()) {
    params.set('q', options.query.trim());
  }
  return params;
}

function calculateTotalPages(total: number, pageSize: number): number {
  return Math.max(1, Math.ceil(total / pageSize));
}

test('resolveLicenseStatus prioritizes top-level record license_status', () => {
  const item: RecordItem = {
    record_id: 'r1',
    source_id: 'sec',
    collection: 'filings',
    record_type: '10-K',
    source_name: 'SEC EDGAR',
    source_url: 'https://www.sec.gov',
    retrieved_at: '2026-01-01T00:00:00Z',
    license_status: 'public_domain',
    data: { license_status: 'data_domain' },
    metadata: { license_status: 'meta_domain' },
  };
  assert.equal(resolveLicenseStatus(item), 'public_domain');
});

test('resolveLicenseStatus falls back to data then metadata then default', () => {
  const withData: RecordItem = {
    record_id: 'r2',
    source_id: 'sec',
    collection: 'filings',
    record_type: '10-K',
    source_name: 'SEC EDGAR',
    source_url: 'https://www.sec.gov',
    retrieved_at: '2026-01-01T00:00:00Z',
    data: { license_status: 'commercial_reviewed' },
    metadata: {},
  };
  assert.equal(resolveLicenseStatus(withData), 'commercial_reviewed');

  const withMetadata: RecordItem = {
    ...withData,
    data: {},
    metadata: { license_status: 'custom_license' },
  };
  assert.equal(resolveLicenseStatus(withMetadata), 'custom_license');

  const withNeither: RecordItem = {
    ...withData,
    data: {},
    metadata: {},
  };
  assert.equal(resolveLicenseStatus(withNeither), 'Review source terms');
});

test('resolveLicenseStatus safely handles null or undefined data/metadata payloads', () => {
  const recordWithNulls = {
    record_id: 'r3',
    source_id: 'sec',
    collection: 'filings',
    record_type: '10-K',
    source_name: 'SEC EDGAR',
    source_url: 'https://www.sec.gov',
    retrieved_at: '2026-01-01T00:00:00Z',
    data: null as any,
    metadata: null as any,
  };
  assert.equal(resolveLicenseStatus(recordWithNulls), 'Review source terms');
});

test('buildSearchParams standardizes ticker uppercase and trims query', () => {
  const params = buildSearchParams({ ticker: '  nvda  ', query: '  semiconductor  ', page: 2, pageSize: 25 });
  assert.equal(params.get('ticker'), 'NVDA');
  assert.equal(params.get('q'), 'semiconductor');
  assert.equal(params.get('page'), '2');
  assert.equal(params.get('page_size'), '25');
});

test('calculateTotalPages calculates accurate upper bounds', () => {
  assert.equal(calculateTotalPages(0, 25), 1);
  assert.equal(calculateTotalPages(25, 25), 1);
  assert.equal(calculateTotalPages(26, 25), 2);
  assert.equal(calculateTotalPages(100, 25), 4);
});

test('parses shared record contract fixture and resolves license status', async () => {
  const fs = await import('node:fs');
  const path = await import('node:path');
  const fixturePath = path.resolve('../contracts/record_contract.json');
  const raw = fs.readFileSync(fixturePath, 'utf-8');
  const record: RecordItem = JSON.parse(raw);

  assert.equal(record.record_id, 'rec:sec:0000320193:20241101');
  assert.equal(record.ticker, 'AAPL');
  assert.equal(record.license_status, 'public_domain');
  assert.equal(resolveLicenseStatus(record), 'public_domain');
  assert.ok(typeof record.data === 'object' && record.data !== null);
  assert.ok(typeof record.metadata === 'object' && record.metadata !== null);
});
