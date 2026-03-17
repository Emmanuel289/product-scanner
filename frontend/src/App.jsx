import { useAuth } from "./hooks/useAuth";
import { useScanner } from "./hooks/useScanner";
import ScanStep from "./components/ScanStep";
import LoadingState from "./components/LoadingState";
import ResultView from "./components/ResultView";
import Signup from "./components/Signup";
import Login from "./components/Login";
import { ArrowLeftIcon, ArrowRightIcon } from "./components/icons/Icons";

export default function App() {
  const {
    currentUser,
    authPhase,
    setAuthPhase,
    authError,
    handleAuthSuccess,
    handleLogout,
  } = useAuth();

  const {
    phase,
    result,
    imageBase64,
    canGoBack,
    canGoForward,
    goBack,
    goForward,
    handleResult,
    handleLoading,
    handleReset,
  } = useScanner();


  const navBtnStyle = (enabled) => ({
    background: "transparent",
    border: `1px solid ${enabled ? "#2a2a2a" : "transparent"}`,
    borderRadius: 8, padding: "6px 8px",
    color: enabled ? "#666" : "#2a2a2a",
    cursor: enabled ? "pointer" : "default",
    display: "flex", alignItems: "center", justifyContent: "center",
    transition: "all 0.15s ease",
    pointerEvents: enabled ? "auto" : "none",
  });

  // ── Font link shared across all pages ────────────────────────────────────────
  const fonts = (
    <link
      href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@400;500;600;700&display=swap"
      rel="stylesheet"
    />
  );

  // ── Auth screens ─────────────────────────────────────────────────────────────
  if (authPhase === "login") {
    return (
      <>
        {fonts}
        <Login
          onSuccess={handleAuthSuccess}
          onGoToSignup={() => setAuthPhase("signup")}
        />
      </>
    );
  }

  if (authPhase === "signup") {
    return (
      <>
        {fonts}
        <Signup
          onSuccess={handleAuthSuccess}
          onGoToLogin={() => setAuthPhase("login")}
        />
      </>
    );
  }

  // ── Main app ─────────────────────────────────────────────────────────────────
  return (
    <>
      {fonts}
      <div style={{ minHeight: "100vh", background: "#080808", display: "flex", justifyContent: "center", padding: "0 0 80px 0" }}>
        <div style={{ width: "100%", maxWidth: 500, padding: "0 16px" }}>

          {/* Top bar */}
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "28px 0 32px" }}>
            <div>
              <div style={{ fontFamily: "'DM Serif Display', serif", fontSize: 22, color: "#fff", letterSpacing: -0.5 }}>StyleCast</div>
              <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 11, color: "#444", letterSpacing: 2, textTransform: "uppercase" }}>Product Scanner</div>
            </div>

            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              {currentUser?.client?.username && (
                <div style={{
                  color: "#444", fontFamily: "'DM Sans', sans-serif", fontSize: 12,
                  borderRight: "1px solid #1e1e1e", paddingRight: 12, marginRight: 4,
                }}>
                  {currentUser.client.username}
                </div>
              )}

              {/* Sign out */}
              <button
                onClick={() => { handleLogout(handleReset); }}
                style={{
                  background: "transparent", border: "none",
                  color: "#333", fontFamily: "'DM Sans', sans-serif", fontSize: 12,
                  cursor: "pointer", padding: "4px 0",
                  transition: "color 0.15s ease",
                }}
                onMouseEnter={e => e.currentTarget.style.color = "#666"}
                onMouseLeave={e => e.currentTarget.style.color = "#333"}
              >
                Sign out
              </button>

              {/* Back + forward */}
              <div style={{ display: "flex", alignItems: "center", gap: 4, marginLeft: 4 }}>
                <button
                  onClick={goBack} disabled={!canGoBack} style={navBtnStyle(canGoBack)}
                  onMouseEnter={e => { if (canGoBack) e.currentTarget.style.borderColor = "#444"; }}
                  onMouseLeave={e => { if (canGoBack) e.currentTarget.style.borderColor = "#2a2a2a"; }}
                >
                  <ArrowLeftIcon />
                </button>
                <button
                  onClick={goForward} disabled={!canGoForward} style={navBtnStyle(canGoForward)}
                  onMouseEnter={e => { if (canGoForward) e.currentTarget.style.borderColor = "#444"; }}
                  onMouseLeave={e => { if (canGoForward) e.currentTarget.style.borderColor = "#2a2a2a"; }}
                >
                  <ArrowRightIcon />
                </button>
              </div>
            </div>
          </div>

          {/* Error banner */}
          {authError && (
            <div style={{ background: "#1a0a0a", border: "1px solid #3a1a1a", borderRadius: 8, padding: "10px 14px", marginBottom: 20, color: "#f87171", fontFamily: "'DM Sans', sans-serif", fontSize: 13 }}>
              {authError}
            </div>
          )}

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
