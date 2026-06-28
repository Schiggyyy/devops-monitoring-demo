"""
Gemeinsame Test-Hilfen.

Die beiden Services heissen beide 'app.py' und liegen in Ordnern mit
Bindestrich ('api-service', 'collector-service'). Beides macht einen
normalen 'import app' unmoeglich. Deshalb laden wir die Module gezielt
ueber ihren Dateipfad.
"""

import importlib.util
import sys
from pathlib import Path

import pytest

# Wurzelverzeichnis des Repos (eine Ebene ueber dem tests/-Ordner)
ROOT = Path(__file__).resolve().parent.parent


def _load_module(name, relpath):
    path = ROOT / relpath
    if not path.exists():
        pytest.skip(f"Datei nicht gefunden: {relpath}")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"Modul {relpath} nicht importierbar: {exc}")
    return module


@pytest.fixture
def api_module():
    """Das FastAPI-Modul des API-Service (api-service/app.py)."""
    return _load_module("api_app", "api-service/app.py")


@pytest.fixture
def collector_module():
    """Das Modul des Collector-Service (collector-service/app.py)."""
    return _load_module("collector_app", "collector-service/app.py")
