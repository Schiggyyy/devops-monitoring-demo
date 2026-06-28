import time
import random
import psycopg2

# Schwelle wie im Original: ueber 80 % -> WARNING (sonst OK).
WARNING_THRESHOLD = 80


def evaluate_status(cpu, ram):
    """Bewertet CPU/RAM zu OK oder WARNING (Logik wie im Original)."""
    if cpu > WARNING_THRESHOLD or ram > WARNING_THRESHOLD:
        return "WARNING"
    return "OK"


def generate_metric():
    """Erzeugt simulierte CPU-/RAM-Werte (wie im Original)."""
    cpu = round(random.uniform(5, 95), 2)
    ram = round(random.uniform(10, 90), 2)
    return cpu, ram


def get_connection():
    return psycopg2.connect(
        host="database",
        database="monitoring",
        user="demo",
        password="demo",
    )


def save_metric(conn, server_name, cpu, ram, status):
    """Schreibt einen Messwert in die Datenbank."""
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO metrics (server_name, cpu_usage, ram_usage, status)
            VALUES (%s, %s, %s, %s)
            """,
            (server_name, cpu, ram, status),
        )
        conn.commit()


def run(conn=None, interval=5):
    """Hauptschleife des Collectors. Laeuft nur beim direkten Start."""
    if conn is None:
        time.sleep(5)
        conn = get_connection()

    while True:
        cpu, ram = generate_metric()
        status = evaluate_status(cpu, ram)
        save_metric(conn, "demo-server-1", cpu, ram, status)
        print(f"Saved metric: CPU={cpu}, RAM={ram}, STATUS={status}")
        time.sleep(interval)


# Die Endlosschleife startet nur, wenn die Datei direkt ausgefuehrt wird.
# Beim Import (z. B. durch die Tests) passiert nichts -> testbar.
if __name__ == "__main__":
    run()