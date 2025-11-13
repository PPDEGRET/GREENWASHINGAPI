const API_BASE = window.API_BASE || "http://localhost:8000";

async function analyzeImage(file) {
  const form = new FormData();
  form.append("file", file);
  const response = await fetch(`${API_BASE}/analyze`, {
    method: "POST",
    body: form,
  });
  if (!response.ok) {
    throw new Error(`Analyze failed (${response.status})`);
  }
  return await response.json();
}

async function downloadReport(file) {
  const form = new FormData();
  form.append("file", file);
  const response = await fetch(`${API_BASE}/report.pdf`, {
    method: "POST",
    body: form,
  });
  if (!response.ok) {
    throw new Error(`Report failed (${response.status})`);
  }
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "LeafCheck_Report.pdf";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("analyze-form");
  const fileInput = document.getElementById("creative-input");
  const analyzeBtn = document.getElementById("analyze-btn");
  const downloadBtn = document.getElementById("download-report");
  const statusMessage = document.getElementById("status-message");
  const fileNameEl = document.getElementById("file-name");
  const resultsEl = document.getElementById("analysis-results");
  const scoreValue = document.getElementById("score-value");
  const levelBadge = document.getElementById("level-badge");
  const scoreFill = document.getElementById("score-fill");
  const reasonsList = document.getElementById("reasons-list");
  const ocrText = document.getElementById("ocr-text");

  let lastFile = null;

  const setStatus = (message, variant) => {
    statusMessage.textContent = message || "";
    statusMessage.classList.remove("error", "success");
    if (variant === "error") {
      statusMessage.classList.add("error");
    } else if (variant === "success") {
      statusMessage.classList.add("success");
    }
  };

  const resetResults = () => {
    resultsEl.classList.add("hidden");
    reasonsList.innerHTML = "";
    ocrText.textContent = "Upload an asset to preview the extracted text.";
    scoreValue.textContent = "0";
    levelBadge.textContent = "Low risk";
    levelBadge.className = "level-badge level-low";
    scoreFill.style.width = "0%";
    scoreFill.className = "score-fill level-low";
    downloadBtn.disabled = true;
  };

  const renderResults = (data) => {
    const score = Math.max(0, Math.min(100, Number(data.score) || 0));
    const level = String(data.level || "Low");
    const levelKey = level.toLowerCase();
    const reasons = Array.isArray(data.reasons) ? data.reasons : [];
    const text = data.text || "";

    scoreValue.textContent = score.toString();
    levelBadge.textContent = `${level} risk`;
    levelBadge.className = `level-badge level-${levelKey}`;
    scoreFill.style.width = `${score}%`;
    scoreFill.className = `score-fill level-${levelKey}`;

    reasonsList.innerHTML = "";
    if (reasons.length === 0) {
      const li = document.createElement("li");
      li.textContent = "No high-risk claims detected.";
      reasonsList.appendChild(li);
    } else {
      reasons.forEach((reason) => {
        const li = document.createElement("li");
        li.textContent = reason;
        reasonsList.appendChild(li);
      });
    }
  });
}

function queueStep(index, delay) {
  const timer = window.setTimeout(() => {
    setActiveStep(index);
  }, delay);
  progressTimers.push(timer);
}

function drawDonut(value) {
  if (!els.scoreDonut) return;
  const pct = Math.max(0, Math.min(100, Number(value) || 0));
  const radius = 80;
  const circumference = 2 * Math.PI * radius;
  const progress = (pct / 100) * circumference;
  els.scoreDonut.innerHTML = `
    <svg class="donut" viewBox="0 0 200 200" role="img" aria-label="Risk score donut">
      <circle cx="100" cy="100" r="${radius}" stroke="#E5EFE8" stroke-width="18" fill="none"></circle>
      <circle cx="100" cy="100" r="${radius}" stroke="#5ea476" stroke-width="18" fill="none"
        stroke-dasharray="${progress} ${circumference - progress}" transform="rotate(-90 100 100)" stroke-linecap="round"></circle>
      <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle"
        font-size="28" font-weight="800" fill="#1f2a24">${Math.round(pct)}</text>
    </svg>
  `;
}

