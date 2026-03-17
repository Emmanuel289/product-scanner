import { useState } from "react";
import { API_URL } from "../constants";

export function useAuth() {
    const [currentUser, setCurrentUser] = useState(null);
    const [authPhase, setAuthPhase] = useState("login");
    const [authError, setAuthError] = useState(null);

    const handleAuthSuccess = (data) => {
        // Set the current user data before updating auth phase to avoid
        // a render where auth phase is "app" but the current user is null
        setCurrentUser(data);
        setAuthPhase("app");
    };

    const handleLogoutSuccess = (onReset) => {
        // Remove the current user before updating auth phase
        // to prevent a render where the auth phase is "login"
        // while there's a current user
        setCurrentUser(null);
        setAuthPhase("login");
        // Reset scanner state after auth phase is set to "login"
        // so the scan history doesn't briefly flash before the
        // login screen renders
        onReset();
    }

    const handleLogout = async (onReset) => {
        if (!currentUser) {
            setAuthPhase("login");
            return;
        }
        const logoutUrl = `${API_URL}/logout`;
        const payload = {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(currentUser),
        };
        try {
            const res = await fetch(logoutUrl, payload);
            const data = await res.json();
            if (!res.ok) {
                setAuthError(data.detail || "Sign out failed. Check your connection.");
                return;
            }
            setAuthError(null);
            handleLogoutSuccess(onReset);
        } catch (error) {
            setAuthError(`Failed to sign out the user. ${error}`);
        }
    };

    return {
        currentUser,
        authPhase,
        setAuthPhase,
        authError,
        handleAuthSuccess,
        handleLogout,
    };
}
