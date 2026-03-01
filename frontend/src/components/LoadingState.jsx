import { useState } from "react";

const STEPS = [
  "Reading packaging...",
  "Matching database...",
  "Analyzing ingredients...",
  "Building your result...",
];

export default function LoadingState() {
  const [step, setStep] = useState(0);

  useState(() => {
    const id = setInterval(() => setStep((s) => Math.min(s + 1, STEPS.length - 1)), 600);
    return () => clearInterval(id);
  });

  return (
    <div style={{ textAlign: "center", padding: "48px 0" }}>
      <div style={{ width: 60, height: 60, margin: "0 auto 24px", position: "relative" }}>
        <div style={{
          width: "100%", height: "100%", borderRadius: "50%",
          border: "3px solid #1e1e1e", borderTopColor: "#8b5cf6",
          animation: "spin 0.8s linear infinite",
        }} />
      </div>
      <div style={{ color: "#fff", fontFamily: "'DM Serif Display', serif", fontSize: 20, marginBottom: 8 }}>
        Scanning product
      </div>
      <div style={{ color: "#6366f1", fontFamily: "'DM Sans', sans-serif", fontSize: 14, transition: "all 0.3s" }}>
        {STEPS[step]}
      </div>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