function getLevelMessage(level) {
  switch ((level || "").toLowerCase()) {
    case "high":
      return "High risk — escalate to legal or compliance before publishing.";
    case "medium":
      return "Medium risk — tighten claims and include qualifying detail.";
    case "low":
    default:
      return "Low risk — keep monitoring claims for emerging guidance.";
  }
}

function renderList(target, items) {
  if (!target) return;
  const safeItems = Array.isArray(items) && items.length > 0 ? items : ["No critical triggers detected."];
  target.innerHTML = safeItems
    .map((item) => `<li>${item}</li>`)
    .join("");
}

function renderResults(payload) {
  const score = Math.max(0, Math.min(100, Number(payload?.score) || 0));
  const level = String(payload?.level || "Low");
  drawDonut(score);
  els.scoreText.textContent = `${score} / 100`;
  els.levelText.textContent = level;
  els.scoreMessage.textContent = getLevelMessage(level);
  renderList(els.triggers, payload?.reasons);
  renderList(els.improvements, payload?.reasons);
  els.pdfBtn.disabled = !lastFile;
}

function resetResultsContent() {
  drawDonut(0);
  els.scoreText.textContent = "0 / 100";
  els.levelText.textContent = "Low";
  els.scoreMessage.textContent = "Upload a creative to see your greenwashing risk.";
  els.triggers.innerHTML = "";
  els.improvements.innerHTML = "";
  els.pdfBtn.disabled = true;
}

function resetUI() {
  clearProgressTimers();
  setActiveStep(-1);
  hide(els.progress);
  hide(els.results);
  els.drop.classList.remove("is-hidden");
  els.drop.classList.remove("dragover");
  resetResultsContent();
  lastFile = null;
  window.setTimeout(() => {
    els.drop.focus({ preventScroll: true });
  }, 0);
}

async function analyzeImage(file) {
  const form = new FormData();
  form.append("file", file);
  setActiveStep(0);
  const response = await fetch(`${API_BASE}/analyze`, {
    method: "POST",
    body: form,
  });
  if (!response.ok) {
    throw new Error("Analyze failed");
  }
  return response.json();
}

async function downloadReport(file) {
  const form = new FormData();
  form.append("file", file);
  setActiveStep(3);
  const response = await fetch(`${API_BASE}/report.pdf`, {
    method: "POST",
    body: form,
  });
  if (!response.ok) {
    throw new Error("Report failed");
  }
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = "LeafCheck_Report.pdf";
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

    ocrText.textContent = text ? text : "OCR did not detect any text.";

    resultsEl.classList.remove("hidden");
    downloadBtn.disabled = false;
  };

  resetResults();

  fileInput.addEventListener("change", () => {
    const [file] = fileInput.files;
    lastFile = file || null;
    fileNameEl.textContent = file ? file.name : "No file selected";
    setStatus("", "");
    resetResults();
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!lastFile) {
      setStatus("Select an image or PDF before running the analysis.", "error");
      return;
    }

    analyzeBtn.disabled = true;
    analyzeBtn.textContent = "Analyzing...";
    setStatus("Running OCR and GPT review...", "");
    try {
      const result = await analyzeImage(lastFile);
      renderResults(result);
      setStatus("Analysis ready.", "success");
    } catch (error) {
      console.error(error);
      setStatus(error.message || "Unable to analyze the asset.", "error");
    } finally {
      analyzeBtn.disabled = false;
      analyzeBtn.textContent = "Analyze with AI";
    }
  });

  downloadBtn.addEventListener("click", async () => {
    if (!lastFile) {
      setStatus("Upload an asset before downloading a report.", "error");
      return;
    }
    downloadBtn.disabled = true;
    const originalText = downloadBtn.textContent;
    downloadBtn.textContent = "Preparing...";
    setStatus("Generating PDF report...", "");
    try {
      await downloadReport(lastFile);
      setStatus("Report downloaded.", "success");
    } catch (error) {
      console.error(error);
      setStatus(error.message || "Unable to download the report.", "error");
    } finally {
      downloadBtn.disabled = false;
      downloadBtn.textContent = originalText;
    }
  });
});
