import { useState } from "react";
import ScanStep from "./components/ScanStep";
import LoadingState from "./components/LoadingState";
import ResultView from "./components/ResultView";
import Signup from "./components/Signup";
import Login from "./components/Login";
import { ArrowLeftIcon, ArrowRightIcon } from "./components/icons/Icons";
import { API_URL } from "./constants";

export default function App() {
  const [authPhase, setAuthPhase] = useState("login"); // "login" | "signup" | "app"
  const [currentUser, setCurrentUser] = useState(null); // stores login response data
  const [serverError, setServerError] = useState(null);

  const [phase, setPhase] = useState("scan");
  const [result, setResult] = useState(null);
  const [imageBase64, setImageBase64] = useState(null);
  const [history, setHistory] = useState(["scan"]);
  const [historyIndex, setHistoryIndex] = useState(0);

  // ── Auth handlers ────────────────────────────────────────────────────────────
  const handleLoginSuccess = (data) => {
    setCurrentUser(data);
    setAuthPhase("app");
  };

  const handleLogoutSuccess = () => {
    setCurrentUser(null);
    setAuthPhase("login");
    handleReset();
  };

  const handleLogout = async () => {
    if (!currentUser) {
      setAuthPhase("login");
      return;
    }

    try {
      const res = await fetch(`${API_URL}/logout`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(currentUser),
      });
      const data = await res.json();
      if (!res.ok) {
        setServerError(data.detail || "Logout failed. Check your connection.")
        return;
      }
      setServerError(null);
      handleLogoutSuccess();
    } catch (error) {
      setServerError(`Failed to sign out the user. ${error}`);
    }
  };

  const handleSignupSuccess = () => {
    setAuthPhase("app");
  };

  // ── Scanner navigation ───────────────────────────────────────────────────────
  const navigateTo = (newPhase) => {
    if (newPhase === "loading") { setPhase("loading"); return; }
    const newHistory = [...history.slice(0, historyIndex + 1), newPhase];
    setHistory(newHistory);
    setHistoryIndex(newHistory.length - 1);
    setPhase(newPhase);
  };

  const goBack = () => {
    if (historyIndex === 0) return;
    const newIndex = historyIndex - 1;
    setHistoryIndex(newIndex);
    setPhase(history[newIndex]);
  };

  const goForward = () => {
    if (historyIndex >= history.length - 1) return;
    const newIndex = historyIndex + 1;
    setHistoryIndex(newIndex);
    setPhase(history[newIndex]);
  };

  const handleResult = (data, b64) => { setResult(data); setImageBase64(b64); navigateTo("result"); };
  const handleLoading = (v) => { if (v) navigateTo("loading"); };
  const handleReset = () => { setResult(null); setImageBase64(null); setHistory(["scan"]); setHistoryIndex(0); setPhase("scan"); };

  const canGoBack = historyIndex > 0 && phase !== "loading";
  const canGoForward = historyIndex < history.length - 1 && phase !== "loading";

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
          onSuccess={handleLoginSuccess}
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
          onSuccess={handleSignupSuccess}
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
              {/* Logged in user indicator */}
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
                onClick={() => { handleLogout(); }}
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
          {serverError && (
            <div style={{ background: "#1a0a0a", border: "1px solid #3a1a1a", borderRadius: 8, padding: "10px 14px", marginBottom: 20, color: "#f87171", fontFamily: "'DM Sans', sans-serif", fontSize: 13 }}>
              {serverError}
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
