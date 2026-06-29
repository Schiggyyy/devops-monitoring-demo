"""
Tests fuer den Collector-Service (collector-service/app.py).

Geprueft wird die echte Logik – ohne Datenbank, ohne laufenden Container.
"""

import pytest


class TestClassifyLogLevel:
    @pytest.mark.parametrize(
        "cpu, ram, expected",
        [
            (50, 50, "INFO"),
            (70, 70, "INFO"),       # genau 70 ist noch INFO (Schwelle ist "groesser als")
            (70.1, 10, "WARNING"),  # knapp ueber 70
            (71, 10, "WARNING"),    # CPU hoch
            (10, 71, "WARNING"),    # RAM hoch
            (85, 85, "WARNING"),    # genau 85 ist noch WARNING
            (85.1, 10, "ERROR"),    # knapp ueber 85
            (86, 10, "ERROR"),      # CPU sehr hoch
            (10, 86, "ERROR"),      # RAM sehr hoch
        ],
    )
    def test_level_grenzwerte(self, collector_module, cpu, ram, expected):
        assert collector_module.classify_log_level(cpu, ram) == expected


class TestBuildLogMessage:
    def test_error_meldung(self, collector_module):
        msg = collector_module.build_log_message(90, 10)
        assert msg.startswith("ERROR resource exhaustion")
        assert "cpu=90%" in msg
        assert "ram=10%" in msg

    def test_warning_meldung(self, collector_module):
        msg = collector_module.build_log_message(75, 10)
        assert msg.startswith("WARNING high load")

    def test_info_meldung_kommt_aus_pool(self, collector_module):
        msg = collector_module.build_log_message(20, 20)
        assert msg.startswith("INFO ")
        # Der Text nach "INFO " muss aus dem definierten Pool stammen.
        assert msg[len("INFO "):] in collector_module.INFO_MESSAGES


class TestGenerateMetric:
    def test_liefert_zwei_zahlen(self, collector_module):
        cpu, ram = collector_module.generate_metric()
        assert isinstance(cpu, float)
        assert isinstance(ram, float)

    def test_werte_in_erwarteten_bereichen(self, collector_module):
        for _ in range(200):
            cpu, ram = collector_module.generate_metric()
            assert 5 <= cpu <= 95
            assert 10 <= ram <= 90


class TestSaveFunctions:
    def _fake_conn(self, calls):
        class FakeCursor:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def execute(self, sql, params):
                calls.append((sql, params))

        class FakeConn:
            def cursor(self):
                return FakeCursor()

        return FakeConn()

    def test_save_raw_metric(self, collector_module):
        calls = []
        collector_module.save_raw_metric(self._fake_conn(calls), "demo-server-1", 50.0, 40.0)
        sql, params = calls[0]
        assert "INSERT INTO raw_metrics" in sql
        assert params == ("demo-server-1", 50.0, 40.0)

    def test_save_raw_log(self, collector_module):
        calls = []
        collector_module.save_raw_log(self._fake_conn(calls), "demo-server-1", "INFO test")
        sql, params = calls[0]
        assert "INSERT INTO raw_logs" in sql
        assert params == ("demo-server-1", "INFO test")