// web/js/ui.js
import { state } from './state.js';
import { login, register, logout, completeOnboarding } from './auth.js';

export const ui = {
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
    ruleMatchesList: document.getElementById("rule-matches-list"),
    gptAnalysisList: document.getElementById("gpt-analysis-list"),
    downloadPdfBtn: document.getElementById("download-pdf-btn"),
    reanalyzeBtn: document.getElementById("reanalyze-btn"),
    usageBanner: document.getElementById("usage-banner"),
};

export const switchAppState = (stateName) => {
    Object.values(ui.appStates).forEach((el) => {
        if (!el) return;
        el.hidden = true;
    });
    if (ui.appStates[stateName]) {
        ui.appStates[stateName].hidden = false;
    }
};

export const renderNav = () => {
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

export const showModal = (viewName) => {
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

export const getModalContent = (viewName) => {
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

export const drawDonut = (score) => {
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

export const renderResults = (data) => {
    drawDonut(data.score);
    if (ui.riskLevel) ui.riskLevel.textContent = data.level;
    if (ui.triggersList) {
        ui.triggersList.innerHTML = (data.reasons || [])
            .map((reason) => `<li>${reason}</li>`)
            .join("");
    }

    if (ui.improvementsList) {
        ui.improvementsList.innerHTML = (data.recommendations || [])
            .map((rec) => `<li>${rec}</li>`)
            .join("");
    }

    if (ui.ruleMatchesList) {
        ui.ruleMatchesList.innerHTML = (data.rule_matches || [])
            .map(match => `<li><strong>${match.category} (${match.severity}):</strong> ${match.recommendation}</li>`)
            .join('');
    }

    if (ui.gptAnalysisList) {
        const gptAnalysis = data.gpt_analysis || {};
        const reasons = gptAnalysis.reasons || [];
        const recommendations = gptAnalysis.recommendations || [];
        ui.gptAnalysisList.innerHTML = [
            ...reasons.map(reason => `<li><strong>Reason:</strong> ${reason}</li>`),
            ...recommendations.map(rec => `<li><strong>Recommendation:</strong> ${rec}</li>`)
        ].join('');
    }
};

export const updateUsageBanner = (summary) => {
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
