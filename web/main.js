const API_BASE = "http://localhost:8000"; // change for prod

let lastFile = null;
const progressTimers = [];

const els = {
  drop: document.getElementById("dropzone"),
  input: document.getElementById("fileInput"),
  progress: document.getElementById("progress"),
  results: document.getElementById("results"),
  scoreDonut: document.getElementById("scoreDonut"),
  scoreText: document.getElementById("scoreText"),
  levelText: document.getElementById("levelText"),
  scoreMessage: document.getElementById("scoreMessage"),
  triggers: document.getElementById("triggers"),
  improvements: document.getElementById("improvements"),
  pdfBtn: document.getElementById("pdfBtn"),
  retryBtn: document.getElementById("retryBtn"),
  stepEls: Array.from(document.querySelectorAll("[data-step]")),
};

function show(el) {
  if (el) {
    el.removeAttribute("hidden");
  }
}

function hide(el) {
  if (el) {
    el.setAttribute("hidden", "");
  }
}

function clearProgressTimers() {
  while (progressTimers.length) {
    const timer = progressTimers.pop();
    clearTimeout(timer);
  }
}

function setActiveStep(index) {
  els.stepEls.forEach((node, idx) => {
    if (index >= 0 && idx <= index) {
      node.classList.add("active");
    } else {
      node.classList.remove("active");
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

function isSupportedImage(file) {
  if (!file) return false;
  const mime = file.type || "";
  const name = file.name || "";
  const mimeMatch = /image\/(png|jpe?g)/i.test(mime);
  const extMatch = /\.(png|jpe?g)$/i.test(name);
  return mimeMatch || extMatch;
}

function handleFiles(fileList) {
  const file = fileList && fileList[0];
  if (!file) return;
  if (!isSupportedImage(file)) {
    window.alert("Please upload a JPG or PNG image.");
    return;
  }
  lastFile = file;
  hide(els.results);
  els.drop.classList.add("is-hidden");
  show(els.progress);
  clearProgressTimers();
  setActiveStep(0);
  queueStep(1, 700);
  (async () => {
    try {
      const data = await analyzeImage(file);
      clearProgressTimers();
      setActiveStep(2);
      renderResults(data);
      hide(els.progress);
      show(els.results);
      window.setTimeout(() => {
        els.results.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 150);
    } catch (error) {
      console.error(error);
      window.alert("Analysis failed. Please try again.");
      resetUI();
    }
  })();
}

function setupDropzone() {
  if (!els.drop || !els.input) return;
  const browseButtons = els.drop.querySelectorAll(".browse-btn");
  browseButtons.forEach((btn) => {
    btn.addEventListener("click", (event) => {
      event.stopPropagation();
      els.input.click();
    });
  });

  els.drop.addEventListener("click", () => {
    els.input.click();
  });

  els.drop.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      els.input.click();
    }
  });

  els.drop.addEventListener("dragover", (event) => {
    event.preventDefault();
    els.drop.classList.add("dragover");
  });

  els.drop.addEventListener("dragleave", () => {
    els.drop.classList.remove("dragover");
  });

  els.drop.addEventListener("drop", (event) => {
    event.preventDefault();
    els.drop.classList.remove("dragover");
    handleFiles(event.dataTransfer.files);
  });

  els.input.addEventListener("change", (event) => {
    handleFiles(event.target.files);
    event.target.value = "";
  });
}

function setupActions() {
  els.pdfBtn.addEventListener("click", async () => {
    if (!lastFile) {
      window.alert("Upload an image before downloading a report.");
      return;
    }
    const original = els.pdfBtn.textContent;
    els.pdfBtn.disabled = true;
    els.pdfBtn.textContent = "Preparing report…";
    try {
      await downloadReport(lastFile);
    } catch (error) {
      console.error(error);
      window.alert("Report download failed. Please try again.");
    } finally {
      els.pdfBtn.textContent = original;
      els.pdfBtn.disabled = false;
    }
  });

  els.retryBtn.addEventListener("click", () => {
    resetUI();
  });
}

function init() {
  drawDonut(0);
  resetResultsContent();
  hide(els.progress);
  hide(els.results);
  setupDropzone();
  setupActions();
}

init();
