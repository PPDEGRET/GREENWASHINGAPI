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
