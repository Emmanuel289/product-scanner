import { useState } from "react";

export function useScanner() {
    const [phase, setPhase] = useState("scan");
    const [result, setResult] = useState(null);
    const [imageBase64, setImageBase64] = useState(null);
    const [history, setHistory] = useState(["scan"]);
    const [historyIndex, setHistoryIndex] = useState(0);

    const navigateTo = (newPhase) => {
        if (newPhase === "loading") {
            setPhase("loading");
            return;
        }
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

    const handleResult = (data, b64) => {
        setResult(data);
        setImageBase64(b64);
        navigateTo("result");
    };

    const handleLoading = (v) => { if (v) navigateTo("loading"); };

    const handleReset = () => {
        setResult(null);
        setImageBase64(null);
        setHistory(["scan"]);
        setHistoryIndex(0);
        setPhase("scan");
    };

    const canGoBack = historyIndex > 0 && phase !== "loading";
    const canGoForward = historyIndex < history.length - 1 && phase !== "loading";

    return {
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
    };
}
