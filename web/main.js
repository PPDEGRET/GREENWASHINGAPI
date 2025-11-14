document.addEventListener("DOMContentLoaded", () => {
    const API_BASE_URL = "http://localhost:8000/api/v1";

    let state = {
        file: null,
        user: null,
    };

    const ui = {
        mainNav: document.getElementById("main-nav"),
        views: {
            app: document.getElementById("view-app"),
            login: document.getElementById("view-login"),
            register: document.getElementById("view-register"),
            onboarding: document.getElementById("view-onboarding"),
            history: document.getElementById("view-history"),
            account: document.getElementById("view-account"),
        },
        appStates: {
            landing: document.getElementById("app-state-landing"),
            progress: document.getElementById("app-state-progress"),
            results: document.getElementById("app-state-results"),
        },
        dropzone: document.getElementById("dropzone"),
        fileInput: document.getElementById("file-input"),
        progressSteps: document.querySelectorAll(".progress-steps .step"),
        scoreDonut: document.getElementById("score-donut"),
        riskLevel: document.getElementById("risk-level"),
        triggersList: document.getElementById("triggers-list"),
        improvementsList: document.getElementById("improvements-list"),
        downloadPdfBtn: document.getElementById("download-pdf-btn"),
        reanalyzeBtn: document.getElementById("reanalyze-btn"),
        usageBanner: document.getElementById("usage-banner"),
    };

    // -----------------------------
    // Helper: switch app sub-state
    // -----------------------------
    const switchAppState = (stateName) => {
        Object.values(ui.appStates).forEach((el) => {
            if (!el) return;
            el.hidden = true;
        });
        if (ui.appStates[stateName]) {
            ui.appStates[stateName].hidden = false;
        }
    };

    // -----------------------------
    // Helper: generic API fetch
    // -----------------------------
    const apiFetch = async (endpoint, options = {}) => {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            credentials: "include",
            ...options,
        });

        const contentType = response.headers.get("content-type") || "";

        if (!response.ok) {
            let errorBody = null;
            try {
                if (contentType.includes("application/json")) {
                    errorBody = await response.json();
                } else {
                    errorBody = await response.text();
                }
            } catch (e) {
                errorBody = null;
            }

            if (response.status === 401) {
                // Unauthorized: clear user and refresh nav
                state.user = null;
                renderNav();
            }

            const error = new Error(`API request failed (${response.status})`);
            error.status = response.status;
            error.body = errorBody;
            throw error;
        }

        if (response.status === 204) return; // No content

        if (contentType.includes("application/json")) {
            return response.json();
        }
        return response;
    };

    // -----------------------------
    // Auth helpers
    // -----------------------------
    const fetchCurrentUser = async () => {
        try {
            state.user = await apiFetch("/users/me");
        } catch (error) {
            state.user = null;
        }
        renderNav();
    };

    const login = async (email, password) => {
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
            renderNav();
        }
    };

    const completeOnboarding = async (onboardingData) => {
        await apiFetch("/me/onboarding", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(onboardingData),
        });
        await fetchCurrentUser();
    };

    // -----------------------------
    // Navigation bar & modals
    // -----------------------------
    const renderNav = () => {
        if (state.user) {
            ui.mainNav.innerHTML = `
                <a href="#history" class="nav-link">History</a>
                <a href="#account" class="nav-link">Account</a>
                <button id="logout-btn" class="btn-secondary">Logout</button>
            `;
            document.getElementById("logout-btn").onclick = logout;
        } else {
            ui.mainNav.innerHTML = `
                <button id="show-login-btn" class="btn-primary">Login / Register</button>
            `;
            document.getElementById("show-login-btn").onclick = () => showModal("login");
        }
    };

    const showModal = (viewName) => {
        const view = ui.views[viewName];
        if (!view) return;

        view.hidden = false;
        view.innerHTML = getModalContent(viewName);

        if (viewName === "login") {
            const form = document.getElementById("login-form");
            form.onsubmit = async (e) => {
                e.preventDefault();
                await login(
                    e.target.elements["login-email"].value,
                    e.target.elements["login-password"].value,
                );
                view.hidden = true;
            };
            const showRegisterLink = document.getElementById("show-register-link");
            if (showRegisterLink) {
                showRegisterLink.onclick = (e) => {
                    e.preventDefault();
                    view.hidden = true;
                    showModal("register");
                };
            }
        } else if (viewName === "register") {
            const form = document.getElementById("register-form");
            form.onsubmit = async (e) => {
                e.preventDefault();
                await register(
                    e.target.elements["register-email"].value,
                    e.target.elements["register-password"].value,
                );
                view.hidden = true;
            };
            const showLoginLink = document.getElementById("show-login-link");
            if (showLoginLink) {
                showLoginLink.onclick = (e) => {
                    e.preventDefault();
                    view.hidden = true;
                    showModal("login");
                };
            }
        } else if (viewName === "onboarding") {
            const form = document.getElementById("onboarding-form");
            form.onsubmit = async (e) => {
                e.preventDefault();
                const data = {
                    company_name: e.target.elements["onboarding-company-name"].value,
                    sector: e.target.elements["onboarding-sector"].value,
                    company_size: e.target.elements["onboarding-company-size"].value,
                    country: e.target.elements["onboarding-country"].value,
                    role: e.target.elements["onboarding-role"].value,
                };
                await completeOnboarding(data);
                view.hidden = true;
            };
        }
    };

    const getModalContent = (viewName) => {
        if (viewName === "login") {
            return `
                <div class="modal-content">
                    <h2>Login</h2>
                    <form id="login-form">
                        <input type="email" id="login-email" placeholder="Email" required />
                        <input type="password" id="login-password" placeholder="Password" required />
                        <button type="submit" class="btn-primary">Login</button>
                        <p>Don't have an account? <a href="#" id="show-register-link">Register here</a></p>
                    </form>
                </div>
            `;
        }
        if (viewName === "register") {
            return `
                <div class="modal-content">
                    <h2>Register</h2>
                    <form id="register-form">
                        <input type="email" id="register-email" placeholder="Email" required />
                        <input type="password" id="register-password" placeholder="Password" required />
                        <button type="submit" class="btn-primary">Register</button>
                        <p>Already have an account? <a href="#" id="show-login-link">Login here</a></p>
                    </form>
                </div>
            `;
        }
        if (viewName === "onboarding") {
            return `
                <div class="modal-content">
                    <h2>Welcome!</h2>
                    <p>Please complete your profile to continue.</p>
                    <form id="onboarding-form">
                        <input type="text" id="onboarding-company-name" placeholder="Company Name" />
                        <input type="text" id="onboarding-sector" placeholder="Sector" />
                        <input type="text" id="onboarding-company-size" placeholder="Company Size" />
                        <input type="text" id="onboarding-country" placeholder="Country" />
                        <input type="text" id="onboarding-role" placeholder="Role" />
                        <button type="submit" class="btn-primary">Save</button>
                    </form>
                </div>
            `;
        }
        return "";
    };

    // -----------------------------
    // Drag & drop + analysis
    // -----------------------------
    const runProgressIndicator = () => {
        if (!ui.progressSteps) return;
        ui.progressSteps.forEach((step, index) => {
            step.classList.remove("active");
            setTimeout(() => step.classList.add("active"), index * 500);
        });
    };

    const drawDonut = (score) => {
        if (!ui.scoreDonut) return;
        const pct = Math.max(0, Math.min(100, score || 0));
        const color = score > 70 ? "#f44336" : score > 30 ? "#ff9800" : "#4CAF50";
        const html = `
            <svg viewBox="0 0 36 36" class="score-svg">
                <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      fill="none" stroke="#e6e6e6" stroke-width="3"></path>
                <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      fill="none" stroke="${color}" stroke-width="3"
                      stroke-dasharray="${pct}, 100"></path>
                <text x="18" y="22" text-anchor="middle" font-size="12" class="score-text">${pct}</text>
            </svg>`;
        ui.scoreDonut.innerHTML = html;
    };

    const renderResults = (data) => {
        drawDonut(data.score);
        if (ui.riskLevel) ui.riskLevel.textContent = data.level;
        if (ui.triggersList) {
            ui.triggersList.innerHTML = (data.reasons || [])
                .map((reason) => `<li>${reason}</li>`)
                .join("");
        }

        let recs = [];
        if (Object.prototype.hasOwnProperty.call(data, "recommendations")) {
            recs = Array.isArray(data.recommendations) ? data.recommendations : [];
        } else {
            recs = [
                "Clarify the environmental claim with scope and metrics.",
                "Provide external certifications or third-party verification.",
                "Avoid absolute expressions such as '100% sustainable'.",
            ];
        }

        if (ui.improvementsList) {
            ui.improvementsList.innerHTML = "";
            recs.forEach((rec) => {
                const li = document.createElement("li");
                const text = rec && typeof rec === "object" ? rec.message || "" : String(rec || "");
                li.textContent = text;
                ui.improvementsList.appendChild(li);
            });
        }
    };

    const updateUsageBanner = (summary) => {
        if (!ui.usageBanner || !summary) return;

        const detail = summary.detail || summary; // Support FastAPI error shape {detail: {...}}
        const used = typeof detail.used_today === "number" ? detail.used_today : null;
        const remaining = typeof detail.remaining_today === "number" ? detail.remaining_today : null;
        const limit = typeof detail.limit === "number" ? detail.limit : null;
        const isPremium = Boolean(detail.is_premium);

        if (isPremium) {
            ui.usageBanner.textContent = "You have unlimited analyses with your premium account.";
            ui.usageBanner.hidden = false;
            return;
        }

        if (limit != null && remaining != null) {
            const usedDisplay = used != null ? used : limit - remaining;
            ui.usageBanner.textContent = `Free analyses today: ${Math.max(0, remaining)} / ${limit} (used ${Math.max(0, usedDisplay)}).`;
            ui.usageBanner.hidden = false;
        } else {
            ui.usageBanner.hidden = true;
        }
    };

    const fetchUsageSummary = async () => {
        try {
            const summary = await apiFetch("/usage/summary");
            updateUsageBanner(summary);
        } catch (error) {
            console.warn("Could not fetch usage summary", error);
        }
    };

    const handleFileUpload = async (file) => {
        if (!file) return;
        state.file = file;
        switchAppState("progress");
        runProgressIndicator();

        const formData = new FormData();
        formData.append("file", file);

        try {
            const data = await apiFetch("/analyze", {
                method: "POST",
                body: formData,
            });

            renderResults(data);
            await fetchUsageSummary();
            switchAppState("results");
        } catch (error) {
            console.error("Error during analysis:", error);
            switchAppState("landing");

            // Handle daily limit exceeded with a friendly message and updated banner
            if (error.status === 429 && error.body) {
                const detail = error.body.detail || error.body;
                updateUsageBanner(detail);

                const limit = detail.limit;
                const remaining = detail.remaining_today;
                let message = "Daily analysis limit reached.";
                if (typeof limit === "number" && typeof remaining === "number") {
                    if (remaining <= 0) {
                        message = `You reached your daily limit of ${limit} free analyses. Please come back tomorrow or upgrade to premium.`;
                    } else {
                        message = `You have ${remaining} analysis${remaining === 1 ? "" : "es"} left today (limit: ${limit}).`;
                    }
                }
                alert(message);
            } else {
                alert("Analysis failed. Please try again.");
            }
        }
    };

    const setupUpload = () => {
        if (!ui.dropzone || !ui.fileInput) return;

        ui.dropzone.addEventListener("click", () => ui.fileInput.click());

        ui.dropzone.addEventListener("dragover", (e) => {
            e.preventDefault();
            ui.dropzone.classList.add("dragover");
        });

        ui.dropzone.addEventListener("dragleave", () => {
            ui.dropzone.classList.remove("dragover");
        });

        ui.dropzone.addEventListener("drop", (e) => {
            e.preventDefault();
            ui.dropzone.classList.remove("dragover");
            if (e.dataTransfer.files.length) {
                handleFileUpload(e.dataTransfer.files[0]);
            }
        });

        ui.fileInput.addEventListener("change", (e) => {
            if (e.target.files.length) {
                handleFileUpload(e.target.files[0]);
            }
        });
    };

    const setupResultsActions = () => {
        if (ui.downloadPdfBtn) {
            ui.downloadPdfBtn.addEventListener("click", async () => {
                if (!state.file) return;
                const formData = new FormData();
                formData.append("file", state.file);
                try {
                    const response = await apiFetch("/report.pdf", {
                        method: "POST",
                        body: formData,
                    });
                    const blob = await response.blob();
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement("a");
                    a.href = url;
                    a.download = "GreenCheck_Report.pdf";
                    a.click();
                    URL.revokeObjectURL(url);
                } catch (error) {
                    console.error("Error downloading PDF:", error);
                }
            });
        }

        if (ui.reanalyzeBtn) {
            ui.reanalyzeBtn.addEventListener("click", () => {
                state.file = null;
                switchAppState("landing");
            });
        }
    };

    // -----------------------------
    // Init
    // -----------------------------
    const init = async () => {
        await fetchCurrentUser();
        await fetchUsageSummary();
        setupUpload();
        setupResultsActions();
        switchAppState("landing");
    };

    init();
});
