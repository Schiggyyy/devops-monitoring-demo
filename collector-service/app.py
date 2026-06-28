import time
import random
import psycopg2

time.sleep(5)

conn = psycopg2.connect(
    host="database",
    database="monitoring",
    user="demo",
    password="demo"
)

SERVER = "demo-server-1"

# Pool an INFO-Meldungen fuer den Normalbetrieb
INFO_MESSAGES = [
    "request handled in 12ms",
    "health check ok",
    "scheduled job finished",
    "user login successful",
    "cache refreshed",
]

while True:
    cpu = round(random.uniform(5, 95), 2)
    ram = round(random.uniform(10, 90), 2)

    # 1) Rohmetrik schreiben (ohne Status - das macht der Processing-Service)
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO raw_metrics (server_name, cpu_usage, ram_usage)
            VALUES (%s, %s, %s)
            """,
            (SERVER, cpu, ram)
        )

    # 2) Passende Log-Zeile erzeugen
    if cpu > 85 or ram > 85:
        message = f"ERROR resource exhaustion: cpu={cpu}% ram={ram}%"
    elif cpu > 70 or ram > 70:
        message = f"WARNING high load: cpu={cpu}% ram={ram}%"
    else:
        message = f"INFO {random.choice(INFO_MESSAGES)}"

    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO raw_logs (source, message) VALUES (%s, %s)",
            (SERVER, message)
        )

    conn.commit()
    print(f"Saved metric (CPU={cpu}, RAM={ram}) and log: {message}")
    time.sleep(5)