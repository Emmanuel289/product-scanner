import { useState } from "react";
import { API_URL, SKIN_TYPES } from "../constants";
import OutcomeBadge from "./ui/OutcomeBadge";
import FitMeter from "./ui/FitMeter";
import PillTag from "./ui/PillTag";
import SectionTitle from "./ui/SectionTitle";
import SubLabel from "./ui/SubLabel";
import ReviewLine from "./ui/ReviewLine";
import { RefreshIcon, ChevronRight } from "./icons/Icons";

// ─── Not Found state — shared between error and explicit not-found ────────────
function NotFound({ onReset, icon = "🔍" }) {
  return (
    <div style={{ textAlign: "center", padding: "48px 0" }}>
      <div style={{ fontSize: 48, marginBottom: 16 }}>{icon}</div>
      <div style={{ color: "#fff", fontFamily: "'DM Serif Display', serif", fontSize: 22, marginBottom: 8 }}>
        Product Not Found
      </div>
      <div style={{ color: "#666", fontFamily: "'DM Sans', sans-serif", fontSize: 14, marginBottom: 24 }}>
        The product couldn't be identified.
      </div>
      <button
        onClick={onReset}
        style={{ background: "#1a1a1a", border: "1px solid #333", borderRadius: 10, padding: "12px 20px", color: "#aaa", cursor: "pointer", fontFamily: "'DM Sans', sans-serif", display: "flex", alignItems: "center", gap: 8, margin: "0 auto" }}
      >
        <RefreshIcon /> Try again
      </button>
    </div>
  );
}

