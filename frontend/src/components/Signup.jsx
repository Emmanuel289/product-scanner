import { useState } from "react";
import { API_URL } from "../constants";

const inputStyle = {
  width: "100%",
  background: "#141414",
  border: "1px solid #2a2a2a",
  borderRadius: 10,
  padding: "12px 14px",
  color: "#fff",
  fontFamily: "'DM Sans', sans-serif",
  fontSize: 14,
  outline: "none",
  boxSizing: "border-box",
  transition: "border-color 0.15s ease",
};

const labelStyle = {
  color: "#555",
  fontFamily: "'DM Sans', sans-serif",
  fontSize: 11,
  letterSpacing: 1.5,
  textTransform: "uppercase",
  marginBottom: 6,
  display: "block",
};

function SuccessBanner({ onDone }) {
  const [fading, setFading] = useState(false);

  useState(() => {
    const fadeTimer = setTimeout(() => setFading(true), 1800);
    const doneTimer = setTimeout(() => onDone(), 2400);
    return () => { clearTimeout(fadeTimer); clearTimeout(doneTimer); };
  }, []);

  return (
    <div style={{
      position: "fixed", inset: 0,
      background: "rgba(0,0,0,0.85)",
      display: "flex", alignItems: "center", justifyContent: "center",
      zIndex: 100,
      opacity: fading ? 0 : 1,
      transition: "opacity 0.6s ease",
    }}>
      <div style={{
        background: "#0d0d0d",
        border: "1px solid #1e1e1e",
        borderRadius: 20,
        padding: "40px 48px",
        textAlign: "center",
        animation: "slideUp 0.4s ease",
      }}>
        <div style={{ fontSize: 40, marginBottom: 16 }}>✦</div>
        <div style={{
          color: "#fff",
          fontFamily: "'DM Serif Display', serif",
          fontSize: 24,
          marginBottom: 8,
        }}>
          You're in
        </div>
        <div style={{
          color: "#555",
          fontFamily: "'DM Sans', sans-serif",
          fontSize: 14,
        }}>
          Account created. Loading your scanner…
        </div>
      </div>
    </div>
  );
}

