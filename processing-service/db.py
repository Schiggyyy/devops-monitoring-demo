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