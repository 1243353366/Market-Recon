package main

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"testing"
)

func validRecord() Record {
	return Record{
		RecordID:      "test:1",
		SourceID:      "test",
		Collection:    "filings",
		RecordType:    "filing",
		SourceName:    "Test Source",
		SourceURL:     "https://example.org/doc",
		RetrievedAt:   "2026-01-01T00:00:00Z",
		Data:          json.RawMessage(`{"value":1}`),
		LicenseStatus: "reviewed",
	}
}

func TestIngestRequiresBearerAndPersistsJSONL(t *testing.T) {
	path := filepath.Join(t.TempDir(), "nested", "records.jsonl")
	g := &Gateway{token: strings.Repeat("x", 24), path: path}
	body, _ := json.Marshal(validRecord())
	request := httptest.NewRequest(http.MethodPost, "/v1/records", bytes.NewReader(body))
	request.Header.Set("Authorization", "Bearer "+g.token)
	response := httptest.NewRecorder()
	g.authorize(g.ingest)(response, request)
	if response.Code != http.StatusAccepted {
		t.Fatalf("expected 202, got %d: %s", response.Code, response.Body.String())
	}
	stored, err := os.ReadFile(path)
	if err != nil || !bytes.Contains(stored, []byte(`"record_id":"test:1"`)) {
		t.Fatalf("record not persisted: %v %s", err, stored)
	}
}

func TestIngestRejectsMissingAuthAndBadURL(t *testing.T) {
	g := &Gateway{token: strings.Repeat("x", 24), path: filepath.Join(t.TempDir(), "records.jsonl")}
	body, _ := json.Marshal(validRecord())
	request := httptest.NewRequest(http.MethodPost, "/v1/records", bytes.NewReader(body))
	response := httptest.NewRecorder()
	g.authorize(g.ingest)(response, request)
	if response.Code != http.StatusUnauthorized {
		t.Fatalf("expected 401, got %d", response.Code)
	}
	r := validRecord()
	r.SourceURL = "http://example.org/doc"
	if r.validate() == nil {
		t.Fatal("expected HTTP source URL validation error")
	}
}

func TestIngestRejectsUnknownFields(t *testing.T) {
	g := &Gateway{token: strings.Repeat("x", 24), path: filepath.Join(t.TempDir(), "records.jsonl")}
	body := `{"record_id":"x","source_id":"s","collection":"c","record_type":"t","source_name":"n","source_url":"https://example.org","retrieved_at":"now","data":{},"license_status":"reviewed","surprise":true}`
	request := httptest.NewRequest(http.MethodPost, "/v1/records", strings.NewReader(body))
	request.Header.Set("Authorization", "Bearer "+g.token)
	response := httptest.NewRecorder()
	g.authorize(g.ingest)(response, request)
	if response.Code != http.StatusBadRequest {
		t.Fatalf("expected 400, got %d", response.Code)
	}
}

func TestIngestRejectsMultipleTrailingRecords(t *testing.T) {
	g := &Gateway{token: strings.Repeat("x", 24), path: filepath.Join(t.TempDir(), "records.jsonl")}
	r1, _ := json.Marshal(validRecord())
	r2, _ := json.Marshal(validRecord())
	body := append(r1, r2...)
	request := httptest.NewRequest(http.MethodPost, "/v1/records", bytes.NewReader(body))
	request.Header.Set("Authorization", "Bearer "+g.token)
	response := httptest.NewRecorder()
	g.authorize(g.ingest)(response, request)
	if response.Code != http.StatusBadRequest {
		t.Fatalf("expected 400 for trailing records, got %d", response.Code)
	}
}

func TestIngestRejectsEmptyRequiredFields(t *testing.T) {
	requiredFields := []func(*Record){
		func(r *Record) { r.RecordID = "   " },
		func(r *Record) { r.SourceID = "" },
		func(r *Record) { r.Collection = "" },
		func(r *Record) { r.RecordType = "" },
		func(r *Record) { r.SourceName = "" },
		func(r *Record) { r.RetrievedAt = "" },
		func(r *Record) { r.LicenseStatus = "" },
	}
	for i, mutator := range requiredFields {
		r := validRecord()
		mutator(&r)
		if err := r.validate(); err == nil {
			t.Errorf("case %d: expected error for empty field", i)
		}
	}
}

