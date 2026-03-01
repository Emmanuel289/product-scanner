import { useState, useRef, useEffect } from "react";

// ─── CONFIG ──────────────────────────────────────────────────────────────────
const API_ENDPOINT = "https://vnf9ydkp22.execute-api.us-east-1.amazonaws.com/prod/scan";

const SKIN_TYPES = [
  { id: "dry", label: "Dry", icon: "🌵" },
  { id: "oily", label: "Oily", icon: "💧" },
  { id: "combination", label: "Combination", icon: "☯️" },
  { id: "sensitive", label: "Sensitive", icon: "🌸" },
];

const FIT_SCORES = { dry: 45, oily: 82, combination: 75, sensitive: 88 };

// ─── ICONS ───────────────────────────────────────────────────────────────────
const ScanIcon = () => (
  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
    <path d="M3 7V5a2 2 0 012-2h2M17 3h2a2 2 0 012 2v2M21 17v2a2 2 0 01-2 2h-2M7 21H5a2 2 0 01-2-2v-2" />
    <line x1="3" y1="12" x2="21" y2="12" />
  </svg>
);

const UploadIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
    <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M17 8l-5-5-5 5M12 3v12" />
  </svg>
);

const CameraIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
    <path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z" />
    <circle cx="12" cy="13" r="4" />
  </svg>
);

const ChevronRight = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M9 18l6-6-6-6" />
  </svg>
);

const RefreshIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M23 4v6h-6M1 20v-6h6M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15" />
  </svg>
);

// ─── OUTCOME BADGE ────────────────────────────────────────────────────────────
function OutcomeBadge({ outcome, large = false }) {
  const map = {
    "✅ Good match": { bg: "#0d2e1a", border: "#1a5c32", text: "#4ade80", dot: "#22c55e", label: "Good Match" },
    "⚠️ Mixed match": { bg: "#2e1f0d", border: "#7a4a0a", text: "#fbbf24", dot: "#f59e0b", label: "Mixed Match" },
    "⚠️ Use with caution": { bg: "#2e1f0d", border: "#7a4a0a", text: "#fbbf24", dot: "#f59e0b", label: "Use with Caution" },
    "❌ Not recommended": { bg: "#2e0d0d", border: "#7a1a1a", text: "#f87171", dot: "#ef4444", label: "Not Recommended" },
  };
  const style = map[outcome] || map["⚠️ Mixed match"];
  return (
    <div style={{
      display: "inline-flex", alignItems: "center", gap: 8,
      background: style.bg, border: `1px solid ${style.border}`,
      borderRadius: 100, padding: large ? "10px 20px" : "6px 14px",
    }}>
      <div style={{ width: large ? 10 : 8, height: large ? 10 : 8, borderRadius: "50%", background: style.dot, boxShadow: `0 0 8px ${style.dot}` }} />
      <span style={{ color: style.text, fontFamily: "'DM Sans', sans-serif", fontWeight: 600, fontSize: large ? 16 : 13 }}>{style.label}</span>
    </div>
  );
}

// ─── FIT METER ────────────────────────────────────────────────────────────────
function FitMeter({ score }) {
  const color = score >= 75 ? "#22c55e" : score >= 50 ? "#f59e0b" : "#ef4444";
  return (
    <div style={{ textAlign: "center", padding: "24px 0" }}>
      <div style={{ position: "relative", width: 120, height: 120, margin: "0 auto 16px" }}>
        <svg width="120" height="120" style={{ transform: "rotate(-90deg)" }}>
          <circle cx="60" cy="60" r="50" fill="none" stroke="#1e1e1e" strokeWidth="10" />
          <circle cx="60" cy="60" r="50" fill="none" stroke={color} strokeWidth="10"
            strokeDasharray={`${2 * Math.PI * 50}`}
            strokeDashoffset={`${2 * Math.PI * 50 * (1 - score / 100)}`}
            strokeLinecap="round"
            style={{ transition: "stroke-dashoffset 1s cubic-bezier(.4,0,.2,1)", filter: `drop-shadow(0 0 6px ${color})` }}
          />
        </svg>
        <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", flexDirection: "column" }}>
          <span style={{ fontSize: 28, fontWeight: 700, color, fontFamily: "'DM Serif Display', serif" }}>{score}%</span>
          <span style={{ fontSize: 10, color: "#666", fontFamily: "'DM Sans', sans-serif", letterSpacing: 1 }}>MATCH</span>
        </div>
      </div>
    </div>
  );
}

