package main

import (
	"bufio"
	"crypto/subtle"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"time"
)

const maxRecordBytes = 1 << 20

type Record struct {
	RecordID      string          `json:"record_id"`
	SourceID      string          `json:"source_id"`
	Collection    string          `json:"collection"`
	RecordType    string          `json:"record_type"`
	SourceName    string          `json:"source_name"`
	SourceURL     string          `json:"source_url"`
	RetrievedAt   string          `json:"retrieved_at"`
	Data          json.RawMessage `json:"data"`
	ObservedAt    *string         `json:"observed_at,omitempty"`
	PublishedAt   *string         `json:"published_at,omitempty"`
	EntityID      *string         `json:"entity_id,omitempty"`
	EntityName    *string         `json:"entity_name,omitempty"`
	Ticker        *string         `json:"ticker,omitempty"`
	CIK           *string         `json:"cik,omitempty"`
	LicenseStatus string          `json:"license_status"`
	Metadata      json.RawMessage `json:"metadata,omitempty"`
}

type Gateway struct {
	token string
	path  string
	mu    sync.Mutex
}

func (r Record) validate() error {
	for name, value := range map[string]string{
		"record_id": r.RecordID, "source_id": r.SourceID, "collection": r.Collection,
		"record_type": r.RecordType, "source_name": r.SourceName, "retrieved_at": r.RetrievedAt,
		"license_status": r.LicenseStatus,
	} {
		if strings.TrimSpace(value) == "" {
			return fmt.Errorf("%s is required", name)
		}
	}
	if !strings.HasPrefix(r.SourceURL, "https://") {
		return errors.New("source_url must use https")
	}
	if !json.Valid(r.Data) {
		return errors.New("data must be valid JSON")
	}
	if len(r.Metadata) > 0 && !json.Valid(r.Metadata) {
		return errors.New("metadata must be valid JSON")
	}
	return nil
}

func (g *Gateway) authorize(next http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		provided := strings.TrimPrefix(r.Header.Get("Authorization"), "Bearer ")
		if subtle.ConstantTimeCompare([]byte(provided), []byte(g.token)) != 1 {
			http.Error(w, "unauthorized", http.StatusUnauthorized)
			return
		}
		if r.Method != http.MethodPost {
			w.Header().Set("Allow", http.MethodPost)
			http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
			return
		}
		next(w, r)
	}
}

func (g *Gateway) ingest(w http.ResponseWriter, r *http.Request) {
	r.Body = http.MaxBytesReader(w, r.Body, maxRecordBytes)
	defer r.Body.Close()
	decoder := json.NewDecoder(r.Body)
	decoder.DisallowUnknownFields()
	var record Record
	if err := decoder.Decode(&record); err != nil {
		http.Error(w, "invalid JSON record", http.StatusBadRequest)
		return
	}
	var trailing any
	if err := decoder.Decode(&trailing); err != io.EOF {
		http.Error(w, "request must contain exactly one JSON record", http.StatusBadRequest)
		return
	}
	if err := record.validate(); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	encoded, err := json.Marshal(record)
	if err != nil {
		http.Error(w, "could not encode record", http.StatusInternalServerError)
		return
	}
	g.mu.Lock()
	defer g.mu.Unlock()
	if err := os.MkdirAll(filepath.Dir(g.path), 0700); err != nil {
		log.Printf("create record dir: %v", err)
		http.Error(w, "record store unavailable", http.StatusInternalServerError)
		return
	}
	file, err := os.OpenFile(g.path, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0600)
	if err != nil {
		log.Printf("open record store: %v", err)
		http.Error(w, "record store unavailable", http.StatusInternalServerError)
		return
	}
	writer := bufio.NewWriter(file)
	_, writeErr := writer.Write(append(encoded, '\n'))
	if writeErr == nil {
		writeErr = writer.Flush()
	}
	closeErr := file.Close()
	if writeErr != nil || closeErr != nil {
		log.Printf("persist record: write=%v close=%v", writeErr, closeErr)
		http.Error(w, "record persistence failed", http.StatusInternalServerError)
		return
	}
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusAccepted)
	_, _ = fmt.Fprintf(w, "{\"accepted\":true,\"record_id\":%q}\n", record.RecordID)
}

func main() {
	token := os.Getenv("MARKET_RECON_INGEST_TOKEN")
	if len(token) < 24 {
		log.Fatal("MARKET_RECON_INGEST_TOKEN must be set and at least 24 characters")
	}
	path := os.Getenv("MARKET_RECON_RECORDS_PATH")
	if path == "" {
		path = "data/normalized-records.jsonl"
	}
	if err := os.MkdirAll(filepath.Dir(path), 0700); err != nil {
		log.Fatalf("create record directory: %v", err)
	}
	gateway := &Gateway{token: token, path: path}
	mux := http.NewServeMux()
	mux.HandleFunc("GET /health", func(w http.ResponseWriter, _ *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		_, _ = io.WriteString(w, "{\"status\":\"ok\"}\n")
	})
	mux.HandleFunc("/v1/records", gateway.authorize(gateway.ingest))
	address := os.Getenv("MARKET_RECON_LISTEN_ADDR")
	if address == "" {
		address = "127.0.0.1:8081"
	}
	server := &http.Server{Addr: address, Handler: mux, ReadHeaderTimeout: 5 * time.Second, ReadTimeout: 15 * time.Second, WriteTimeout: 15 * time.Second, IdleTimeout: 60 * time.Second, MaxHeaderBytes: 16 << 10}
	log.Printf("ingestion gateway listening on %s", address)
	log.Fatal(server.ListenAndServe())
}
