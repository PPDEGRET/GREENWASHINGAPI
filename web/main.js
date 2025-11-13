const API_BASE = "http://localhost:8000";

const els = {
  landing: document.getElementById("app-state-landing"),
  progress: document.getElementById("app-state-progress"),
  results: document.getElementById("app-state-results"),
  dropzone: document.getElementById("dropzone"),
  fileInput: document.getElementById("file-input"),
  scoreDonut: document.getElementById("score-donut"),
  triggersList: document.getElementById("triggers-list"),
  improvementsList: document.getElementById("improvements-list"),
  downloadPdfBtn: document.getElementById("download-pdf-btn"),
  reanalyzeBtn: document.getElementById("reanalyze-btn"),
  progressSteps: document.querySelectorAll("[data-step]"),
};

const appStates = {
    landing: els.landing,
    progress: els.progress,
    results: els.results
}

let lastFile = null;

function switchState(state) {
  console.log("Switching to state:", state);
  for (const appState in appStates) {
    if (appState === state) {
        console.log("Showing:", appState);
        appStates[appState].hidden = false;
    } else {
        console.log("Hiding:", appState);
        appStates[appState].hidden = true;
    }
  }
}

function runProgressIndicator() {
    let activeIndex = 0;
    els.progressSteps.forEach((step, index) => {
        setTimeout(() => {
            step.classList.add("active");
        }, index * 750);
    });
}

function drawDonut(score) {
  const pct = Math.max(0, Math.min(100, score || 0));
  const html = `
    <svg viewBox="0 0 36 36" class="score-svg">
      <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
            fill="none" stroke="#e6e6e6" stroke-width="3"></path>
      <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
            fill="none" stroke="#d9534f" stroke-width="3"
            stroke-dasharray="${pct}, 100"></path>
      <text x="18" y="22" text-anchor="middle" font-size="12" class="score-text">${pct}</text>
    </svg>
    `;
  els.scoreDonut.innerHTML = html;
}

function renderTriggers(triggers) {
  els.triggersList.innerHTML = triggers
    .map((item) => `<li>${item}</li>`)
    .join("");
}

function renderImprovements() {
    const improvements = [
        "Be specific",
        "Provide proof"
    ]
  els.improvementsList.innerHTML = improvements
    .map((item) => `<li>${item}</li>`)
    .join("");
}

async function handleFileUpload(file) {
  lastFile = file;
  switchState("progress");
  runProgressIndicator();

  const formData = new FormData();
  formData.append("file", file);

  try {
    console.log("Fetching data from API...");
    const response = await fetch(`${API_BASE}/analyze`, {
      method: "POST",
      body: formData,
    });
    console.log("API response received:", response);
    const data = await response.json();
    console.log("API data parsed:", data);

    drawDonut(data.score);
    renderTriggers(data.reasons);
    renderImprovements();
    switchState("results");
  } catch (error) {
    console.error("Error analyzing file:", error);
    alert("There was an an error analyzing your file. Please try again.");
    switchState("landing");
  }
}

function setupEventListeners() {
  els.dropzone.addEventListener("click", () => els.fileInput.click());
  els.dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    els.dropzone.classList.add("dragover");
  });
  els.dropzone.addEventListener("dragleave", () => {
    els.dropzone.classList.remove("dragover");
  });
  els.dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    els.dropzone.classList.remove("dragover");
    if (e.dataTransfer.files.length) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  });

  els.fileInput.addEventListener("change", (e) => {
    if (e.target.files.length) {
      handleFileUpload(e.target.files[0]);
    }
  });

  els.downloadPdfBtn.addEventListener("click", async () => {
    if (!lastFile) return;
    const formData = new FormData();
    formData.append("file", lastFile);

    try {
      const response = await fetch(`${API_BASE}/report.pdf`, {
        method: "POST",
        body: formData,
      });
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "report.pdf";
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Error downloading PDF:", error);
    }
  });

  els.reanalyzeBtn.addEventListener("click", () => {
    lastFile = null;
    switchState("landing");
  });
}

function init() {
  switchState("landing");
  setupEventListeners();
}

init();
