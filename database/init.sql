CREATE TABLE IF NOT EXISTS metrics (
    id SERIAL PRIMARY KEY,
    server_name VARCHAR(100),
    cpu_usage FLOAT,
    ram_usage FLOAT,
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);