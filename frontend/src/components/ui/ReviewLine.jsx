export default function ReviewLine({ text, good = false }) {
  return (
    <div style={{ display: "flex", gap: 6, marginBottom: 6, alignItems: "flex-start" }}>
      <span style={{ color: good ? "#22c55e" : "#f87171", fontSize: 11, marginTop: 3 }}>●</span>
      <span style={{ color: "#aaa", fontFamily: "'DM Sans', sans-serif", fontSize: 13, lineHeight: 1.5 }}>
        {text}
      </span>
    </div>
  );
}