// ─── PILL TAG ─────────────────────────────────────────────────────────────────
function PillTag({ text, variant = "default" }) {
  const styles = {
    default: { bg: "#1a1a1a", text: "#888", border: "#2a2a2a" },
    good: { bg: "#0d2e1a", text: "#4ade80", border: "#1a5c32" },
    warn: { bg: "#2e1f0d", text: "#fbbf24", border: "#7a4a0a" },
  };
  const s = styles[variant];
  return (
    <span style={{
      display: "inline-block", padding: "4px 12px", borderRadius: 100,
      background: s.bg, border: `1px solid ${s.border}`,
      color: s.text, fontSize: 12, fontFamily: "'DM Sans', sans-serif",
    }}>{text}</span>
  );
}

// ─── SCAN STEP ────────────────────────────────────────────────────────────────
function ScanStep({ onResult, onLoading }) {
  const [preview, setPreview] = useState(null);
  const [cameraActive, setCameraActive] = useState(false);
  const [dragging, setDragging] = useState(false);
  const fileRef = useRef();
  const cameraFileRef = useRef();   // fallback for mobile native camera
  const videoRef = useRef();
  const streamRef = useRef();

  // ── Start live camera stream ──
  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: { ideal: "environment" }, width: { ideal: 1280 }, height: { ideal: 720 } }
      });
      streamRef.current = stream;
      setCameraActive(true);
      // Attach stream to video element after state update renders it
      setTimeout(() => {
        if (videoRef.current) videoRef.current.srcObject = stream;
      }, 50);
    } catch (err) {
      // Fallback: open native camera file picker (works on iOS/Android)
      cameraFileRef.current?.click();
    }
  };

  // ── Stop stream ──
  const stopCamera = () => {
    streamRef.current?.getTracks().forEach(t => t.stop());
    streamRef.current = null;
    setCameraActive(false);
  };

  // ── Capture still from live video ──
  const captureFrame = () => {
    const video = videoRef.current;
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext("2d").drawImage(video, 0, 0);
    setPreview(canvas.toDataURL("image/jpeg", 0.92));
    stopCamera();
  };

  // ── Handle file from upload or camera fallback ──
  const handleFile = (f) => {
    if (!f || !f.type.startsWith("image/")) return;
    const reader = new FileReader();
    reader.onload = (e) => setPreview(e.target.result);
    reader.readAsDataURL(f);
  };

  const handleDrop = (e) => {
    e.preventDefault(); setDragging(false);
    handleFile(e.dataTransfer.files[0]);
  };

  // ── Stop camera on unmount ──
  useEffect(() => () => stopCamera(), []);

  const retake = () => { setPreview(null); stopCamera(); };

  const handleAnalyze = async () => {
    if (!preview) return;
    onLoading(true);
    try {
      const base64 = preview.split(",")[1];
      const res = await fetch(API_ENDPOINT, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image_base64: base64 }),
      });
      const data = await res.json();
      onResult(data);
    } catch (err) {
      onResult({ error: true, message: err.message });
    } finally {
      onLoading(false);
    }
  };

  // ── Live camera view ──
  if (cameraActive) return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div style={{ position: "relative", borderRadius: 16, overflow: "hidden", background: "#000", aspectRatio: "4/3" }}>
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          style={{ width: "100%", height: "100%", objectFit: "cover", display: "block" }}
        />
        {/* Viewfinder overlay */}
        <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", pointerEvents: "none" }}>
          <div style={{
            width: "72%", aspectRatio: "3/2",
            border: "2px solid rgba(99,102,241,0.8)",
            borderRadius: 12,
            boxShadow: "0 0 0 9999px rgba(0,0,0,0.45)",
            position: "relative",
          }}>
            {/* Corner accents */}
            {[
              { top: -2, left: -2, borderTop: "3px solid #6366f1", borderLeft: "3px solid #6366f1", borderRadius: "4px 0 0 0" },
              { top: -2, right: -2, borderTop: "3px solid #6366f1", borderRight: "3px solid #6366f1", borderRadius: "0 4px 0 0" },
              { bottom: -2, left: -2, borderBottom: "3px solid #6366f1", borderLeft: "3px solid #6366f1", borderRadius: "0 0 0 4px" },
              { bottom: -2, right: -2, borderBottom: "3px solid #6366f1", borderRight: "3px solid #6366f1", borderRadius: "0 0 4px 0" },
            ].map((style, i) => (
              <div key={i} style={{ position: "absolute", width: 20, height: 20, ...style }} />
            ))}
          </div>
        </div>
        <div style={{ position: "absolute", bottom: 12, left: 0, right: 0, textAlign: "center" }}>
          <span style={{ color: "rgba(255,255,255,0.5)", fontFamily: "'DM Sans', sans-serif", fontSize: 12 }}>
            Point at product label
          </span>
        </div>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
        <button onClick={retake} style={{
          background: "#141414", border: "1px solid #2a2a2a", borderRadius: 12,
          padding: "14px", color: "#888", cursor: "pointer",
          fontFamily: "'DM Sans', sans-serif", fontSize: 14,
        }}>Cancel</button>
        <button onClick={captureFrame} style={{
          background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
          border: "none", borderRadius: 12, padding: "14px",
          color: "#fff", fontSize: 14, fontWeight: 700, cursor: "pointer",
          fontFamily: "'DM Sans', sans-serif",
          boxShadow: "0 0 20px rgba(99,102,241,0.4)",
        }}>Capture</button>
      </div>
    </div>
  );

  // ── Preview + analyze ──
  if (preview) return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div style={{ position: "relative", borderRadius: 16, overflow: "hidden" }}>
        <img src={preview} alt="Product" style={{ width: "100%", maxHeight: 300, objectFit: "cover", display: "block" }} />
        <div style={{
          position: "absolute", inset: 0,
          background: "linear-gradient(to top, rgba(0,0,0,0.8) 0%, transparent 60%)",
          display: "flex", alignItems: "flex-end", padding: 16,
        }}>
          <button onClick={retake} style={{
            background: "rgba(0,0,0,0.5)", border: "1px solid rgba(255,255,255,0.15)",
            borderRadius: 8, padding: "6px 14px", color: "#ccc", cursor: "pointer",
            fontFamily: "'DM Sans', sans-serif", fontSize: 13, backdropFilter: "blur(8px)",
          }}>Retake</button>
        </div>
      </div>
      <button onClick={handleAnalyze} style={{
        background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
        border: "none", borderRadius: 12, padding: "16px 24px",
        color: "#fff", fontSize: 16, fontWeight: 700, cursor: "pointer",
        fontFamily: "'DM Sans', sans-serif", letterSpacing: 0.5,
        boxShadow: "0 0 24px rgba(99,102,241,0.4)",
        transition: "transform 0.15s ease, box-shadow 0.15s ease",
      }}
        onMouseEnter={e => { e.currentTarget.style.transform = "scale(1.02)"; e.currentTarget.style.boxShadow = "0 0 32px rgba(99,102,241,0.6)"; }}
        onMouseLeave={e => { e.currentTarget.style.transform = "scale(1)"; e.currentTarget.style.boxShadow = "0 0 24px rgba(99,102,241,0.4)"; }}
      >
        Analyze Product →
      </button>
    </div>
  );

  // ── Default: two equal entry buttons + drag zone ──
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>

        {/* Take Photo */}
        <button onClick={startCamera} style={{
          background: "#0d0d0d", border: "1px solid #2a2a2a",
          borderRadius: 14, padding: "28px 16px",
          cursor: "pointer", display: "flex", flexDirection: "column",
          alignItems: "center", gap: 10, transition: "border-color 0.15s ease",
        }}
          onMouseEnter={e => e.currentTarget.style.borderColor = "#6366f1"}
          onMouseLeave={e => e.currentTarget.style.borderColor = "#2a2a2a"}
        >
          <div style={{ color: "#6366f1" }}><CameraIcon /></div>
          <span style={{ color: "#fff", fontFamily: "'DM Sans', sans-serif", fontWeight: 600, fontSize: 14 }}>Take Photo</span>
          <span style={{ color: "#555", fontFamily: "'DM Sans', sans-serif", fontSize: 12 }}>Use your camera</span>
        </button>

        {/* Upload */}
        <div
          onClick={() => fileRef.current?.click()}
          onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={handleDrop}
          style={{
            background: dragging ? "rgba(99,102,241,0.06)" : "#0d0d0d",
            border: `1px solid ${dragging ? "#6366f1" : "#2a2a2a"}`,
            borderRadius: 14, padding: "28px 16px",
            cursor: "pointer", display: "flex", flexDirection: "column",
            alignItems: "center", gap: 10, transition: "border-color 0.15s ease",
          }}
          onMouseEnter={e => { if (!dragging) e.currentTarget.style.borderColor = "#6366f1"; }}
          onMouseLeave={e => { if (!dragging) e.currentTarget.style.borderColor = "#2a2a2a"; }}
        >
          <div style={{ color: "#6366f1" }}><UploadIcon /></div>
          <span style={{ color: "#fff", fontFamily: "'DM Sans', sans-serif", fontWeight: 600, fontSize: 14 }}>Upload</span>
          <span style={{ color: "#555", fontFamily: "'DM Sans', sans-serif", fontSize: 12 }}>Gallery or file</span>
        </div>
      </div>

      <div style={{ textAlign: "center", color: "#333", fontFamily: "'DM Sans', sans-serif", fontSize: 12 }}>
        or drag & drop onto Upload
      </div>

      {/* Hidden inputs */}
      {/* Upload (no capture — opens file picker / gallery) */}
      <input
        ref={fileRef}
        type="file"
        accept="image/*"
        style={{ display: "none" }}
        onChange={e => handleFile(e.target.files[0])}
      />
      {/* Camera fallback for mobile devices that block getUserMedia */}
      <input
        ref={cameraFileRef}
        type="file"
        accept="image/*"
        capture="environment"
        style={{ display: "none" }}
        onChange={e => handleFile(e.target.files[0])}
      />
    </div>
  );
}

