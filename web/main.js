// web/main.js
import { apiFetch } from './js/api.js';
import { state } from './js/state.js';
import { ui, switchAppState, renderResults, updateUsageBanner } from './js/ui.js';
import { fetchCurrentUser } from './js/auth.js';

document.addEventListener("DOMContentLoaded", () => {
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

    const runProgressIndicator = () => {
        if (!ui.progressSteps) return;
        ui.progressSteps.forEach((step, index) => {
            step.classList.remove("active");
            setTimeout(() => step.classList.add("active"), index * 500);
        });
    };

    const fetchUsageSummary = async () => {
        try {
            const summary = await apiFetch("/usage/summary");
            updateUsageBanner(summary);
        } catch (error) {
            console.warn("Could not fetch usage summary", error);
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

    const init = async () => {
        await fetchCurrentUser();
        await fetchUsageSummary();
        setupUpload();
        setupResultsActions();
        switchAppState("landing");
    };

    init();
});
