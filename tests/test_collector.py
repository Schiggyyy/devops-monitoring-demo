"""
Tests fuer den Collector-Service (collector-service/app.py).

Geprueft wird die echte Logik des Collectors – ohne Datenbank, ohne
laufenden Container.
"""

import pytest


class TestEvaluateStatus:
    @pytest.mark.parametrize(
        "cpu, ram, expected",
        [
            (10, 10, "OK"),
            (50, 50, "OK"),
            (80, 80, "OK"),        # genau 80 ist noch OK (Schwelle ist "groesser als")
            (80.1, 10, "WARNING"),  # knapp ueber der Schwelle
            (81, 10, "WARNING"),    # CPU zu hoch
            (10, 81, "WARNING"),    # RAM zu hoch
            (95, 90, "WARNING"),    # beide hoch
        ],
    )
    def test_status_grenzwerte(self, collector_module, cpu, ram, expected):
        assert collector_module.evaluate_status(cpu, ram) == expected

    def test_nur_cpu_ueber_grenze(self, collector_module):
        assert collector_module.evaluate_status(85, 20) == "WARNING"

    def test_nur_ram_ueber_grenze(self, collector_module):
        assert collector_module.evaluate_status(20, 85) == "WARNING"


class TestGenerateMetric:
    def test_liefert_zwei_zahlen(self, collector_module):
        cpu, ram = collector_module.generate_metric()
        assert isinstance(cpu, float)
        assert isinstance(ram, float)

    def test_werte_liegen_in_erwarteten_bereichen(self, collector_module):
        # Mehrfach pruefen, da die Werte zufaellig erzeugt werden.
        for _ in range(200):
            cpu, ram = collector_module.generate_metric()
            assert 5 <= cpu <= 95
            assert 10 <= ram <= 90


class TestSaveMetric:
    def test_schreibt_in_die_datenbank(self, collector_module):
        # Einfaches Fake-Connection-Objekt, das die SQL-Aufrufe mitschreibt.
        calls = {}

        class FakeCursor:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def execute(self, sql, params):
                calls["sql"] = sql
                calls["params"] = params

        class FakeConn:
            def cursor(self):
                return FakeCursor()

            def commit(self):
                calls["committed"] = True

        collector_module.save_metric(FakeConn(), "demo-server-1", 50.0, 40.0, "OK")

        assert calls["params"] == ("demo-server-1", 50.0, 40.0, "OK")
        assert calls["committed"] is True
        assert "INSERT INTO metrics" in calls["sql"]
