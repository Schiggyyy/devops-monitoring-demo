"""
Tests fuer den API-Service (api-service/app.py).

Es wird die echte FastAPI-App getestet. Damit kein echtes PostgreSQL
laufen muss, wird die Datenbank-Verbindung durch ein Fake-Objekt ersetzt
(monkeypatch). So sind die Tests schnell und laufen ueberall.
"""

import pytest

try:
    from fastapi.testclient import TestClient
except ImportError:  # FastAPI/httpx nicht installiert
    TestClient = None


# --- Fake-Datenbank -------------------------------------------------------

class FakeCursor:
    def __init__(self, rows):
        self._rows = rows

    def execute(self, *args, **kwargs):
        pass  # SQL wird im Test nicht wirklich ausgefuehrt

    def fetchall(self):
        return self._rows


class FakeConnection:
    def __init__(self, rows):
        self._rows = rows

    def cursor(self, *args, **kwargs):
        return FakeCursor(self._rows)

    def close(self):
        pass


# --- Fixtures -------------------------------------------------------------

@pytest.fixture
def beispiel_daten():
    return [
        {
            "id": 1, "server_name": "demo-server-1", "cpu_usage": 50.0,
            "ram_usage": 40.0, "status": "OK", "created_at": "2024-01-01T10:00:00",
        },
        {
            "id": 2, "server_name": "demo-server-1", "cpu_usage": 91.0,
            "ram_usage": 30.0, "status": "WARNING", "created_at": "2024-01-01T10:00:05",
        },
    ]


@pytest.fixture
def client(api_module, monkeypatch, beispiel_daten):
    if TestClient is None:
        pytest.skip("fastapi/httpx nicht installiert (pip install -r requirements-dev.txt)")
    # Echte DB-Verbindung durch Fake ersetzen
    monkeypatch.setattr(api_module, "get_connection", lambda: FakeConnection(beispiel_daten))
    return TestClient(api_module.app)


# --- Tests ----------------------------------------------------------------

def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Monitoring API is running"}


def test_metrics_status_200(client):
    assert client.get("/metrics").status_code == 200


def test_metrics_liefert_liste(client):
    assert isinstance(client.get("/metrics").json(), list)


def test_metrics_hat_erwartete_felder(client):
    daten = client.get("/metrics").json()
    assert len(daten) == 2
    for feld in ("id", "server_name", "cpu_usage", "ram_usage", "status", "created_at"):
        assert feld in daten[0]


def test_metrics_inhalt_stimmt(client):
    daten = client.get("/metrics").json()
    assert daten[0]["server_name"] == "demo-server-1"
    assert daten[1]["status"] == "WARNING"
