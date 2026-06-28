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

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO raw_metrics (server_name, cpu_usage, ram_usage)
            VALUES (%s, %s, %s)
            """,
            ("demo-server-1", cpu, ram)
        )
        conn.commit()

    print(f"Saved raw metric: CPU={cpu}, RAM={ram}")
    time.sleep(5)