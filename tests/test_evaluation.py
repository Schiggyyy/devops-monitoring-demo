"""
Tests fuer die Bewertungslogik - brauchen KEINE Datenbank.
Ausfuehren mit: pytest
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "processing-service"))

from evaluation import classify, evaluate, worse
from log_evaluation import evaluate_log, parse_level


def test_classify_ok():
    assert classify(10, 70, 90) == "OK"
    assert classify(69.9, 70, 90) == "OK"


def test_classify_warning_an_der_grenze():
    assert classify(70, 70, 90) == "WARNING"
    assert classify(89.9, 70, 90) == "WARNING"


def test_classify_critical_an_der_grenze():
    assert classify(90, 70, 90) == "CRITICAL"
    assert classify(100, 70, 90) == "CRITICAL"


def test_worse_nimmt_die_schlimmere_stufe():
    assert worse("OK", "WARNING") == "WARNING"
    assert worse("CRITICAL", "OK") == "CRITICAL"
    assert worse("WARNING", "WARNING") == "WARNING"


def test_evaluate_alles_ok():
    result = evaluate(cpu_usage=20, ram_usage=30)
    assert result.status == "OK"


def test_evaluate_warning_durch_cpu():
    result = evaluate(cpu_usage=75, ram_usage=30)
    assert result.cpu_status == "WARNING"
    assert result.ram_status == "OK"
    assert result.status == "WARNING"


def test_evaluate_critical_durch_ram():
    result = evaluate(cpu_usage=40, ram_usage=95)
    assert result.cpu_status == "OK"
    assert result.ram_status == "CRITICAL"
    assert result.status == "CRITICAL"


def test_evaluate_schlechterer_wert_gewinnt():
    result = evaluate(cpu_usage=80, ram_usage=92)
    assert result.status == "CRITICAL"

def test_parse_level_findet_ganze_woerter():
    assert parse_level("ERROR resource exhaustion") == "ERROR"
    assert parse_level("WARNING high load") == "WARNING"


def test_parse_level_ignoriert_teilwoerter():
    # "warned" darf nicht als WARNING erkannt werden
    assert parse_level("user was warned about quota") == "INFO"


def test_parse_level_schwerster_treffer_gewinnt():
    assert parse_level("INFO followed by ERROR") == "ERROR"


def test_parse_level_default_ist_info():
    assert parse_level("keine stufe enthalten") == "INFO"


def test_warn_wird_zu_warning_normalisiert():
    assert parse_level("WARN disk almost full") == "WARNING"


def test_evaluate_log_liefert_level_und_status():
    assert evaluate_log("ERROR crash") == ("ERROR", "CRITICAL")
    assert evaluate_log("INFO health check ok") == ("INFO", "OK")