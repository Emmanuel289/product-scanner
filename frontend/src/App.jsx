import { useState } from "react";
import ScanStep from "./components/ScanStep";
import LoadingState from "./components/LoadingState";
import ResultView from "./components/ResultView";

export default function App() {
  const [phase, setPhase] = useState("scan"); // scan | loading | result
  const [result, setResult] = useState(null);
  const [imageBase64, setImageBase64] = useState(null);

  const handleResult = (data, b64) => { setResult(data); setImageBase64(b64); setPhase("result"); };
  const handleLoading = (v) => { if (v) setPhase("loading"); };
  const handleReset = () => { setResult(null); setImageBase64(null); setPhase("scan"); };

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
            <div>
              <div style={{ fontFamily: "'DM Serif Display', serif", fontSize: 22, color: "#fff", letterSpacing: -0.5 }}>StyleCast</div>
              <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 11, color: "#444", letterSpacing: 2, textTransform: "uppercase" }}>Product Scanner</div>
            </div>
            {phase === "result" && (
              <div style={{ width: 8, height: 8, borderRadius: "50%", background: "#22c55e", boxShadow: "0 0 10px #22c55e" }} />
            )}
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
