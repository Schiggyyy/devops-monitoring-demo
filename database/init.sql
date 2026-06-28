-- ===========================================================================
-- Metriken
-- ===========================================================================

-- Rohdaten: das, was der Collector liefert (ohne Status)
CREATE TABLE IF NOT EXISTS raw_metrics (
    id          SERIAL PRIMARY KEY,
    server_name TEXT      NOT NULL,
    cpu_usage   REAL      NOT NULL,
    ram_usage   REAL      NOT NULL,
    created_at  TIMESTAMP NOT NULL DEFAULT NOW(),
    processed   BOOLEAN   NOT NULL DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_raw_metrics_unprocessed
    ON raw_metrics (processed)
    WHERE processed = FALSE;

-- Verarbeitete Daten: erzeugt vom Processing-Service, gelesen von der API
CREATE TABLE IF NOT EXISTS processed_metrics (
    id           SERIAL PRIMARY KEY,
    raw_id       INTEGER REFERENCES raw_metrics (id),
    server_name  TEXT      NOT NULL,
    cpu_usage    REAL      NOT NULL,
    ram_usage    REAL      NOT NULL,
    cpu_status   TEXT      NOT NULL,
    ram_status   TEXT      NOT NULL,
    status       TEXT      NOT NULL,
    created_at   TIMESTAMP NOT NULL,
    processed_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_processed_metrics_created
    ON processed_metrics (created_at DESC);

-- ===========================================================================
-- Logs
-- ===========================================================================

-- Roh-Logs: rohe Textzeilen, die der Collector meldet (ohne Level-Auswertung)
CREATE TABLE IF NOT EXISTS raw_logs (
    id          SERIAL PRIMARY KEY,
    source      TEXT      NOT NULL,
    message     TEXT      NOT NULL,
    created_at  TIMESTAMP NOT NULL DEFAULT NOW(),
    processed   BOOLEAN   NOT NULL DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_raw_logs_unprocessed
    ON raw_logs (processed)
    WHERE processed = FALSE;

-- Bewertete Logs: mit geparstem Level und Status, die API liest hieraus
CREATE TABLE IF NOT EXISTS processed_logs (
    id           SERIAL PRIMARY KEY,
    raw_id       INTEGER REFERENCES raw_logs (id),
    source       TEXT      NOT NULL,
    level        TEXT      NOT NULL,   -- INFO | WARNING | ERROR | CRITICAL
    status       TEXT      NOT NULL,   -- OK | WARNING | CRITICAL
    message      TEXT      NOT NULL,
    created_at   TIMESTAMP NOT NULL,
    processed_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_processed_logs_created
    ON processed_logs (created_at DESC);