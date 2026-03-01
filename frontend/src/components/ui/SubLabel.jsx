export default function SubLabel({ children }) {
  return (
    <div style={{
      color: "#555", fontFamily: "'DM Sans', sans-serif",
      fontSize: 11, letterSpacing: 1.5,
      textTransform: "uppercase", marginBottom: 8,
    }}>
      {children}
    </div>
  );
}
