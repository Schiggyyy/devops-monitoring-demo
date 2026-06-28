"""
Tests fuer die Bewertungslogik - brauchen KEINE Datenbank.
Ausfuehren mit: pytest
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evaluation import classify, evaluate, worse


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