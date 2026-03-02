import { useState, useRef, useEffect } from "react";
import { API_ENDPOINT } from "../constants";
import { CameraIcon, UploadIcon } from "./icons/Icons";

export default function ScanStep({ onResult, onLoading }) {
    const [preview, setPreview] = useState(null);
    const [cameraActive, setCameraActive] = useState(false);
    const [dragging, setDragging] = useState(false);
    const fileRef = useRef();
    const cameraFileRef = useRef(); // fallback for mobile native camera
    const videoRef = useRef();
    const streamRef = useRef();

    // ── Start live camera stream ──
    const startCamera = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: { ideal: "environment" }, width: { ideal: 1280 }, height: { ideal: 720 } },
            });
            streamRef.current = stream;
            setCameraActive(true);
            setTimeout(() => {
                if (videoRef.current) videoRef.current.srcObject = stream;
            }, 50);
        } catch {
            cameraFileRef.current?.click();
        }
    };

    // ── Stop stream ──
    const stopCamera = () => {
        streamRef.current?.getTracks().forEach((t) => t.stop());
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
        e.preventDefault();
        setDragging(false);
        handleFile(e.dataTransfer.files[0]);
    };

    // ── Stop camera on unmount ──
    useEffect(() => () => stopCamera(), []);

    const retake = () => {
        setPreview(null);
        stopCamera();
    };

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
            onResult(data, base64);
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
                    ref={videoRef} autoPlay playsInline muted
                    style={{ width: "100%", height: "100%", objectFit: "cover", display: "block" }}
                />
                {/* Viewfinder overlay */}
                <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", pointerEvents: "none" }}>
                    <div style={{ width: "72%", aspectRatio: "3/2", border: "2px solid rgba(99,102,241,0.8)", borderRadius: 12, boxShadow: "0 0 0 9999px rgba(0,0,0,0.45)", position: "relative" }}>
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
                <button onClick={retake} style={{ background: "#141414", border: "1px solid #2a2a2a", borderRadius: 12, padding: "14px", color: "#888", cursor: "pointer", fontFamily: "'DM Sans', sans-serif", fontSize: 14 }}>
                    Cancel
                </button>
                <button onClick={captureFrame} style={{ background: "linear-gradient(135deg, #6366f1, #8b5cf6)", border: "none", borderRadius: 12, padding: "14px", color: "#fff", fontSize: 14, fontWeight: 700, cursor: "pointer", fontFamily: "'DM Sans', sans-serif", boxShadow: "0 0 20px rgba(99,102,241,0.4)" }}>
                    Capture
                </button>
            </div>
        </div>
    );

    // ── Preview + analyze ──
    if (preview) return (
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <div style={{ position: "relative", borderRadius: 16, overflow: "hidden" }}>
                <img src={preview} alt="Product" style={{ width: "100%", maxHeight: 300, objectFit: "cover", display: "block" }} />
                <div style={{ position: "absolute", inset: 0, background: "linear-gradient(to top, rgba(0,0,0,0.8) 0%, transparent 60%)", display: "flex", alignItems: "flex-end", padding: 16 }}>
                    <button onClick={retake} style={{ background: "rgba(0,0,0,0.5)", border: "1px solid rgba(255,255,255,0.15)", borderRadius: 8, padding: "6px 14px", color: "#ccc", cursor: "pointer", fontFamily: "'DM Sans', sans-serif", fontSize: 13, backdropFilter: "blur(8px)" }}>
                        Retake
                    </button>
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

    // ── Default: two equal entry buttons + drag zone ──
    return (
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>

                {/* Take Photo */}
                <button
                    onClick={startCamera}
                    onMouseEnter={e => e.currentTarget.style.borderColor = "#6366f1"}
                    onMouseLeave={e => e.currentTarget.style.borderColor = "#2a2a2a"}
                    style={{ background: "#0d0d0d", border: "1px solid #2a2a2a", borderRadius: 14, padding: "28px 16px", cursor: "pointer", display: "flex", flexDirection: "column", alignItems: "center", gap: 10, transition: "border-color 0.15s ease" }}
                >
                    <div style={{ color: "#6366f1" }}><CameraIcon /></div>
                    <span style={{ color: "#fff", fontFamily: "'DM Sans', sans-serif", fontWeight: 600, fontSize: 14 }}>Take Photo</span>
                    <span style={{ color: "#555", fontFamily: "'DM Sans', sans-serif", fontSize: 12 }}>Use your camera</span>
                </button>

                {/* Upload */}
                <div
                    onClick={() => fileRef.current?.click()}
                    onDragOver={e => { e.preventDefault(); setDragging(true); }}
                    onDragLeave={() => setDragging(false)}
                    onDrop={handleDrop}
                    onMouseEnter={e => { if (!dragging) e.currentTarget.style.borderColor = "#6366f1"; }}
                    onMouseLeave={e => { if (!dragging) e.currentTarget.style.borderColor = "#2a2a2a"; }}
                    style={{ background: dragging ? "rgba(99,102,241,0.06)" : "#0d0d0d", border: `1px solid ${dragging ? "#6366f1" : "#2a2a2a"}`, borderRadius: 14, padding: "28px 16px", cursor: "pointer", display: "flex", flexDirection: "column", alignItems: "center", gap: 10, transition: "border-color 0.15s ease" }}
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
            <input ref={fileRef} type="file" accept="image/*" style={{ display: "none" }} onChange={e => handleFile(e.target.files[0])} />
            <input ref={cameraFileRef} type="file" accept="image/*" capture="environment" style={{ display: "none" }} onChange={e => handleFile(e.target.files[0])} />
        </div>
    );
}