// ─── LOADING STATE ────────────────────────────────────────────────────────────
function LoadingState() {
  const steps = ["Reading packaging...", "Matching database...", "Analyzing ingredients...", "Building your result..."];
  const [step, setStep] = useState(0);
  useState(() => {
    const id = setInterval(() => setStep(s => Math.min(s + 1, steps.length - 1)), 600);
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
      <div style={{ color: "#fff", fontFamily: "'DM Serif Display', serif", fontSize: 20, marginBottom: 8 }}>Scanning product</div>
      <div style={{ color: "#6366f1", fontFamily: "'DM Sans', sans-serif", fontSize: 14, transition: "all 0.3s" }}>{steps[step]}</div>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}

// ─── RESULT VIEW ──────────────────────────────────────────────────────────────
function ResultView({ data, onReset }) {
  const [skinType, setSkinType] = useState(null);
  const [fitScore, setFitScore] = useState(null);
  const [showPersonalized, setShowPersonalized] = useState(false);

  if (data.error) return (
    <div style={{ textAlign: "center", padding: "48px 0" }}>
      <div style={{ fontSize: 48, marginBottom: 16 }}>❌</div>
      <div style={{ color: "#fff", fontFamily: "'DM Serif Display', serif", fontSize: 22, marginBottom: 8 }}>Product Not Found</div>
      <div style={{ color: "#666", fontFamily: "'DM Sans', sans-serif", fontSize: 14, marginBottom: 24 }}>We couldn't confidently identify this product, so we didn't make a guess.</div>
      <button onClick={onReset} style={{ background: "#1a1a1a", border: "1px solid #333", borderRadius: 10, padding: "12px 20px", color: "#aaa", cursor: "pointer", fontFamily: "'DM Sans', sans-serif", display: "flex", alignItems: "center", gap: 8, margin: "0 auto" }}>
        <RefreshIcon /> Try again
      </button>
    </div>
  );

  const isNotFound = data.status?.includes("Product Not Found");
  if (isNotFound) return (
    <div style={{ textAlign: "center", padding: "48px 0" }}>
      <div style={{ fontSize: 48, marginBottom: 16 }}>🔍</div>
      <div style={{ color: "#fff", fontFamily: "'DM Serif Display', serif", fontSize: 22, marginBottom: 8 }}>Product Not Found</div>
      <div style={{ color: "#666", fontFamily: "'DM Sans', sans-serif", fontSize: 14, marginBottom: 24 }}>We couldn't confidently identify this product, so we didn't make a guess.</div>
      <button onClick={onReset} style={{ background: "#1a1a1a", border: "1px solid #333", borderRadius: 10, padding: "12px 20px", color: "#aaa", cursor: "pointer", fontFamily: "'DM Sans', sans-serif", display: "flex", alignItems: "center", gap: 8, margin: "0 auto" }}>
        <RefreshIcon /> Try again
      </button>
    </div>
  );

  const s = data.product_summary;

  const handleSkinSelect = (id) => {
    setSkinType(id);
    setFitScore(FIT_SCORES[id] || 70);
    setShowPersonalized(true);
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 0 }}>

      {/* Header */}
      <div style={{ marginBottom: 24 }}>
        <div style={{ color: "#666", fontFamily: "'DM Sans', sans-serif", fontSize: 12, letterSpacing: 2, textTransform: "uppercase", marginBottom: 4 }}>{data.brand}</div>
        <div style={{ color: "#fff", fontFamily: "'DM Serif Display', serif", fontSize: 26, lineHeight: 1.2, marginBottom: 12 }}>{data.product_name}</div>
        <OutcomeBadge outcome={showPersonalized && fitScore ? (fitScore >= 75 ? "✅ Good match" : fitScore >= 50 ? "⚠️ Mixed match" : "❌ Not recommended") : data.status} large />
      </div>

      {/* Personalized fit meter */}
      {showPersonalized && fitScore && (
        <div style={{ background: "#0d0d0d", border: "1px solid #1e1e1e", borderRadius: 16, padding: 20, marginBottom: 16 }}>
          <FitMeter score={fitScore} />
          <div style={{ textAlign: "center", color: "#aaa", fontFamily: "'DM Sans', sans-serif", fontSize: 13 }}>
            Fit score for <strong style={{ color: "#fff" }}>{skinType}</strong> skin type
          </div>
        </div>
      )}

      {/* Skin type selector */}
      {!showPersonalized && (
        <div style={{ background: "#0d0d0d", border: "1px solid #1e1e1e", borderRadius: 16, padding: 20, marginBottom: 16 }}>
          <div style={{ color: "#aaa", fontFamily: "'DM Sans', sans-serif", fontSize: 13, marginBottom: 14 }}>
            Want to see how well this fits <em>you</em>?
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
            {SKIN_TYPES.map(st => (
              <button key={st.id} onClick={() => handleSkinSelect(st.id)} style={{
                background: skinType === st.id ? "rgba(99,102,241,0.2)" : "#141414",
                border: `1px solid ${skinType === st.id ? "#6366f1" : "#2a2a2a"}`,
                borderRadius: 10, padding: "12px 16px", cursor: "pointer",
                color: "#fff", fontFamily: "'DM Sans', sans-serif", fontSize: 14,
                display: "flex", alignItems: "center", gap: 8,
                transition: "all 0.15s ease",
              }}>
                <span>{st.icon}</span> {st.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Intelligence summary */}
      <div style={{ background: "#0d0d0d", border: "1px solid #1e1e1e", borderRadius: 16, padding: 20, marginBottom: 16 }}>
        <SectionTitle>Product Intelligence</SectionTitle>

        {/* Texture + finish */}
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 16 }}>
          {s.texture && <PillTag text={`Texture: ${s.texture}`} />}
          {s.finish && <PillTag text={`Finish: ${s.finish}`} />}
          {s.coverage && <PillTag text={`Coverage: ${s.coverage}`} />}
        </div>

        {/* Skin types */}
        {s.skin_types?.length > 0 && (
          <div style={{ marginBottom: 14 }}>
            <SubLabel>Best suited for</SubLabel>
            <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>{s.skin_types.map(t => <PillTag key={t} text={t} variant="good" />)}</div>
          </div>
        )}

        {/* Avoid for */}
        {s.avoid_for?.length > 0 && (
          <div style={{ marginBottom: 14 }}>
            <SubLabel>May not suit</SubLabel>
            <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>{s.avoid_for.map(t => <PillTag key={t} text={t} variant="warn" />)}</div>
          </div>
        )}

        {/* Ingredient intent */}
        {s.ingredient_intent && (
          <div style={{ marginBottom: 14 }}>
            <SubLabel>Key ingredients</SubLabel>
            <div style={{ color: "#aaa", fontFamily: "'DM Sans', sans-serif", fontSize: 14, lineHeight: 1.7 }}>
              {s.ingredient_intent.split("+").map((part, i) => <div key={i} style={{ marginBottom: 4 }}>• {part.trim()}</div>)}
            </div>
          </div>
        )}

        {/* Risk badges */}
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          <PillTag text={`Pore risk: ${s.comedogenic_risk}`} variant={s.comedogenic_risk === "high" ? "warn" : "default"} />
          <PillTag text={`Sensitivity risk: ${s.sensitivity_risk}`} variant={s.sensitivity_risk === "high" ? "warn" : "default"} />
        </div>
      </div>

      {/* Pros / Cons */}
      <div style={{ background: "#0d0d0d", border: "1px solid #1e1e1e", borderRadius: 16, padding: 20, marginBottom: 16 }}>
        <SectionTitle>What customers say</SectionTitle>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
          {s.pros?.length > 0 && (
            <div>
              <SubLabel>👍 Praised for</SubLabel>
              {s.pros.map(p => <ReviewLine key={p} text={p} good />)}
            </div>
          )}
          {s.cons?.length > 0 && (
            <div>
              <SubLabel>👎 Criticism</SubLabel>
              {s.cons.map(c => <ReviewLine key={c} text={c} />)}
            </div>
          )}
        </div>
      </div>

      {/* Rationale */}
      {s.rationale?.length > 0 && (
        <div style={{ background: "#0a0a12", border: "1px solid #1e1e30", borderRadius: 16, padding: 20, marginBottom: 16 }}>
          <SectionTitle>Why this result</SectionTitle>
          {s.rationale.map((r, i) => (
            <div key={i} style={{ display: "flex", alignItems: "flex-start", gap: 8, marginBottom: 8 }}>
              <span style={{ color: "#6366f1", marginTop: 2 }}><ChevronRight /></span>
              <span style={{ color: "#aaa", fontFamily: "'DM Sans', sans-serif", fontSize: 14, lineHeight: 1.6 }}>{r}</span>
            </div>
          ))}
        </div>
      )}

      {/* Alternatives */}
      {data.alternatives?.length > 0 && (
        <div style={{ background: "#0d0d0d", border: "1px solid #1e1e1e", borderRadius: 16, padding: 20, marginBottom: 16 }}>
          <SectionTitle>Better alternatives</SectionTitle>
          {data.alternatives.map((alt, i) => (
            <div key={i} style={{
              background: "#141414", border: "1px solid #222", borderRadius: 12, padding: 16, marginBottom: i < data.alternatives.length - 1 ? 10 : 0
            }}>
              <div style={{ color: "#fff", fontFamily: "'DM Sans', sans-serif", fontWeight: 600, fontSize: 15, marginBottom: 6 }}>{alt.name}</div>
              <div style={{ color: "#666", fontFamily: "'DM Sans', sans-serif", fontSize: 13 }}>{alt.why_different}</div>
            </div>
          ))}
        </div>
      )}

      {/* Reset */}
      <button onClick={onReset} style={{
        background: "transparent", border: "1px solid #2a2a2a", borderRadius: 10,
        padding: "14px 20px", color: "#666", cursor: "pointer",
        fontFamily: "'DM Sans', sans-serif", fontSize: 14,
        display: "flex", alignItems: "center", justifyContent: "center", gap: 8,
        transition: "all 0.15s ease",
      }}
        onMouseEnter={e => e.currentTarget.style.borderColor = "#444"}
        onMouseLeave={e => e.currentTarget.style.borderColor = "#2a2a2a"}
      >
        <RefreshIcon /> Scan another product
      </button>
    </div>
  );
}

// ─── TINY HELPERS ─────────────────────────────────────────────────────────────
function SectionTitle({ children }) {
  return <div style={{ color: "#fff", fontFamily: "'DM Serif Display', serif", fontSize: 17, marginBottom: 14 }}>{children}</div>;
}
function SubLabel({ children }) {
  return <div style={{ color: "#555", fontFamily: "'DM Sans', sans-serif", fontSize: 11, letterSpacing: 1.5, textTransform: "uppercase", marginBottom: 8 }}>{children}</div>;
}
function ReviewLine({ text, good }) {
  return (
    <div style={{ display: "flex", gap: 6, marginBottom: 6, alignItems: "flex-start" }}>
      <span style={{ color: good ? "#22c55e" : "#f87171", fontSize: 11, marginTop: 3 }}>●</span>
      <span style={{ color: "#aaa", fontFamily: "'DM Sans', sans-serif", fontSize: 13, lineHeight: 1.5 }}>{text}</span>
    </div>
  );
}

// ─── ROOT APP ─────────────────────────────────────────────────────────────────
export default function App() {
  const [phase, setPhase] = useState("scan"); // scan | loading | result
  const [result, setResult] = useState(null);

  const handleResult = (data) => { setResult(data); setPhase("result"); };
  const handleLoading = (v) => { if (v) setPhase("loading"); };
  const handleReset = () => { setResult(null); setPhase("scan"); };

  return (
    <>
      <link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet" />
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
                    <div style={{ height: 2, borderRadius: 2, background: done ? "#6366f1" : active ? "#6366f1" : "#1e1e1e", opacity: active ? 1 : done ? 0.6 : 1 }} />
                    <span style={{ color: active ? "#aaa" : "#333", fontFamily: "'DM Sans', sans-serif", fontSize: 11, letterSpacing: 1 }}>{label}</span>
                  </div>
                );
              })}
            </div>
          )}

          {/* Content */}
          {phase === "scan" && <ScanStep onResult={handleResult} onLoading={handleLoading} />}
          {phase === "loading" && <LoadingState />}
          {phase === "result" && <ResultView data={result} onReset={handleReset} />}
        </div>
      </div>
    </>
  );
}
