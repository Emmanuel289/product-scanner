import { useState } from "react";
import { signOut } from "aws-amplify/auth";

export function useAuth() {
    const [currentUser, setCurrentUser] = useState(null);
    const [pendingUsername, setPendingUsername] = useState(null);
    const [authPhase, setAuthPhase] = useState("login");
    const [authError, setAuthError] = useState(null);

    // Successful login
    const handleAuthSuccess = (data) => {
        setAuthError(null);
        setPendingUsername(null);
        setCurrentUser(data);
        setAuthPhase("app");
    };

    // Signup requires email confirmation
    const handleConfirmSignup = (username) => {
        setAuthError(null);
        setCurrentUser(null);
        setPendingUsername(username);
        setAuthPhase("confirmsignup");
    };

    // Signup completed without requiring confirmation
    const handleSignupComplete = () => {
        setAuthError(null);
        setPendingUsername(null);;
        setAuthPhase("login");
    }

    // Confirmation completed
    const handleConfirmationSuccess = () => {
        setAuthError(null);
        setPendingUsername(null);
        setCurrentUser(null);
        setAuthPhase("login");
    }

    // Centralized Logout
    const handleLogout = async (onReset) => {
        setAuthError(null);

        try {
            await signOut();
        } catch (error) {
            setAuthError("Sign out encountered an error.");
        }

        setCurrentUser(null);
        setPendingUsername(null);
        setAuthPhase("login");
        onReset?.();
    };

    return {
        currentUser,
        pendingUsername,
        authPhase,
        setAuthPhase,
        authError,
        setAuthError,
        handleAuthSuccess,
        handleConfirmSignup,
        handleSignupComplete,
        handleConfirmationSuccess,
        handleLogout,
    };
}
