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

-- Verarbeitete Daten: das, was der Processing-Service erzeugt und die API liest
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