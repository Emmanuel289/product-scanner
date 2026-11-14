import { useState, useEffect } from "react";
import { confirmSignUp } from "aws-amplify/auth";

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


function SuccessBanner({ username, onDone }) {
    const [fading, setFading] = useState(false);

    useEffect(() => {
        const fadeTimer = setTimeout(
            () => setFading(true),
            1800
        );

        const doneTimer = setTimeout(
            () => onDone?.(),
            2400
        );

        return () => {
            clearTimeout(fadeTimer);
            clearTimeout(doneTimer);
        };
    }, [onDone]);

    return (
        <div style={{
            position: "fixed",
            inset: 0,
            background: "rgba(0,0,0,0.85)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
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
            }}>
                <div style={{ fontSize: 40, marginBottom: 16 }}>
                    ✦
                </div>

                <div style={{
                    color: "#fff",
                    fontSize: 24,
                    marginBottom: 8,
                }}>
                    Account confirmed
                </div>

                <div style={{
                    color: "#555",
                    fontSize: 14,
                }}>
                    {username} has been successfully confirmed.
                    Redirecting to login...
                </div>
            </div>
        </div>
    );
}


export default function ConfirmSignUpPage({ onSuccess, userName }) {
    const [form, setForm] = useState({ code: "" });
    const [errors, setErrors] = useState({});
    const [submitting, setSubmitting] = useState(false);
    const [serverError, setServerError] = useState(null);
    const [showSuccess, setShowSuccess] = useState(false);
    const [focusedField, setFocusedField] = useState(null);

    const validateFormInputs = () => {
        const e = {};
        if (!form.code.trim()) {
            e.code = "Please enter the confirmation code that was sent to your email";
        }
        return e;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (submitting) return;

        setServerError(null);

        const validationErrors = validateFormInputs();

        if (Object.keys(validationErrors).length) {
            setErrors(validationErrors);
            return;
        }

        setErrors({});
        setSubmitting(true);
        try {
            await confirmSignUp({
                username: userName,
                confirmationCode: form.code.trim(),
            });
            setShowSuccess(true);

        } catch (error) {
            console.error("Confirmation error:", error);
            switch (error.name) {
                case "CodeMismatchException":
                    setServerError("The confirmation code is incorrect.");
                    break;

                case "ExpiredCodeException":
                    setServerError("Your confirmation code has expired");

                case "UserNotFoundException":
                    setServerError("The account could not be found.");
                    break;

                case "AliasExistsException":
                    setServerError("This email address is already associated with another account. Please sign in to your existing account.");
                    break;

                case "NotAuthorizedException":
                    setServerError("This account may already be confirmed.");

                default:
                    setServerError(
                        error.message || "Unable to confirm your account."
                    );
            }
        } finally {
            setSubmitting(false);
        }
    };

    const fields = [
        { key: "code", label: "Confirmation Code", type: "text", placeholder: "1234" },
    ];

    return (
        <>
            {showSuccess && (
                <SuccessBanner username={userName} onDone={onSuccess} />
            )}

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
                        <div style={{ color: "#555", fontFamily: "'DM Sans', sans-serif", fontSize: 14 }}>
                            Enter the confirmation code that was sent to your email.
                        </div>
                    </div>

                    {/* Card */}
                    <form
                        onSubmit={handleSubmit}
                        noValidate
                        style={{ background: "#0d0d0d", border: "1px solid #1e1e1e", borderRadius: 20, padding: 28 }}
                    >
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
                            {fields.map(({ key, label, type, placeholder, autoComplete }) => (
                                <div key={key}>
                                    <label style={labelStyle}>{label}</label>
                                    <input
                                        type={type}
                                        placeholder={placeholder}
                                        autoComplete={autoComplete}
                                        value={form[key]}
                                        onChange={(e) => {
                                            const val = e.target.value;
                                            setForm((f) => ({ ...f, [key]: val }));
                                            if (errors[key]) setErrors((prev) => ({ ...prev, [key]: null }));
                                        }}
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
                            type="submit"
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
                            onMouseEnter={(e) => { if (!submitting) e.currentTarget.style.background = "rgba(99,102,241,0.25)"; }}
                            onMouseLeave={(e) => { if (!submitting) e.currentTarget.style.background = "rgba(99,102,241,0.15)"; }}
                        >
                            {submitting ? "Confirming Sign up…" : "Confirm Sign up"}
                        </button>
                    </form>
                </div>
            </div>
        </>
    );
}