// ─── Main result view ─────────────────────────────────────────────────────────
export default function ResultView({ data, imageBase64, onReset }) {
  const [skinType, setSkinType] = useState(null);
  const [personalizedData, setPersonalizedData] = useState(null);
  const [personalizing, setPersonalizing] = useState(false);

  if (data.error || data.status?.includes("Product Not Found")) {
    return <NotFound onReset={onReset} icon={data.error ? "❌" : "🔍"} />;
  }

  // Use personalized data if available, otherwise use original scan result
  const activeData = personalizedData || data;
  const s = activeData.product_summary || activeData;
  const fitScore = s?.fit_score || null;
  const isPersonalized = s?.personalized === true;

  const handleSkinSelect = async (id) => {
    if (id === skinType) return;
    setSkinType(id);
    setPersonalizing(true);
    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          image_base64: imageBase64,
          user_profile: { skin_type: id, concerns: [], sensitive: false },
        }),
      });
      const result = await res.json();
      setPersonalizedData(result);
    } catch (err) {
      console.error("Personalization call failed:", err);
    } finally {
      setPersonalizing(false);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 0 }}>

      {/* ── Header ── */}
      <div style={{ marginBottom: 24 }}>
        {/* Brand + category pill on same row */}
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
          <div style={{
            color: "#666",
            fontFamily: "'DM Sans', sans-serif",
            fontSize: 12,
            letterSpacing: 2,
            textTransform: "uppercase",
          }}>
            {activeData.brand}
          </div>

          {s.category && (
            <>
              <div style={{ width: 3, height: 3, borderRadius: "50%", background: "#333" }} />
              <div style={{
                display: "inline-block",
                padding: "2px 10px",
                borderRadius: 100,
                background: "#1a1a1a",
                border: "1px solid #2a2a2a",
                color: "#555",
                fontSize: 11,
                fontFamily: "'DM Sans', sans-serif",
                letterSpacing: 1,
                textTransform: "uppercase",
              }}>
                {s.category}
              </div>
            </>
          )}
        </div>
        {/* Product name */}
        <div style={{
          color: "#fff",
          fontFamily: "'DM Serif Display', serif",
          fontSize: 26,
          lineHeight: 1.2,
        }}>
          {activeData.product_name}
        </div>
        <div>
          <OutcomeBadge outcome={activeData.status} large />
        </div>
      </div>

      {/* ── Fit meter (only after skin type selected) ── */}
      {isPersonalized && fitScore !== null && (
        <div style={{ background: "#0d0d0d", border: "1px solid #1e1e1e", borderRadius: 16, padding: 20, marginBottom: 16 }}>
          <FitMeter score={fitScore} />
          <div style={{ textAlign: "center", color: "#aaa", fontFamily: "'DM Sans', sans-serif", fontSize: 13 }}>
            Fitness score for <strong style={{ color: "#fff" }}>{skinType}</strong> skin
            <div style={{ fontSize: 11, color: "#555", marginTop: 4 }}>
              The above fitness score reflects the product's alignment with your skin type, concerns, and other risk factors.
            </div>
          </div>
        </div>
      )}

      {/* ── Product intelligence ── */}
      <div style={{ background: "#0d0d0d", border: "1px solid #1e1e1e", borderRadius: 16, padding: 20, marginBottom: 16 }}>
        <SectionTitle>Product Intelligence Summary</SectionTitle>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 16 }}>
          {s.texture && <PillTag text={`Texture: ${s.texture}`} />}
          {s.finish && <PillTag text={`Finish: ${s.finish}`} />}
          {s.coverage && <PillTag text={`Coverage: ${s.coverage}`} />}
        </div>

        {s.skin_types?.length > 0 && (
          <div style={{ marginBottom: 14 }}>
            <SubLabel>Best suited for</SubLabel>
            <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
              {s.skin_types.map((t) => <PillTag key={t} text={`${t} skin`} variant="good" />)}
            </div>
          </div>
        )}

        {s.avoid_for?.length > 0 && (
          <div style={{ marginBottom: 14 }}>
            <SubLabel>May not suit</SubLabel>
            <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
              {s.avoid_for.map((t) => <PillTag key={t} text={`${t} skin`} variant="warn" />)}
            </div>
          </div>
        )}

        {s.ingredient_intent && (
          <div style={{ marginBottom: 14 }}>
            <SubLabel>Key ingredients</SubLabel>
            <div style={{ color: "#aaa", fontFamily: "'DM Sans', sans-serif", fontSize: 14, lineHeight: 1.7 }}>
              {s.ingredient_intent.split("+").map((part, i) => (
                <div key={i} style={{ marginBottom: 4 }}>• {part.trim()}</div>
              ))}
            </div>
          </div>
        )}

        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          <PillTag text={`Pore risk: ${s.comedogenic_risk}`} variant={s.comedogenic_risk === "high" ? "warn" : "default"} />
          <PillTag text={`Sensitivity risk: ${s.sensitivity_risk}`} variant={s.sensitivity_risk === "high" ? "warn" : "default"} />
        </div>
      </div>

      {/* ── Skin type selector ── */}
      <div style={{ background: "#0d0d0d", border: "1px solid #1e1e1e", borderRadius: 16, padding: 20, marginBottom: 16 }}>
        <div style={{ color: "#aaa", fontFamily: "'DM Sans', sans-serif", fontSize: 13, marginBottom: 14 }}>
          {isPersonalized ? "Switch skin type to update your score" : "Want to see how well this fits\u202fyou?"}
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
          {SKIN_TYPES.map((st) => (
            <button
              key={st.id}
              onClick={() => handleSkinSelect(st.id)}
              disabled={personalizing}
              style={{
                background: skinType === st.id ? "rgba(99,102,241,0.2)" : "#141414",
                border: `1px solid ${skinType === st.id ? "#6366f1" : "#2a2a2a"}`,
                borderRadius: 10, padding: "12px 16px",
                cursor: personalizing ? "wait" : "pointer",
                color: "#fff", fontFamily: "'DM Sans', sans-serif", fontSize: 14,
                display: "flex", alignItems: "center", gap: 8,
                transition: "all 0.15s ease",
                opacity: personalizing && skinType !== st.id ? 0.4 : 1,
              }}
            >
              <span>{st.icon}</span>
              {st.label}
              {personalizing && skinType === st.id && (
                <span style={{ marginLeft: "auto", fontSize: 11, color: "#6366f1" }}>…</span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* ── What customers say ── */}
      <div style={{ background: "#0d0d0d", border: "1px solid #1e1e1e", borderRadius: 16, padding: 20, marginBottom: 16 }}>
        <SectionTitle>What customers say</SectionTitle>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
          {s.pros?.length > 0 && (
            <div>
              <SubLabel>👍 Praised for</SubLabel>
              {s.pros.map((p) => <ReviewLine key={p} text={p} good />)}
            </div>
          )}
          {s.cons?.length > 0 && (
            <div>
              <SubLabel>👎 Criticism</SubLabel>
              {s.cons.map((c) => <ReviewLine key={c} text={c} />)}
            </div>
          )}
        </div>
      </div>

      {/* ── Why this result ── */}
      {s.rationale?.length > 0 && (
        <div style={{ background: "#0a0a12", border: "1px solid #1e1e30", borderRadius: 16, padding: 20, marginBottom: 16 }}>
          <SectionTitle>{"Why this result"}</SectionTitle>
          {s.rationale.map((r, i) => (
            <div key={i} style={{ display: "flex", alignItems: "flex-start", gap: 8, marginBottom: 8 }}>
              <span style={{ color: "#6366f1", marginTop: 2 }}><ChevronRight /></span>
              <span style={{ color: "#aaa", fontFamily: "'DM Sans', sans-serif", fontSize: 14, lineHeight: 1.6 }}>{r}</span>
            </div>
          ))}
        </div>
      )}

      {/* ── Better alternatives ── */}
      {activeData.alternatives?.length > 0 && (
        <div style={{ background: "#0d0d0d", border: "1px solid #1e1e1e", borderRadius: 16, padding: 20, marginBottom: 16 }}>
          <SectionTitle>Better alternatives</SectionTitle>
          {activeData.alternatives.map((alt, i) => (
            <div key={i} style={{ background: "#141414", border: "1px solid #222", borderRadius: 12, padding: 16, marginBottom: i < activeData.alternatives.length - 1 ? 10 : 0 }}>
              <div style={{ color: "#fff", fontFamily: "'DM Sans', sans-serif", fontWeight: 600, fontSize: 15, marginBottom: 6 }}>{alt.name}</div>
              <div style={{ color: "#666", fontFamily: "'DM Sans', sans-serif", fontSize: 13 }}>{alt.why_different}</div>
            </div>
          ))}
        </div>
      )}

      {/* ── Reset ── */}
      <button
        onClick={onReset}
        onMouseEnter={e => e.currentTarget.style.borderColor = "#444"}
        onMouseLeave={e => e.currentTarget.style.borderColor = "#2a2a2a"}
        style={{ background: "transparent", border: "1px solid #2a2a2a", borderRadius: 10, padding: "14px 20px", color: "#666", cursor: "pointer", fontFamily: "'DM Sans', sans-serif", fontSize: 14, display: "flex", alignItems: "center", justifyContent: "center", gap: 8, transition: "all 0.15s ease" }}
      >
        <RefreshIcon /> Scan another product
      </button>
    </div>
  );
}
