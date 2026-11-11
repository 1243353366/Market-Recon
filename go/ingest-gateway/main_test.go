package main

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func validRecord() Record {
	return Record{RecordID: "test:1", SourceID: "test", Collection: "filings", RecordType: "filing", SourceName: "Test Source", SourceURL: "https://example.org/doc", RetrievedAt: "2026-01-01T00:00:00Z", Data: json.RawMessage(`{"value":1}`), LicenseStatus: "reviewed"}
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
