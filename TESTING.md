# Testing

Das Projekt nutzt **pytest**. Getestet werden der **Collector-Service** und der
**API-Service**. Die Tests laufen lokal und automatisch bei jedem Git-Push
(GitHub Actions). Es ist **kein** laufendes PostgreSQL noetig – die Datenbank
wird in den Tests durch ein Fake-Objekt ersetzt.

## Was wird getestet

**Collector-Service** (`tests/test_collector.py`)
- `evaluate_status()` – Status OK/WARNING inkl. Grenzwerten (80 %)
- `generate_metric()` – erzeugte Werte liegen im erwarteten Bereich
- `save_metric()` – schreibt korrekt in die Datenbank (gemockt)

**API-Service** (`tests/test_api.py`)
- `GET /` – liefert die Statusmeldung
- `GET /metrics` – HTTP 200, Liste, korrekte Felder und Inhalte (DB gemockt)

## Dateien, die ins Repo gehoeren

| Datei | Hinweis |
|-------|---------|
| `collector-service/app.py` | **ersetzt** eure bisherige Datei (siehe unten) |
| `tests/conftest.py` | laedt die Service-Module |
| `tests/test_collector.py` | Collector-Tests |
| `tests/test_api.py` | API-Tests |
| `pytest.ini` | pytest-Konfiguration |
| `requirements-dev.txt` | Test-Abhaengigkeiten |
| `.github/workflows/tests.yml` | CI-Pipeline |

## Wichtig: angepasster Collector

`collector-service/app.py` wurde minimal umgebaut, damit er testbar ist:
- Die Status-Berechnung steckt jetzt in `evaluate_status(cpu, ram)`
- Datenerzeugung in `generate_metric()`, DB-Schreiben in `save_metric()`
- Die Endlosschleife laeuft nur noch beim direkten Start
  (`if __name__ == "__main__"`)

**Das Verhalten im Betrieb ist identisch** – der Container startet die Schleife
wie vorher. Ersetzt eure bisherige `collector-service/app.py` durch die neue.

## Lokal testen

```bash
pip install -r requirements-dev.txt
pytest -v
```

## Hochladen und automatisch testen

```bash
git add .
git commit -m "Tests fuer Collector und API + CI-Pipeline"
git push
```

Das Ergebnis erscheint im GitHub-Repo unter dem Reiter **Actions**.
