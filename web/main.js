document.addEventListener("DOMContentLoaded", () => {
    const API_BASE_URL = "http://localhost:8000/api/v1";
    let state = {
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
    };

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
        view.hidden = false;
        view.innerHTML = getModalContent(viewName);

        if (viewName === 'login') {
            document.getElementById("login-form").onsubmit = async (e) => {
                e.preventDefault();
                await login(e.target.elements["login-email"].value, e.target.elements["login-password"].value);
                view.hidden = true;
            };
        } else if (viewName === 'register') {
            document.getElementById("register-form").onsubmit = async (e) => {
                e.preventDefault();
                await register(e.target.elements["register-email"].value, e.target.elements["register-password"].value);
                view.hidden = true;
            };
        } else if (viewName === 'onboarding') {
            document.getElementById("onboarding-form").onsubmit = async (e) => {
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
        if (viewName === 'login') {
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
        if (viewName === 'register') {
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
        if (viewName === 'onboarding') {
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
        return '';
    }

    const init = async () => {
        // await fetchCurrentUser();
        renderNav();
    };

    init();
});
