export default function OutcomeBadge({ outcome, large = false }) {
  const map = {
    "✅ Good match":        { bg: "#0d2e1a", border: "#1a5c32", text: "#4ade80", dot: "#22c55e", label: "Good Match" },
    "⚠️ Mixed match":       { bg: "#2e1f0d", border: "#7a4a0a", text: "#fbbf24", dot: "#f59e0b", label: "Mixed Match" },
    "⚠️ Use with caution":  { bg: "#2e1f0d", border: "#7a4a0a", text: "#fbbf24", dot: "#f59e0b", label: "Use with Caution" },
    "❌ Not recommended":   { bg: "#2e0d0d", border: "#7a1a1a", text: "#f87171", dot: "#ef4444", label: "Not Recommended" },
  };
  const style = map[outcome] || map["⚠️ Mixed match"];

  return (
    <div style={{
      display: "inline-flex", alignItems: "center", gap: 8,
      background: style.bg, border: `1px solid ${style.border}`,
      borderRadius: 100, padding: large ? "10px 20px" : "6px 14px",
    }}>
      <div style={{
        width: large ? 10 : 8, height: large ? 10 : 8,
        borderRadius: "50%", background: style.dot,
        boxShadow: `0 0 8px ${style.dot}`,
      }} />
      <span style={{
        color: style.text, fontFamily: "'DM Sans', sans-serif",
        fontWeight: 600, fontSize: large ? 16 : 13,
      }}>
        {style.label}
      </span>
    </div>
  );
}
