from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost",
    ],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

def get_connection():
    return psycopg2.connect(
        host="database",
        database="monitoring",
        user="demo",
        password="demo"
    )

@app.get("/")
def root():
    return {"message": "Monitoring API is running"}

@app.get("/metrics")
def get_metrics():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT id, server_name, cpu_usage, ram_usage,
               cpu_status, ram_status, status, created_at
        FROM processed_metrics
        ORDER BY created_at DESC
        LIMIT 20
    """)

    data = cur.fetchall()
    conn.close()
    return data

@app.get("/logs")
def get_logs():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT id, source, level, status, message, created_at
        FROM processed_logs
        ORDER BY created_at DESC
        LIMIT 30
    """)

    data = cur.fetchall()
    conn.close()
    return data