"""
Reine Bewertungslogik des Processing-Service.

Kennt KEINE Datenbank - bekommt nur Zahlen, gibt einen Status zurueck.
Dadurch vollstaendig per Unit-Test pruefbar, ohne laufende PostgreSQL.
"""

import os
from dataclasses import dataclass


# Schwellenwerte - ueber Umgebungsvariablen konfigurierbar.
CPU_WARNING = float(os.getenv("CPU_WARNING", "70"))
CPU_CRITICAL = float(os.getenv("CPU_CRITICAL", "90"))
RAM_WARNING = float(os.getenv("RAM_WARNING", "70"))
RAM_CRITICAL = float(os.getenv("RAM_CRITICAL", "90"))

# Rangfolge der Stufen, um den schlechteren Gesamtstatus zu bestimmen.
SEVERITY = {"OK": 0, "WARNING": 1, "CRITICAL": 2}


@dataclass
class Evaluation:
    cpu_status: str
    ram_status: str
    status: str  # Gesamtstatus = der schlechtere von CPU und RAM


def classify(value: float, warning: float, critical: float) -> str:
    """>= critical -> CRITICAL, >= warning -> WARNING, sonst OK."""
    if value >= critical:
        return "CRITICAL"
    if value >= warning:
        return "WARNING"
    return "OK"


def worse(status_a: str, status_b: str) -> str:
    """Gibt den schwerwiegenderen der beiden Status zurueck."""
    return status_a if SEVERITY[status_a] >= SEVERITY[status_b] else status_b


def evaluate(cpu_usage: float, ram_usage: float) -> Evaluation:
    """Bewertet eine Messung. Gesamtstatus = schlechterer der Einzelwerte."""
    cpu_status = classify(cpu_usage, CPU_WARNING, CPU_CRITICAL)
    ram_status = classify(ram_usage, RAM_WARNING, RAM_CRITICAL)
    return Evaluation(
        cpu_status=cpu_status,
        ram_status=ram_status,
        status=worse(cpu_status, ram_status),
    )