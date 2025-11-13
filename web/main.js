document.addEventListener("DOMContentLoaded", () => {
    const API_BASE_URL = "http://localhost:8000/api/v1";

    const state = {
        file: null,
    };

    const ui = {
        states: {
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
    };

    const switchState = (newState) => {
        Object.values(ui.states).forEach(stateEl => stateEl.hidden = true);
        ui.states[newState].hidden = false;
    };

    const handleFileUpload = async (file) => {
        state.file = file;
        switchState("progress");
        runProgressIndicator();

        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await fetch(`${API_BASE_URL}/analyze`, {
                method: "POST",
                body: formData,
            });
            if (!response.ok) throw new Error("Analysis failed");
            const data = await response.json();
            renderResults(data);
            switchState("results");
        } catch (error) {
            console.error("Error during analysis:", error);
            alert("Analysis failed. Please try again.");
            switchState("landing");
        }
    };

    const runProgressIndicator = () => {
        ui.progressSteps.forEach((step, index) => {
            setTimeout(() => step.classList.add("active"), index * 500);
        });
    };

    const renderResults = (data) => {
        drawDonut(data.score);
        ui.riskLevel.textContent = data.level;
        ui.triggersList.innerHTML = (data.reasons || []).map(reason => `<li>${reason}</li>`).join('');

        const recommendations = data.recommendations || [];
        ui.improvementsList.innerHTML = ""; // Clear existing recommendations

        if (recommendations.length === 0) {
            // Display a default message if no recommendations are provided
            const li = document.createElement("li");
            li.textContent = "No specific recommendations available. Ensure claims are clear and verifiable.";
            li.className = "recommendation-item severity-default";
            ui.improvementsList.appendChild(li);
            return;
        }

        // Sort recommendations by severity (highest first)
        recommendations.sort((a, b) => b.severity - a.severity);

        recommendations.forEach(rec => {
            const li = document.createElement("li");
            li.className = `recommendation-item severity-${rec.severity}`;

            const severityIndicator = document.createElement("span");
            severityIndicator.className = "severity-indicator";
            severityIndicator.setAttribute("aria-hidden", "true");

            const message = document.createElement("span");
            message.textContent = rec.message;

            li.appendChild(severityIndicator);
            li.appendChild(message);

            ui.improvementsList.appendChild(li);
        });
    };

    const drawDonut = (score) => {
        const pct = Math.max(0, Math.min(100, score || 0));
        const html = `
            <svg viewBox="0 0 36 36" class="score-svg">
                <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      fill="none" stroke="#e6e6e6" stroke-width="3"></path>
                <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      fill="none" stroke="${score > 70 ? '#f44336' : score > 30 ? '#ff9800' : '#4CAF50'}" stroke-width="3"
                      stroke-dasharray="${pct}, 100"></path>
                <text x="18" y="22" text-anchor="middle" font-size="12" class="score-text">${pct}</text>
            </svg>`;
        ui.scoreDonut.innerHTML = html;
    };

    const setupEventListeners = () => {
        ui.dropzone.addEventListener("click", () => ui.fileInput.click());
        ui.dropzone.addEventListener("dragover", e => {
            e.preventDefault();
            ui.dropzone.classList.add("dragover");
        });
        ui.dropzone.addEventListener("dragleave", () => ui.dropzone.classList.remove("dragover"));
        ui.dropzone.addEventListener("drop", e => {
            e.preventDefault();
            ui.dropzone.classList.remove("dragover");
            if (e.dataTransfer.files.length) handleFileUpload(e.dataTransfer.files[0]);
        });
        ui.fileInput.addEventListener("change", e => {
            if (e.target.files.length) handleFileUpload(e.target.files[0]);
        });
        ui.downloadPdfBtn.addEventListener("click", async () => {
            if (!state.file) return;
            const formData = new FormData();
            formData.append("file", state.file);
            try {
                const response = await fetch(`${API_BASE_URL}/report.pdf`, {
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
        ui.reanalyzeBtn.addEventListener("click", () => {
            state.file = null;
            switchState("landing");
        });
    };

    const init = () => {
        switchState("landing");
        setupEventListeners();
    };

    init();
});
