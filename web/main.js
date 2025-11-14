document.addEventListener("DOMContentLoaded", () => {
    const API_BASE_URL = "http://localhost:8000/api/v1";
    let state = {
        file: null,
        user: null,
    };

    const ui = {
        views: {
            landing: document.getElementById("view-landing"),
            login: document.getElementById("view-login"),
            register: document.getElementById("view-register"),
            onboarding: document.getElementById("view-onboarding"),
            app: document.getElementById("view-app"),
            history: document.getElementById("view-history"),
            account: document.getElementById("view-account"),
        },
        mainNav: document.getElementById("main-nav"),
        showLoginBtn: document.getElementById("show-login-btn"),
        showRegisterBtn: document.getElementById("show-register-btn"),
        showLoginLink: document.getElementById("show-login-link"),
        showRegisterLink: document.getElementById("show-register-link"),
        loginForm: document.getElementById("login-form"),
        registerForm: document.getElementById("register-form"),
        onboardingForm: document.getElementById("onboarding-form"),
        logoutBtn: document.getElementById("logout-btn"),
        dropzone: document.getElementById("dropzone"),
        fileInput: document.getElementById("file-input"),
        historyList: document.getElementById("history-list"),
        accountDetails: document.getElementById("account-details"),
    };

    const switchView = (viewName) => {
        Object.values(ui.views).forEach(view => view.hidden = true);
        ui.views[viewName].hidden = false;
    };

    const apiFetch = async (endpoint, options = {}) => {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {credentials: 'include', ...options});
        if (!response.ok) {
            if (response.status === 401) logout();
            throw new Error(`API request failed: ${response.statusText}`);
        }
        if (response.status === 204) return; // No Content
        return response.json();
    };

    const login = async (email, password) => {
        const formData = new URLSearchParams();
        formData.append("username", email);
        formData.append("password", password);
        await apiFetch("/auth/jwt/login", {
            method: "POST",
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData,
        });
        await fetchCurrentUser();
        router();
    };

    const register = async (email, password) => {
        await apiFetch("/auth/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password }),
        });
        await login(email, password);
    };

    const logout = async () => {
        try {
            await apiFetch("/auth/jwt/logout", { method: "POST" });
        } catch (error) {
            console.error("Logout failed, clearing client-side state anyway.", error);
        } finally {
            state.user = null;
            ui.mainNav.hidden = true;
            router();
        }
    };

    const fetchCurrentUser = async () => {
        console.log("Before fetchCurrentUser:", state.user);
        try {
            state.user = await apiFetch("/users/me");
            ui.mainNav.hidden = false;
        } catch (error) {
            state.user = null;
        }
        console.log("After fetchCurrentUser:", state.user);
    };

    const completeOnboarding = async (onboardingData) => {
        console.log("Before completeOnboarding:", state.user);
        await apiFetch("/me/onboarding", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(onboardingData),
        });
        await fetchCurrentUser();
        console.log("After completeOnboarding:", state.user);
        router();
    };

    const router = () => {
        const hash = window.location.hash;
        console.log("Routing with hash:", hash, "and user:", state.user);

        if (!state.user) {
            if (hash === "#register") switchView("register");
            else if (hash === "#login") switchView("login");
            else switchView("landing");
            return;
        }

        if (state.user && !state.user.company_name) {
            switchView("onboarding");
            return;
        }

        if (hash === "#history") {
            // renderHistory(); // Implement this
            switchView("history");
        } else if (hash === "#account") {
            // renderAccount(); // Implement this
            switchView("account");
        } else {
            switchView("app");
        }
    };

    const setupEventListeners = () => {
        ui.showLoginBtn.onclick = () => window.location.hash = "login";
        ui.showRegisterBtn.onclick = () => window.location.hash = "register";
        ui.showLoginLink.onclick = () => window.location.hash = "login";
        ui.showRegisterLink.onclick = () => window.location.hash = "register";

        ui.loginForm.onsubmit = async (e) => {
            e.preventDefault();
            await login(e.target.elements["login-email"].value, e.target.elements["login-password"].value);
        };
        ui.registerForm.onsubmit = async (e) => {
            e.preventDefault();
            await register(e.target.elements["register-email"].value, e.target.elements["register-password"].value);
        };
        ui.onboardingForm.onsubmit = async (e) => {
            e.preventDefault();
            const data = {
                company_name: e.target.elements["onboarding-company-name"].value,
                sector: e.target.elements["onboarding-sector"].value,
                company_size: e.target.elements["onboarding-company-size"].value,
                country: e.target.elements["onboarding-country"].value,
                role: e.target.elements["onboarding-role"].value,
            };
            await completeOnboarding(data);
        };
        ui.logoutBtn.onclick = logout;
        window.onhashchange = router;
    };

    const init = async () => {
        await fetchCurrentUser();
        setupEventListeners();
        router();
    };

    init();
});
