// web/js/auth.js
import { apiFetch } from './api.js';
import { state } from './state.js';
import { renderNav } from './ui.js';

export const fetchCurrentUser = async () => {
    try {
        state.user = await apiFetch("/users/me");
    } catch (error) {
        state.user = null;
    }
    renderNav();
};

export const login = async (email, password) => {
    const formData = new URLSearchParams();
    formData.append("username", email);
    formData.append("password", password);

    await apiFetch("/auth/jwt/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: formData,
    });

    await fetchCurrentUser();
};

export const register = async (email, password) => {
    await apiFetch("/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
    });

    await login(email, password);
};

export const logout = async () => {
    try {
        await apiFetch("/auth/jwt/logout", { method: "POST" });
    } catch (error) {
        console.error("Logout failed, clearing client-side state anyway.", error);
    } finally {
        state.user = null;
        renderNav();
    }
};

export const completeOnboarding = async (onboardingData) => {
    await apiFetch("/me/onboarding", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(onboardingData),
    });
    await fetchCurrentUser();
};
