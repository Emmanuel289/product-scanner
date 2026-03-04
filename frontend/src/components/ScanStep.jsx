import { useState, useRef, useEffect, useCallback } from "react";
import { API_URL } from "../constants";
import { CameraIcon, UploadIcon } from "./icons/Icons";

const SearchIcon = () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="11" cy="11" r="8" />
        <path d="M21 21l-4.35-4.35" />
    </svg>
);

const SpinnerIcon = () => (
    <div style={{
        width: 14, height: 14, borderRadius: "50%",
        border: "2px solid #333", borderTopColor: "#6366f1",
        animation: "spin 0.7s linear infinite", flexShrink: 0,
    }} />
);

export default function ScanStep({ onResult, onLoading }) {
    const [preview, setPreview] = useState(null);
    const [cameraActive, setCameraActive] = useState(false);
    const [searchMode, setSearchMode] = useState(false);
    const [searchQuery, setSearchQuery] = useState("");
    const [searching, setSearching] = useState(false);
    const [searchResults, setSearchResults] = useState(null); // null = no search yet

    const fileRef = useRef();
    const cameraFileRef = useRef();
    const videoRef = useRef();
    const streamRef = useRef();
    const searchRef = useRef();
    const debounceRef = useRef();

    // ── Camera ──────────────────────────────────────────────────────────────────
    const startCamera = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: { ideal: "environment" }, width: { ideal: 1280 }, height: { ideal: 720 } },
            });
            streamRef.current = stream;
            setCameraActive(true);
            setTimeout(() => { if (videoRef.current) videoRef.current.srcObject = stream; }, 50);
        } catch {
            cameraFileRef.current?.click();
        }
    };

    const stopCamera = () => {
        streamRef.current?.getTracks().forEach((t) => t.stop());
        streamRef.current = null;
        setCameraActive(false);
    };

    const captureFrame = () => {
        const video = videoRef.current;
        const canvas = document.createElement("canvas");
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext("2d").drawImage(video, 0, 0);
        setPreview(canvas.toDataURL("image/jpeg", 0.92));
        stopCamera();
    };

    useEffect(() => () => stopCamera(), []);

    // ── File handling ────────────────────────────────────────────────────────────
    const handleFile = (f) => {
        if (!f || !f.type.startsWith("image/")) return;
        const reader = new FileReader();
        reader.onload = (e) => setPreview(e.target.result);
        reader.readAsDataURL(f);
    };

    const retake = () => { setPreview(null); stopCamera(); };

    const handleAnalyze = async () => {
        if (!preview) return;
        onLoading(true);
        try {
            const base64 = preview.split(",")[1];
            const res = await fetch(API_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ image_base64: base64 }),
            });
            const data = await res.json();
            onResult(data, base64);
        } catch (err) {
            onResult({ error: true, message: err.message });
        } finally {
            onLoading(false);
        }
    };

    // ── Name search ──────────────────────────────────────────────────────────────
    const runSearch = useCallback(async (query) => {
        if (!query || query.trim().length < 3) { setSearchResults(null); setSearching(false); return; }
        setSearching(true);
        try {
            const res = await fetch(API_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ product_name: query.trim() }),
            });
            const data = await res.json();
            setSearchResults(data);
        } catch {
            setSearchResults({ error: true });
        } finally {
            setSearching(false);
        }
    }, []);

    const handleSearchInput = (e) => {
        const q = e.target.value;
        setSearchQuery(q);
        setSearchResults(null);
        clearTimeout(debounceRef.current);
        debounceRef.current = setTimeout(() => runSearch(q), 350);
    };

    const handleSearchSelect = () => {
        if (!searchResults || searchResults.status?.includes("Not Found") || searchResults.error) return;
        onResult(searchResults, null);
    };

    const openSearch = () => {
        setSearchMode(true);
        setTimeout(() => searchRef.current?.focus(), 50);
    };

    const closeSearch = () => {
        setSearchMode(false);
        setSearchQuery("");
        setSearchResults(null);
        clearTimeout(debounceRef.current);
    };

    // ── Live camera view ────────────────────────────────────────────────────────
    if (cameraActive) return (
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <div style={{ position: "relative", borderRadius: 16, overflow: "hidden", background: "#000", aspectRatio: "4/3" }}>
                <video ref={videoRef} autoPlay playsInline muted style={{ width: "100%", height: "100%", objectFit: "cover", display: "block" }} />
                <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", pointerEvents: "none" }}>
                    <div style={{ width: "72%", aspectRatio: "3/2", border: "2px solid rgba(99,102,241,0.8)", borderRadius: 12, boxShadow: "0 0 0 9999px rgba(0,0,0,0.45)", position: "relative" }}>
                        {[
                            { top: -2, left: -2, borderTop: "3px solid #6366f1", borderLeft: "3px solid #6366f1", borderRadius: "4px 0 0 0" },
                            { top: -2, right: -2, borderTop: "3px solid #6366f1", borderRight: "3px solid #6366f1", borderRadius: "0 4px 0 0" },
                            { bottom: -2, left: -2, borderBottom: "3px solid #6366f1", borderLeft: "3px solid #6366f1", borderRadius: "0 0 0 4px" },
                            { bottom: -2, right: -2, borderBottom: "3px solid #6366f1", borderRight: "3px solid #6366f1", borderRadius: "0 0 4px 0" },
                        ].map((style, i) => <div key={i} style={{ position: "absolute", width: 20, height: 20, ...style }} />)}
                    </div>
                </div>
                <div style={{ position: "absolute", bottom: 12, left: 0, right: 0, textAlign: "center" }}>
                    <span style={{ color: "rgba(255,255,255,0.5)", fontFamily: "'DM Sans', sans-serif", fontSize: 12 }}>Point at product label</span>
                </div>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
                <button onClick={retake} style={{ background: "#141414", border: "1px solid #2a2a2a", borderRadius: 12, padding: "14px", color: "#888", cursor: "pointer", fontFamily: "'DM Sans', sans-serif", fontSize: 14 }}>Cancel</button>
                <button onClick={captureFrame} style={{ background: "linear-gradient(135deg, #6366f1, #8b5cf6)", border: "none", borderRadius: 12, padding: "14px", color: "#fff", fontSize: 14, fontWeight: 700, cursor: "pointer", fontFamily: "'DM Sans', sans-serif", boxShadow: "0 0 20px rgba(99,102,241,0.4)" }}>Capture</button>
            </div>
        </div>
    );

    // ── Preview + analyze ────────────────────────────────────────────────────────
    if (preview) return (
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <div style={{ position: "relative", borderRadius: 16, overflow: "hidden" }}>
                <img src={preview} alt="Product" style={{ width: "100%", maxHeight: 300, objectFit: "cover", display: "block" }} />
                <div style={{ position: "absolute", inset: 0, background: "linear-gradient(to top, rgba(0,0,0,0.8) 0%, transparent 60%)", display: "flex", alignItems: "flex-end", padding: 16 }}>
                    <button onClick={retake} style={{ background: "rgba(0,0,0,0.5)", border: "1px solid rgba(255,255,255,0.15)", borderRadius: 8, padding: "6px 14px", color: "#ccc", cursor: "pointer", fontFamily: "'DM Sans', sans-serif", fontSize: 13, backdropFilter: "blur(8px)" }}>Retake</button>
                </div>
            </div>
            <button
                onClick={handleAnalyze}
                onMouseEnter={e => { e.currentTarget.style.transform = "scale(1.02)"; e.currentTarget.style.boxShadow = "0 0 32px rgba(99,102,241,0.6)"; }}
                onMouseLeave={e => { e.currentTarget.style.transform = "scale(1)"; e.currentTarget.style.boxShadow = "0 0 24px rgba(99,102,241,0.4)"; }}
                style={{ background: "linear-gradient(135deg, #6366f1, #8b5cf6)", border: "none", borderRadius: 12, padding: "16px 24px", color: "#fff", fontSize: 16, fontWeight: 700, cursor: "pointer", fontFamily: "'DM Sans', sans-serif", letterSpacing: 0.5, boxShadow: "0 0 24px rgba(99,102,241,0.4)", transition: "transform 0.15s ease, box-shadow 0.15s ease" }}
            >
                Scan Product
            </button>
        </div>
    );

    // ── Default: buttons + search ────────────────────────────────────────────────
    return (
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>

            {/* Primary actions */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                <button
                    onClick={startCamera}
                    onMouseEnter={e => e.currentTarget.style.borderColor = "#6366f1"}
                    onMouseLeave={e => e.currentTarget.style.borderColor = "#2a2a2a"}
                    style={{ background: "#0d0d0d", border: "1px solid #2a2a2a", borderRadius: 14, padding: "28px 16px", cursor: "pointer", display: "flex", flexDirection: "column", alignItems: "center", gap: 10, transition: "border-color 0.15s ease" }}
                >
                    <div style={{ color: "#6366f1" }}><CameraIcon /></div>
                    <span style={{ color: "#fff", fontFamily: "'DM Sans', sans-serif", fontWeight: 600, fontSize: 14 }}>Take Photo</span>
                </button>

                <div
                    onClick={() => fileRef.current?.click()}
                    onMouseEnter={e => { e.currentTarget.style.borderColor = "#6366f1"; }}
                    onMouseLeave={e => { e.currentTarget.style.borderColor = "#2a2a2a"; }}
                    style={{ background: "#0d0d0d", border: "1px solid #2a2a2a", borderRadius: 14, padding: "28px 16px", cursor: "pointer", display: "flex", flexDirection: "column", alignItems: "center", gap: 10, transition: "border-color 0.15s ease" }}
                >
                    <div style={{ color: "#6366f1" }}><UploadIcon /></div>
                    <span style={{ color: "#fff", fontFamily: "'DM Sans', sans-serif", fontWeight: 600, fontSize: 14 }}>Upload Image</span>
                </div>
            </div>

            {/* Divider */}
            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <div style={{ flex: 1, height: 1, background: "#1a1a1a" }} />
                <span style={{ color: "#333", fontFamily: "'DM Sans', sans-serif", fontSize: 11, letterSpacing: 1, textTransform: "uppercase" }}>or</span>
                <div style={{ flex: 1, height: 1, background: "#1a1a1a" }} />
            </div>

            {/* Search fallback */}
            {!searchMode ? (
                <button
                    onClick={openSearch}
                    onMouseEnter={e => { e.currentTarget.style.borderColor = "#6366f1"; e.currentTarget.style.color = "#aaa"; }}
                    onMouseLeave={e => { e.currentTarget.style.borderColor = "#1e1e1e"; e.currentTarget.style.color = "#444"; }}
                    style={{ background: "transparent", border: "1px solid #1e1e1e", borderRadius: 12, padding: "14px 20px", color: "#444", cursor: "pointer", fontFamily: "'DM Sans', sans-serif", fontSize: 14, display: "flex", alignItems: "center", justifyContent: "center", gap: 8, transition: "all 0.15s ease" }}
                >
                    <SearchIcon />
                    Can't scan? Search a product by name
                </button>
            ) : (
                <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>

                    {/* Search input */}
                    <div style={{ position: "relative", display: "flex", alignItems: "center" }}>
                        <div style={{ position: "absolute", left: 14, color: "#555", display: "flex" }}>
                            {searching ? <SpinnerIcon /> : <SearchIcon />}
                        </div>
                        <input
                            ref={searchRef}
                            type="text"
                            value={searchQuery}
                            onChange={handleSearchInput}
                            placeholder="e.g. La Roche-Posay Toleriane..."
                            style={{
                                width: "100%", boxSizing: "border-box",
                                background: "#0d0d0d", border: "1px solid #6366f1",
                                borderRadius: 12, padding: "14px 44px 14px 42px",
                                color: "#fff", fontFamily: "'DM Sans', sans-serif", fontSize: 14,
                                outline: "none",
                            }}
                        />
                        <button
                            onClick={closeSearch}
                            style={{ position: "absolute", right: 12, background: "none", border: "none", color: "#444", cursor: "pointer", fontSize: 18, lineHeight: 1, padding: 2 }}
                        >×</button>
                    </div>

                    {/* Results */}
                    {searchResults && !searching && (
                        searchResults.error || searchResults.status?.includes("Not Found") ? (
                            <div style={{ background: "#0d0d0d", border: "1px solid #1e1e1e", borderRadius: 12, padding: "14px 16px", color: "#555", fontFamily: "'DM Sans', sans-serif", fontSize: 13, textAlign: "center" }}>
                                No product found — try a different name
                            </div>
                        ) : (
                            <button
                                onClick={handleSearchSelect}
                                onMouseEnter={e => e.currentTarget.style.borderColor = "#6366f1"}
                                onMouseLeave={e => e.currentTarget.style.borderColor = "#2a2a2a"}
                                style={{ background: "#0d0d0d", border: "1px solid #2a2a2a", borderRadius: 12, padding: "14px 16px", cursor: "pointer", textAlign: "left", transition: "border-color 0.15s ease", width: "100%" }}
                            >
                                <div style={{ color: "#555", fontFamily: "'DM Sans', sans-serif", fontSize: 11, letterSpacing: 1.5, textTransform: "uppercase", marginBottom: 4 }}>
                                    {searchResults.brand}
                                </div>
                                <div style={{ color: "#fff", fontFamily: "'DM Serif Display', serif", fontSize: 16, lineHeight: 1.3 }}>
                                    {searchResults.product_name}
                                </div>
                                <div style={{ color: "#6366f1", fontFamily: "'DM Sans', sans-serif", fontSize: 12, marginTop: 6 }}>
                                    Tap to view →
                                </div>
                            </button>
                        )
                    )}
                </div>
            )}

            {/* Hidden inputs */}
            <input ref={fileRef} type="file" accept="image/*" style={{ display: "none" }} onChange={e => handleFile(e.target.files[0])} />
            <input ref={cameraFileRef} type="file" accept="image/*" capture="environment" style={{ display: "none" }} onChange={e => handleFile(e.target.files[0])} />
        </div>
    );
}
