"""
Datenbank-Zugriff fuer den Processing-Service.
Gesamte PostgreSQL-Kommunikation gebuendelt, getrennt von der Bewertungslogik.
"""

import os
import time

import psycopg2
import psycopg2.extras


DB_CONFIG = {
    "host": os.getenv("DB_HOST", "database"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME", "monitoring"),
    "user": os.getenv("DB_USER", "demo"),
    "password": os.getenv("DB_PASSWORD", "demo"),
}


def connect(retries: int = 10, delay: float = 3.0):
    """Verbindung mit Retry - PostgreSQL ist beim Start oft noch nicht bereit."""
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            conn.autocommit = False
            print(f"[processing] DB-Verbindung hergestellt (Versuch {attempt})")
            return conn
        except psycopg2.OperationalError as error:
            last_error = error
            print(f"[processing] DB noch nicht erreichbar ({attempt}/{retries}) ...")
            time.sleep(delay)
    raise RuntimeError(f"Keine Datenbankverbindung moeglich: {last_error}")


# --- Metriken -------------------------------------------------------------

def fetch_unprocessed(conn, limit: int = 100):
    """Liest noch nicht verarbeitete Rohmetriken (processed = FALSE)."""
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            """
            SELECT id, server_name, cpu_usage, ram_usage, created_at
            FROM raw_metrics
            WHERE processed = FALSE
            ORDER BY id ASC
            LIMIT %s
            """,
            (limit,),
        )
        return cur.fetchall()


def store_processed(conn, raw_row: dict, evaluation) -> None:
    """Bewertete Metrik speichern + Rohzeile markieren - in EINER Transaktion."""
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO processed_metrics
                (raw_id, server_name, cpu_usage, ram_usage,
                 cpu_status, ram_status, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                raw_row["id"],
                raw_row["server_name"],
                raw_row["cpu_usage"],
                raw_row["ram_usage"],
                evaluation.cpu_status,
                evaluation.ram_status,
                evaluation.status,
                raw_row["created_at"],
            ),
        )
        cur.execute(
            "UPDATE raw_metrics SET processed = TRUE WHERE id = %s",
            (raw_row["id"],),
        )
    conn.commit()


# --- Logs -----------------------------------------------------------------

def fetch_unprocessed_logs(conn, limit: int = 100):
    """Liest noch nicht bewertete Roh-Logs (processed = FALSE)."""
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            """
            SELECT id, source, message, created_at
            FROM raw_logs
            WHERE processed = FALSE
            ORDER BY id ASC
            LIMIT %s
            """,
            (limit,),
        )
        return cur.fetchall()


def store_processed_log(conn, raw_row: dict, level: str, status: str) -> None:
    """Bewertetes Log speichern + Rohzeile markieren - in EINER Transaktion."""
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO processed_logs
                (raw_id, source, level, status, message, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                raw_row["id"],
                raw_row["source"],
                level,
                status,
                raw_row["message"],
                raw_row["created_at"],
            ),
        )
        cur.execute(
            "UPDATE raw_logs SET processed = TRUE WHERE id = %s",
            (raw_row["id"],),
        )
    conn.commit()