func TestAuthorizeRejectsNonPostMethod(t *testing.T) {
	g := &Gateway{token: strings.Repeat("x", 24), path: filepath.Join(t.TempDir(), "records.jsonl")}
	request := httptest.NewRequest(http.MethodGet, "/v1/records", nil)
	request.Header.Set("Authorization", "Bearer "+g.token)
	response := httptest.NewRecorder()
	g.authorize(g.ingest)(response, request)
	if response.Code != http.StatusMethodNotAllowed {
		t.Fatalf("expected 405 Method Not Allowed, got %d", response.Code)
	}
	if response.Header().Get("Allow") != http.MethodPost {
		t.Fatalf("expected Allow: POST, got %s", response.Header().Get("Allow"))
	}
}

func TestConcurrentIngestAppendsSafely(t *testing.T) {
	path := filepath.Join(t.TempDir(), "records.jsonl")
	g := &Gateway{token: strings.Repeat("x", 24), path: path}
	var wg sync.WaitGroup
	count := 10
	for i := 0; i < count; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			r := validRecord()
			r.RecordID = string(rune('A' + id))
			body, _ := json.Marshal(r)
			req := httptest.NewRequest(http.MethodPost, "/v1/records", bytes.NewReader(body))
			req.Header.Set("Authorization", "Bearer "+g.token)
			rec := httptest.NewRecorder()
			g.authorize(g.ingest)(rec, req)
			if rec.Code != http.StatusAccepted {
				t.Errorf("concurrent ingest %d failed with code %d", id, rec.Code)
			}
		}(i)
	}
	wg.Wait()

	data, err := os.ReadFile(path)
	if err != nil {
		t.Fatalf("reading persisted file: %v", err)
	}
	lines := strings.Split(strings.TrimSpace(string(data)), "\n")
	if len(lines) != count {
		t.Fatalf("expected %d persisted records, found %d", count, len(lines))
	}
}

func TestIngestRejectsNonObjectDataAndMetadata(t *testing.T) {
	gateway := &Gateway{token: "valid-token-at-least-24-characters-long", path: filepath.Join(t.TempDir(), "records.jsonl")}
	handler := gateway.authorize(gateway.ingest)

	// String data
	body1 := `{"record_id":"1","source_id":"s","collection":"c","record_type":"r","source_name":"sn","source_url":"https://example.org","retrieved_at":"2026-01-01T00:00:00Z","license_status":"public_domain","data":"not an object"}`
	req1 := httptest.NewRequest(http.MethodPost, "/v1/records", strings.NewReader(body1))
	req1.Header.Set("Authorization", "Bearer valid-token-at-least-24-characters-long")
	rec1 := httptest.NewRecorder()
	handler(rec1, req1)
	if rec1.Code != http.StatusBadRequest || !strings.Contains(rec1.Body.String(), "data must be a JSON object") {
		t.Fatalf("expected 400 data must be a JSON object, got %d %s", rec1.Code, rec1.Body.String())
	}

	// Array metadata
	body2 := `{"record_id":"2","source_id":"s","collection":"c","record_type":"r","source_name":"sn","source_url":"https://example.org","retrieved_at":"2026-01-01T00:00:00Z","license_status":"public_domain","data":{},"metadata":[1,2,3]}`
	req2 := httptest.NewRequest(http.MethodPost, "/v1/records", strings.NewReader(body2))
	req2.Header.Set("Authorization", "Bearer valid-token-at-least-24-characters-long")
	rec2 := httptest.NewRecorder()
	handler(rec2, req2)
	if rec2.Code != http.StatusBadRequest || !strings.Contains(rec2.Body.String(), "metadata must be a JSON object") {
		t.Fatalf("expected 400 metadata must be a JSON object, got %d %s", rec2.Code, rec2.Body.String())
	}
}
