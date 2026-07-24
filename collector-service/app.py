import os
import time
import random
import psycopg2

HEARTBEAT_FILE = "/tmp/heartbeat"

SERVERS = ["demo-server-1", "demo-server-2", "demo-server-3"]

# Pool an INFO-Meldungen fuer den Normalbetrieb
INFO_MESSAGES = [
    "request handled in 12ms",
    "health check ok",
    "scheduled job finished",
    "user login successful",
    "cache refreshed",
]


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "database"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "monitoring"),
        user=os.getenv("DB_USER", "demo"),
        password=os.getenv("DB_PASSWORD", "demo"),
        sslmode="require",
    )


def generate_metric():
    """Erzeugt simulierte CPU-/RAM-Werte. Rein -> testbar."""
    cpu = round(random.uniform(5, 95), 2)
    ram = round(random.uniform(10, 90), 2)
    return cpu, ram


def build_log_message(cpu, ram):
    """
    Baut eine rohe Log-Zeile passend zur Auslastung. Rein -> testbar.

    Der Collector bewertet hier NICHT - er erzeugt nur den Text. Das Level
    (WARNING/ERROR/INFO) steht zwar im Text, wird aber erst vom
    Processing-Service herausgeparst.
    """
    if cpu > 85 or ram > 85:
        return f"ERROR resource exhaustion: cpu={cpu}% ram={ram}%"
    if cpu > 70 or ram > 70:
        return f"WARNING high load: cpu={cpu}% ram={ram}%"
    return f"INFO {random.choice(INFO_MESSAGES)}"


def save_metric(conn, server_name, cpu, ram):
    """Schreibt eine ROHE Metrik (ohne Status) nach raw_metrics."""
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO raw_metrics (server_name, cpu_usage, ram_usage)
            VALUES (%s, %s, %s)
            """,
            (server_name, cpu, ram),
        )


def save_log(conn, source, message):
    """Schreibt eine ROHE Log-Zeile nach raw_logs."""
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO raw_logs (source, message) VALUES (%s, %s)",
            (source, message),
        )


def write_heartbeat():
    """Schreibt den aktuellen Zeitstempel in die Heartbeat-Datei fuer den Healthcheck."""
    with open(HEARTBEAT_FILE, "w") as f:
        f.write(str(time.time()))


def run(conn=None, interval=5):
    if conn is None:
        time.sleep(5)
        conn = get_connection()

    while True:
        for server in SERVERS:
            cpu, ram = generate_metric()
            message = build_log_message(cpu, ram)
            save_metric(conn, server, cpu, ram)
            save_log(conn, server, message)
        conn.commit()  # alle Server gemeinsam committen

        write_heartbeat()

        print(f"Saved metrics + logs for {len(SERVERS)} servers")
        time.sleep(interval)


# Die Endlosschleife startet nur, wenn die Datei direkt ausgefuehrt wird.
# Beim Import (z. B. durch Tests) passiert nichts -> testbar.
if __name__ == "__main__":
    run()