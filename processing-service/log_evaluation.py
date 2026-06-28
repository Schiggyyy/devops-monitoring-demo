"""
Bewertung von Log-Zeilen - reine Logik, keine Datenbank.

Parst aus einer rohen Log-Zeile das Level (INFO/WARNING/ERROR/...) und mappt
es auf denselben Status wie bei den Metriken (OK/WARNING/CRITICAL). Das Level
wird wortweise gesucht, damit z. B. "warned" nicht faelschlich als WARNING gilt.
"""

import re

# Log-Level -> Gesamtstatus (gleiche Stufen wie bei den Metriken)
LEVEL_TO_STATUS = {
    "DEBUG": "OK",
    "INFO": "OK",
    "WARNING": "WARNING",
    "WARN": "WARNING",
    "ERROR": "CRITICAL",
    "CRITICAL": "CRITICAL",
    "FATAL": "CRITICAL",
}

# Vom schwersten zum leichtesten - der schwerste Treffer gewinnt.
SEVERITY_ORDER = ("CRITICAL", "FATAL", "ERROR", "WARNING", "WARN", "INFO", "DEBUG")


def parse_level(message: str) -> str:
    """Sucht das Log-Level als ganzes Wort in der Zeile. Default: INFO."""
    tokens = set(re.findall(r"[A-Za-z]+", message.upper()))
    for level in SEVERITY_ORDER:
        if level in tokens:
            return "WARNING" if level == "WARN" else level
    return "INFO"


def evaluate_log(message: str):
    """Gibt (level, status) zurueck."""
    level = parse_level(message)
    return level, LEVEL_TO_STATUS[level]