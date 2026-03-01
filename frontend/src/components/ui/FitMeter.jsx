export default function FitMeter({ score }) {
  const color = score >= 75 ? "#22c55e" : score >= 50 ? "#f59e0b" : "#ef4444";
  const radius = 50;
  const circumference = 2 * Math.PI * radius;

  return (
    <div style={{ textAlign: "center", padding: "24px 0" }}>
      <div style={{ position: "relative", width: 120, height: 120, margin: "0 auto 16px" }}>
        <svg width="120" height="120" style={{ transform: "rotate(-90deg)" }}>
          <circle cx="60" cy="60" r={radius} fill="none" stroke="#1e1e1e" strokeWidth="10" />
          <circle
            cx="60" cy="60" r={radius}
            fill="none" stroke={color} strokeWidth="10"
            strokeDasharray={circumference}
            strokeDashoffset={circumference * (1 - score / 100)}
            strokeLinecap="round"
            style={{
              transition: "stroke-dashoffset 1s cubic-bezier(.4,0,.2,1)",
              filter: `drop-shadow(0 0 6px ${color})`,
            }}
          />
        </svg>
        <div style={{
          position: "absolute", inset: 0,
          display: "flex", alignItems: "center", justifyContent: "center", flexDirection: "column",
        }}>
          <span style={{ fontSize: 28, fontWeight: 700, color, fontFamily: "'DM Serif Display', serif" }}>
            {score}%
          </span>
          <span style={{ fontSize: 10, color: "#666", fontFamily: "'DM Sans', sans-serif", letterSpacing: 1 }}>
            MATCH
          </span>
        </div>
      </div>
    </div>
  );
}
