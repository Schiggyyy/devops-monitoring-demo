import React, { useEffect, useState } from "react";
import { Activity, Cpu, Database, Server, AlertTriangle, CheckCircle } from "lucide-react";
import LogPanel from "./LogPanel.jsx";

const API_URL = "http://localhost:8000/metrics";

function App() {
  const [metrics, setMetrics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [selectedServer, setSelectedServer] = useState("all");

  async function fetchMetrics() {
    try {
      const response = await fetch(API_URL);
      const data = await response.json();
      setMetrics(data);
      setLastUpdated(new Date().toLocaleTimeString("de-DE"));
    } catch (error) {
      console.error("Fehler beim Laden der Metriken:", error);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 5000);
    return () => clearInterval(interval);
  }, []);

  // Liste der vorhandenen Server dynamisch aus den Daten ableiten.
  const servers = [...new Set(metrics.map((item) => item.server_name))].sort();

  // Nach gewaehltem Server filtern ("all" = keine Filterung).
  const filtered =
    selectedServer === "all"
      ? metrics
      : metrics.filter((item) => item.server_name === selectedServer);

  const latest = filtered[0];

  const averageCpu =
    filtered.length > 0
      ? (filtered.reduce((sum, item) => sum + Number(item.cpu_usage), 0) / filtered.length).toFixed(1)
      : 0;

  const averageRam =
    filtered.length > 0
      ? (filtered.reduce((sum, item) => sum + Number(item.ram_usage), 0) / filtered.length).toFixed(1)
      : 0;

  const warningCount = filtered.filter((item) => item.status === "WARNING").length;

  return (
    <div style={styles.page}>
      <header style={styles.header}>
        <div>
          <h1 style={styles.title}>DevOps Monitoring Dashboard</h1>
          <p style={styles.subtitle}>
            Microservice-Demo mit Collector, PostgreSQL, FastAPI und React Frontend
          </p>
        </div>

        <div style={styles.statusBadge}>
          <Activity size={18} />
          <span>Live Demo</span>
        </div>
      </header>

      <div style={styles.filterBar}>
        <button
          style={{
            ...styles.filterButton,
            ...(selectedServer === "all" ? styles.filterButtonActive : {}),
          }}
          onClick={() => setSelectedServer("all")}
        >
          Alle Server
        </button>
        {servers.map((server) => (
          <button
            key={server}
            style={{
              ...styles.filterButton,
              ...(selectedServer === server ? styles.filterButtonActive : {}),
            }}
            onClick={() => setSelectedServer(server)}
          >
            {server}
          </button>
        ))}
      </div>

      <section style={styles.grid}>
        <DashboardCard
          icon={<Server size={28} />}
          title="Aktueller Server"
          value={
            selectedServer === "all"
              ? latest?.server_name || "Keine Daten"
              : selectedServer
          }
          description="Simulierte Monitoring-Quelle"
        />

        <DashboardCard
          icon={<Cpu size={28} />}
          title="Ø CPU-Auslastung"
          value={`${averageCpu}%`}
          description="Durchschnitt der letzten Messwerte"
        />

        <DashboardCard
          icon={<Database size={28} />}
          title="Ø RAM-Auslastung"
          value={`${averageRam}%`}
          description="Gespeichert in PostgreSQL"
        />

        <DashboardCard
          icon={warningCount > 0 ? <AlertTriangle size={28} /> : <CheckCircle size={28} />}
          title="Warnungen"
          value={warningCount}
          description="CPU oder RAM über Grenzwert"
          warning={warningCount > 0}
        />
      </section>

      <section style={styles.panel}>
        <div style={styles.panelHeader}>
          <div>
            <h2 style={styles.panelTitle}>Letzte Monitoring-Daten</h2>
            <p style={styles.panelSubtitle}>
              {selectedServer === "all"
                ? "Alle Server"
                : `Gefiltert: ${selectedServer}`}
              {" - Aktualisierung alle 5 Sekunden"}
              {lastUpdated && ` - zuletzt um ${lastUpdated}`}
            </p>
          </div>
        </div>

        {loading ? (
          <p style={styles.loading}>Daten werden geladen...</p>
        ) : (
          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.th}>ID</th>
                <th style={styles.th}>Server</th>
                <th style={styles.th}>CPU</th>
                <th style={styles.th}>RAM</th>
                <th style={styles.th}>Status</th>
                <th style={styles.th}>Zeitpunkt</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((item) => (
                <tr key={item.id} style={styles.tr}>
                  <td style={styles.td}>{item.id}</td>
                  <td style={styles.td}>{item.server_name}</td>
                  <td style={styles.td}>{Number(item.cpu_usage).toFixed(1)}%</td>
                  <td style={styles.td}>{Number(item.ram_usage).toFixed(1)}%</td>
                  <td style={styles.td}>
                    <span
                      style={{
                        ...styles.badge,
                        ...(item.status === "WARNING" ? styles.badgeWarning : styles.badgeOk),
                      }}
                    >
                      {item.status}
                    </span>
                  </td>
                  <td style={styles.td}>
                    {new Date(item.created_at).toLocaleString("de-DE")}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      <LogPanel />
    </div>
  );
}

function DashboardCard({ icon, title, value, description, warning }) {
  return (
    <div style={styles.card}>
      <div style={warning ? styles.cardIconWarning : styles.cardIcon}>{icon}</div>
      <div>
        <p style={styles.cardTitle}>{title}</p>
        <h3 style={styles.cardValue}>{value}</h3>
        <p style={styles.cardDescription}>{description}</p>
      </div>
    </div>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    background: "#0f172a",
    color: "#e5e7eb",
    fontFamily: "Arial, sans-serif",
    padding: "32px",
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "32px",
  },
  title: {
    fontSize: "34px",
    margin: 0,
  },
  subtitle: {
    color: "#94a3b8",
    marginTop: "8px",
  },
  statusBadge: {
    display: "flex",
    alignItems: "center",
    gap: "8px",
    background: "#1e293b",
    border: "1px solid #334155",
    borderRadius: "999px",
    padding: "10px 16px",
  },
  filterBar: {
    display: "flex",
    gap: "10px",
    marginBottom: "24px",
    flexWrap: "wrap",
  },
  filterButton: {
    padding: "8px 16px",
    borderRadius: "999px",
    border: "1px solid #334155",
    background: "#1e293b",
    color: "#94a3b8",
    cursor: "pointer",
    fontSize: "14px",
  },
  filterButtonActive: {
    background: "#2563eb",
    color: "#ffffff",
    borderColor: "#2563eb",
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(230px, 1fr))",
    gap: "20px",
    marginBottom: "28px",
  },
  card: {
    background: "#1e293b",
    border: "1px solid #334155",
    borderRadius: "18px",
    padding: "22px",
    display: "flex",
    gap: "16px",
    alignItems: "center",
    boxShadow: "0 10px 25px rgba(0,0,0,0.25)",
  },
  cardIcon: {
    background: "#2563eb",
    padding: "14px",
    borderRadius: "14px",
    display: "flex",
  },
  cardIconWarning: {
    background: "#f97316",
    padding: "14px",
    borderRadius: "14px",
    display: "flex",
  },
  cardTitle: {
    color: "#94a3b8",
    margin: 0,
    fontSize: "14px",
  },
  cardValue: {
    margin: "6px 0",
    fontSize: "28px",
  },
  cardDescription: {
    color: "#94a3b8",
    margin: 0,
    fontSize: "13px",
  },
  panel: {
    background: "#1e293b",
    border: "1px solid #334155",
    borderRadius: "18px",
    padding: "24px",
    boxShadow: "0 10px 25px rgba(0,0,0,0.25)",
  },
  panelHeader: {
    marginBottom: "18px",
  },
  panelTitle: {
    margin: 0,
    fontSize: "22px",
  },
  panelSubtitle: {
    marginTop: "6px",
    color: "#94a3b8",
  },
  loading: {
    color: "#94a3b8",
  },
  table: {
    width: "100%",
    borderCollapse: "collapse",
  },
  th: {
    textAlign: "left",
    padding: "12px",
    color: "#94a3b8",
    borderBottom: "1px solid #334155",
    fontSize: "14px",
  },
  tr: {
    borderBottom: "1px solid #334155",
  },
  td: {
    padding: "12px",
    fontSize: "14px",
  },
  badge: {
    padding: "6px 10px",
    borderRadius: "999px",
    fontSize: "12px",
    fontWeight: "bold",
  },
  badgeOk: {
    background: "#14532d",
    color: "#bbf7d0",
  },
  badgeWarning: {
    background: "#7c2d12",
    color: "#fed7aa",
  },
};

export default App;