export default function SignupPage({ onSuccess, onGoToLogin }) {
  const [form, setForm] = useState({ username: "", email: "", password: "", confirm: "" });
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [serverError, setServerError] = useState(null);
  const [showSuccess, setShowSuccess] = useState(false);
  const [focusedField, setFocusedField] = useState(null);

  const validate = () => {
    const e = {};
    if (!form.username.trim()) e.username = "Username is required";
    if (!form.email.trim()) e.email = "Email is required";
    else if (!/\S+@\S+\.\S+/.test(form.email)) e.email = "Enter a valid email";
    if (!form.password) e.password = "Password is required";
    else if (form.password.length < 8) e.password = "At least 8 characters";
    if (form.password !== form.confirm) e.confirm = "Passwords don't match";
    return e;
  };

  const handleSubmit = async () => {
    setServerError(null);
    const e = validate();
    if (Object.keys(e).length) { setErrors(e); return; }
    setErrors({});
    setSubmitting(true);
    try {
      const res = await fetch(`${API_URL}/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: form.username,
          email: form.email,
          password: form.password,
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        setServerError(data.detail || "Signup failed. Please try again.");
        return;
      }
      setShowSuccess(true);
    } catch {
      setServerError("Could not connect to the server.");
    } finally {
      setSubmitting(false);
    }
  };

  const fields = [
    { key: "username", label: "Username", type: "text", placeholder: "e.g. skincaregeek" },
    { key: "email", label: "Email", type: "email", placeholder: "you@example.com" },
    { key: "password", label: "Password", type: "password", placeholder: "Min. 8 characters" },
    { key: "confirm", label: "Confirm Password", type: "password", placeholder: "Repeat your password" },
  ];

  return (
    <>
      {showSuccess && <SuccessBanner onDone={onSuccess} />}

      <style>{`
        @keyframes slideUp {
          from { opacity: 0; transform: translateY(16px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        input::placeholder { color: #333; }
        input:focus { border-color: #6366f1 !important; }
      `}</style>

      <div style={{ minHeight: "100vh", background: "#080808", display: "flex", alignItems: "center", justifyContent: "center", padding: 24 }}>
        <div style={{ width: "100%", maxWidth: 400, animation: "slideUp 0.4s ease" }}>

          {/* Header */}
          <div style={{ textAlign: "center", marginBottom: 32 }}>
            <div style={{ color: "#6366f1", fontFamily: "'DM Sans', sans-serif", fontSize: 11, letterSpacing: 3, textTransform: "uppercase", marginBottom: 12 }}>
              Product Scanner
            </div>
            <div style={{ color: "#fff", fontFamily: "'DM Serif Display', serif", fontSize: 30, marginBottom: 8 }}>
              Create an account
            </div>
            <div style={{ color: "#555", fontFamily: "'DM Sans', sans-serif", fontSize: 14 }}>
              Start scanning products personalised to your skin.
            </div>
          </div>

          {/* Card */}
          <div style={{ background: "#0d0d0d", border: "1px solid #1e1e1e", borderRadius: 20, padding: 28 }}>

            {serverError && (
              <div style={{
                background: "rgba(239,68,68,0.08)",
                border: "1px solid rgba(239,68,68,0.2)",
                borderRadius: 10, padding: "10px 14px",
                color: "#ef4444", fontFamily: "'DM Sans', sans-serif", fontSize: 13,
                marginBottom: 20,
              }}>
                {serverError}
              </div>
            )}

            <div style={{ display: "flex", flexDirection: "column", gap: 18 }}>
              {fields.map(({ key, label, type, placeholder }) => (
                <div key={key}>
                  <label style={labelStyle}>{label}</label>
                  <input
                    type={type}
                    placeholder={placeholder}
                    value={form[key]}
                    onChange={e => setForm(f => ({ ...f, [key]: e.target.value }))}
                    onFocus={() => setFocusedField(key)}
                    onBlur={() => setFocusedField(null)}
                    style={{
                      ...inputStyle,
                      borderColor: errors[key] ? "rgba(239,68,68,0.5)" : focusedField === key ? "#6366f1" : "#2a2a2a",
                    }}
                  />
                  {errors[key] && (
                    <div style={{ color: "#ef4444", fontFamily: "'DM Sans', sans-serif", fontSize: 12, marginTop: 5 }}>
                      {errors[key]}
                    </div>
                  )}
                </div>
              ))}
            </div>

            <button
              onClick={handleSubmit}
              disabled={submitting}
              style={{
                width: "100%", marginTop: 24,
                background: submitting ? "#1a1a2e" : "rgba(99,102,241,0.15)",
                border: "1px solid #6366f1",
                borderRadius: 10, padding: "13px 20px",
                color: submitting ? "#555" : "#a5b4fc",
                fontFamily: "'DM Sans', sans-serif", fontSize: 14,
                cursor: submitting ? "wait" : "pointer",
                transition: "all 0.15s ease",
                letterSpacing: 0.5,
              }}
              onMouseEnter={e => { if (!submitting) e.currentTarget.style.background = "rgba(99,102,241,0.25)"; }}
              onMouseLeave={e => { if (!submitting) e.currentTarget.style.background = "rgba(99,102,241,0.15)"; }}
            >
              {submitting ? "Creating account…" : "Create account →"}
            </button>
          </div>

          {/* Footer link */}
          <div style={{ textAlign: "center", marginTop: 20, color: "#444", fontFamily: "'DM Sans', sans-serif", fontSize: 13 }}>
            Already have an account?{" "}
            <span
              onClick={onGoToLogin}
              style={{ color: "#6366f1", cursor: "pointer", textDecoration: "underline" }}
            >
              Sign in
            </span>
          </div>
        </div>
      </div>
    </>
  );
}
