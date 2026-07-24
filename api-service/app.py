import os
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
        "https://frontend-service.internal.bluerock-d23a0e49.norwayeast.azurecontainerapps.io",
    ],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "database"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "monitoring"),
        user=os.getenv("DB_USER", "demo"),
        password=os.getenv("DB_PASSWORD", "demo"),
        sslmode="require"
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