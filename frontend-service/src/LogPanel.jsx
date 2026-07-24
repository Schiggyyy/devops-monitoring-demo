import React, { useEffect, useState } from "react";
import { FileText } from "lucide-react";

const LOGS_URL = "/api/logs";

const levelColors = {
  INFO: { bg: "#14532d", color: "#bbf7d0" },
  WARNING: { bg: "#7c2d12", color: "#fed7aa" },
  ERROR: { bg: "#7f1d1d", color: "#fecaca" },
  CRITICAL: { bg: "#7f1d1d", color: "#fecaca" },
};

function LogPanel() {
  const [logs, setLogs] = useState([]);

  async function fetchLogs() {
    try {
      const response = await fetch(LOGS_URL);
      setLogs(await response.json());
    } catch (error) {
      console.error("Fehler beim Laden der Logs:", error);
    }
  }

  useEffect(() => {
    fetchLogs();
    const interval = setInterval(fetchLogs, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <section style={s.panel}>
      <div style={s.header}>
        <FileText size={20} />
        <h2 style={s.title}>Server-Logs</h2>
        <span style={s.subtitle}>geparst und bewertet durch den Processing-Service</span>
      </div>

      <div style={s.list}>
        {logs.length === 0 ? (
          <p style={s.empty}>Noch keine Logs vorhanden ...</p>
        ) : (
          logs.map((log) => {
            const c = levelColors[log.level] || levelColors.INFO;
            return (
              <div key={log.id} style={s.row}>
                <span style={s.time}>
                  {new Date(log.created_at).toLocaleTimeString("de-DE")}
                </span>
                <span style={{ ...s.level, background: c.bg, color: c.color }}>
                  {log.level}
                </span>
                <span style={s.source}>{log.source}</span>
                <span style={s.message}>{log.message}</span>
              </div>
            );
          })
        )}
      </div>
    </section>
  );
}

const s = {
  panel: {
    background: "#1e293b",
    border: "1px solid #334155",
    borderRadius: "18px",
    padding: "24px",
    marginTop: "28px",
    boxShadow: "0 10px 25px rgba(0,0,0,0.25)",
  },
  header: { display: "flex", alignItems: "center", gap: "10px", marginBottom: "16px" },
  title: { margin: 0, fontSize: "22px" },
  subtitle: { color: "#94a3b8", fontSize: "13px" },
  list: { display: "flex", flexDirection: "column", gap: "6px", fontFamily: "monospace" },
  empty: { color: "#94a3b8" },
  row: {
    display: "grid",
    gridTemplateColumns: "90px 90px 130px 1fr",
    alignItems: "center",
    gap: "12px",
    padding: "8px 10px",
    borderRadius: "8px",
    background: "#0f172a",
    fontSize: "13px",
  },
  time: { color: "#94a3b8" },
  level: { padding: "3px 8px", borderRadius: "999px", fontSize: "11px", fontWeight: "bold", textAlign: "center" },
  source: { color: "#94a3b8" },
  message: { color: "#e5e7eb", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" },
};

export default LogPanel;