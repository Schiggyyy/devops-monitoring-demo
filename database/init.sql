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