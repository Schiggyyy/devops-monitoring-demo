"""
Processing-Service - Hauptschleife.

Verarbeitet pro Durchlauf zwei Quellen:
    - Metriken: raw_metrics -> bewerten -> processed_metrics
    - Logs:     raw_logs    -> Level parsen -> processed_logs

Der Service erzeugt selbst keine Daten, er liest nur, was der Collector liefert.
"""

import os
import time

import db
from evaluation import evaluate
from log_evaluation import evaluate_log


INTERVAL = float(os.getenv("PROCESSING_INTERVAL", "5"))


def process_metric_batch(conn) -> int:
    rows = db.fetch_unprocessed(conn)
    for row in rows:
        result = evaluate(row["cpu_usage"], row["ram_usage"])
        db.store_processed(conn, row, result)
        print(
            f"[processing] METRIC {row['server_name']}: "
            f"CPU {row['cpu_usage']}% -> {result.cpu_status}, "
            f"RAM {row['ram_usage']}% -> {result.ram_status} => {result.status}"
        )
    return len(rows)


def process_log_batch(conn) -> int:
    rows = db.fetch_unprocessed_logs(conn)
    for row in rows:
        level, status = evaluate_log(row["message"])
        db.store_processed_log(conn, row, level, status)
        print(f"[processing] LOG {row['source']}: {level} => {status}")
    return len(rows)


def main() -> None:
    conn = db.connect()
    print("[processing] Service gestartet, warte auf Rohdaten und Logs ...")
    try:
        while True:
            try:
                process_metric_batch(conn)
                process_log_batch(conn)
            except Exception as error:
                print(f"[processing] Fehler im Durchlauf: {error}")
                conn.rollback()
            time.sleep(INTERVAL)
    finally:
        conn.close()


if __name__ == "__main__":
    main()