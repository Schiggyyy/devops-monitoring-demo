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

while True:
    cpu = round(random.uniform(5, 95), 2)
    ram = round(random.uniform(10, 90), 2)

    if cpu > 80 or ram > 80:
        status = "WARNING"
    else:
        status = "OK"

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO metrics (server_name, cpu_usage, ram_usage, status)
            VALUES (%s, %s, %s, %s)
            """,
            ("demo-server-1", cpu, ram, status)
        )
        conn.commit()

    print(f"Saved metric: CPU={cpu}, RAM={ram}, STATUS={status}")
    time.sleep(5)