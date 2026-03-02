import { useState } from "react";
import ScanStep from "./components/ScanStep";
import LoadingState from "./components/LoadingState";
import ResultView from "./components/ResultView";
import { ArrowLeftIcon, ArrowRightIcon } from "./components/icons/Icons";

export default function App() {
  const [phase, setPhase] = useState("scan");
  const [result, setResult] = useState(null);
  const [imageBase64, setImageBase64] = useState(null);
  // history only tracks scan ↔ result — loading is transient
  const [history, setHistory] = useState(["scan"]);
  const [historyIndex, setHistoryIndex] = useState(0);

  const navigateTo = (newPhase) => {
    if (newPhase === "loading") {
      setPhase("loading");
      return;
    }
    const newHistory = [...history.slice(0, historyIndex + 1), newPhase];
    setHistory(newHistory);
    setHistoryIndex(newHistory.length - 1);
    setPhase(newPhase);
  };

  const goBack = () => {
    if (historyIndex === 0) return;
    const newIndex = historyIndex - 1;
    setHistoryIndex(newIndex);
    setPhase(history[newIndex]);
  };

  const goForward = () => {
    if (historyIndex >= history.length - 1) return;
    const newIndex = historyIndex + 1;
    setHistoryIndex(newIndex);
    setPhase(history[newIndex]);
  };

  const handleResult = (data, b64) => { setResult(data); setImageBase64(b64); navigateTo("result"); };
  const handleLoading = (v) => { if (v) navigateTo("loading"); };
  const handleReset = () => { setResult(null); setImageBase64(null); setHistory(["scan"]); setHistoryIndex(0); setPhase("scan"); };

  const canGoBack = historyIndex > 0 && phase !== "loading";
  const canGoForward = historyIndex < history.length - 1 && phase !== "loading";

  const navBtnStyle = (enabled) => ({
    background: "transparent",
    border: `1px solid ${enabled ? "#2a2a2a" : "transparent"}`,
    borderRadius: 8,
    padding: "6px 8px",
    color: enabled ? "#666" : "#2a2a2a",
    cursor: enabled ? "pointer" : "default",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    transition: "all 0.15s ease",
    pointerEvents: enabled ? "auto" : "none",
  });

  return (
    <>
      <link
        href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@400;500;600;700&display=swap"
        rel="stylesheet"
      />
      <div style={{ minHeight: "100vh", background: "#080808", display: "flex", justifyContent: "center", padding: "0 0 80px 0" }}>
        <div style={{ width: "100%", maxWidth: 420, padding: "0 16px" }}>

          {/* Top bar */}
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "28px 0 32px" }}>

            {/* Back + forward */}
            <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
              <button
                onClick={goBack}
                disabled={!canGoBack}
                style={navBtnStyle(canGoBack)}
                onMouseEnter={e => { if (canGoBack) e.currentTarget.style.borderColor = "#444"; }}
                onMouseLeave={e => { if (canGoBack) e.currentTarget.style.borderColor = "#2a2a2a"; }}
              >
                <ArrowLeftIcon />
              </button>
              <button
                onClick={goForward}
                disabled={!canGoForward}
                style={navBtnStyle(canGoForward)}
                onMouseEnter={e => { if (canGoForward) e.currentTarget.style.borderColor = "#444"; }}
                onMouseLeave={e => { if (canGoForward) e.currentTarget.style.borderColor = "#2a2a2a"; }}
              >
                <ArrowRightIcon />
              </button>
            </div>

            {/* Brand */}
            <div style={{ textAlign: "right" }}>
              <div style={{ fontFamily: "'DM Serif Display', serif", fontSize: 22, color: "#fff", letterSpacing: -0.5 }}>StyleCast</div>
              <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 11, color: "#444", letterSpacing: 2, textTransform: "uppercase" }}>Product Scanner</div>
            </div>
          </div>

          {/* Step indicator */}
          {phase !== "result" && (
            <div style={{ display: "flex", gap: 6, marginBottom: 28 }}>
              {["Scan", "Analyze", "Result"].map((label, i) => {
                const active = (phase === "scan" && i === 0) || (phase === "loading" && i === 1);
                const done = (phase === "loading" && i === 0) || (phase === "result" && i < 2);
                return (
                  <div key={label} style={{ flex: 1, display: "flex", flexDirection: "column", gap: 6 }}>
                    <div style={{ height: 2, borderRadius: 2, background: done || active ? "#6366f1" : "#1e1e1e", opacity: done ? 0.6 : 1 }} />
                    <span style={{ color: active ? "#aaa" : "#333", fontFamily: "'DM Sans', sans-serif", fontSize: 11, letterSpacing: 1 }}>{label}</span>
                  </div>
                );
              })}
            </div>
          )}

          {/* Content */}
          {phase === "scan" && <ScanStep onResult={handleResult} onLoading={handleLoading} />}
          {phase === "loading" && <LoadingState />}
          {phase === "result" && <ResultView data={result} imageBase64={imageBase64} onReset={handleReset} />}
        </div>
      </div>
    </>
  );
}