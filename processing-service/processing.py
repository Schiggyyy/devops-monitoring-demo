"""
Processing-Service - Hauptschleife.

Ablauf: unverarbeitete Rohdaten lesen -> bewerten -> in processed_metrics
schreiben -> Rohzeile als verarbeitet markieren -> kurz warten -> wiederholen.

Der Service erzeugt selbst keine Daten. Er liest, was der Collector in
raw_metrics schreibt, und legt das bewertete Ergebnis in processed_metrics ab.
"""

import os
import time

import db
from evaluation import evaluate


INTERVAL = float(os.getenv("PROCESSING_INTERVAL", "5"))


def process_batch(conn) -> int:
    """Verarbeitet einen Schwung Rohdaten, gibt die Anzahl zurueck."""
    rows = db.fetch_unprocessed(conn)
    for row in rows:
        result = evaluate(row["cpu_usage"], row["ram_usage"])
        db.store_processed(conn, row, result)
        print(
            f"[processing] {row['server_name']}: "
            f"CPU {row['cpu_usage']}% -> {result.cpu_status}, "
            f"RAM {row['ram_usage']}% -> {result.ram_status} "
            f"=> {result.status}"
        )
    return len(rows)


def main() -> None:
    conn = db.connect()
    print("[processing] Service gestartet, warte auf Rohdaten ...")
    try:
        while True:
            try:
                process_batch(conn)
            except Exception as error:
                print(f"[processing] Fehler im Durchlauf: {error}")
                conn.rollback()
            time.sleep(INTERVAL)
    finally:
        conn.close()


if __name__ == "__main__":
    main()