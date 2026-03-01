export default function PillTag({ text, variant = "default" }) {
  const styles = {
    default: { bg: "#1a1a1a", text: "#888",    border: "#2a2a2a" },
    good:    { bg: "#0d2e1a", text: "#4ade80", border: "#1a5c32" },
    warn:    { bg: "#2e1f0d", text: "#fbbf24", border: "#7a4a0a" },
  };
  const s = styles[variant];

  return (
    <span style={{
      display: "inline-block", padding: "4px 12px", borderRadius: 100,
      background: s.bg, border: `1px solid ${s.border}`,
      color: s.text, fontSize: 12, fontFamily: "'DM Sans', sans-serif",
    }}>
      {text}
    </span>
  );
}
