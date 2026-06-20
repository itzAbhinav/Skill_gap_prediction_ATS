// ===========================================================
// Skill Gap Scanner — frontend logic
// Talks to the Flask backend at API_BASE_URL via fetch().
// ===========================================================

// Set this to your deployed Render backend URL once you have it,
// e.g. "https://skill-gap-scanner-backend.onrender.com"
// Leave as-is to keep testing against your local Flask server.
const API_BASE_URL = "http://127.0.0.1:5000";

const resumeInput = document.getElementById("resumeInput");
const dropzone = document.getElementById("dropzone");
const dropzoneContent = document.getElementById("dropzoneContent");
const dropzoneFile = document.getElementById("dropzoneFile");
const fileNameEl = document.getElementById("fileName");
const clearFileBtn = document.getElementById("clearFile");

const jdInput = document.getElementById("jdInput");
const scanBtn = document.getElementById("scanBtn");
const errorMsg = document.getElementById("errorMsg");

const inputCard = document.getElementById("inputCard");
const loading = document.getElementById("loading");
const loadingText = document.getElementById("loadingText");
const results = document.getElementById("results");

const resultBanner = document.getElementById("resultBanner");
const resultBannerText = document.getElementById("resultBannerText");
const resumeChips = document.getElementById("resumeChips");
const matchedChips = document.getElementById("matchedChips");
const missingChips = document.getElementById("missingChips");

const atsGaugeFill = document.getElementById("atsGaugeFill");
const atsScoreNumber = document.getElementById("atsScoreNumber");
const atsLabel = document.getElementById("atsLabel");
const atsExplanation = document.getElementById("atsExplanation");
const fixesList = document.getElementById("fixesList");

const GAUGE_ARC_LENGTH = 204.2; // total length of the semicircle path, see style.css
const resetBtn = document.getElementById("resetBtn");

let selectedFile = null;

// ---------- File selection (click + drag/drop) ----------

dropzone.addEventListener("click", () => resumeInput.click());

resumeInput.addEventListener("change", (e) => {
  if (e.target.files.length > 0) setSelectedFile(e.target.files[0]);
});

["dragenter", "dragover"].forEach((evt) => {
  dropzone.addEventListener(evt, (e) => {
    e.preventDefault();
    dropzone.classList.add("dragover");
  });
});

["dragleave", "drop"].forEach((evt) => {
  dropzone.addEventListener(evt, (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
  });
});

dropzone.addEventListener("drop", (e) => {
  const file = e.dataTransfer.files[0];
  if (file) setSelectedFile(file);
});

clearFileBtn.addEventListener("click", (e) => {
  e.stopPropagation();
  selectedFile = null;
  resumeInput.value = "";
  dropzoneContent.hidden = false;
  dropzoneFile.hidden = true;
});

function setSelectedFile(file) {
  const ext = file.name.split(".").pop().toLowerCase();
  if (ext !== "pdf" && ext !== "docx") {
    showError("Please upload a .pdf or .docx file.");
    return;
  }
  hideError();
  selectedFile = file;
  fileNameEl.textContent = file.name;
  dropzoneContent.hidden = true;
  dropzoneFile.hidden = false;
}

// ---------- Error display ----------

function showError(message) {
  errorMsg.textContent = message;
  errorMsg.hidden = false;
}

function hideError() {
  errorMsg.hidden = true;
}

// ---------- Scan action ----------

scanBtn.addEventListener("click", async () => {
  hideError();

  if (!selectedFile) {
    showError("Please upload a resume first (.pdf or .docx).");
    return;
  }
  const jobDescription = jdInput.value.trim();
  if (!jobDescription) {
    showError("Please paste a job description.");
    return;
  }

  const formData = new FormData();
  formData.append("resume", selectedFile);
  formData.append("job_description", jobDescription);

  setLoading(true);

  // Render's free tier spins down idle backends; the first request after a
  // period of inactivity can take 30-60s to wake it back up. Swap the loading
  // text after a few seconds so this doesn't look like the app is frozen.
  const wakeUpTimer = setTimeout(() => {
    loadingText.textContent = "Waking up the server (free hosting naps when idle)…";
  }, 4000);

  try {
    const response = await fetch(`${API_BASE_URL}/analyze`, {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    if (!response.ok) {
      showError(data.error || "Something went wrong. Please try again.");
      setLoading(false);
      return;
    }

    renderResults(data);
    setLoading(false);
  } catch (err) {
    showError(
      "Couldn't reach the analysis server. Make sure the Flask backend is running on " +
        API_BASE_URL +
        "."
    );
    setLoading(false);
  } finally {
    clearTimeout(wakeUpTimer);
    loadingText.textContent = "Extracting skills…";
  }
});

function setLoading(isLoading) {
  scanBtn.disabled = isLoading;
  loading.hidden = !isLoading;
  if (isLoading) {
    results.hidden = true;
  }
}

// ---------- Render results ----------

function renderResults(data) {
  resultBannerText.textContent = data.message;
  resultBanner.classList.remove("is-match", "is-gap");
  resultBanner.classList.add(data.exact_match ? "is-match" : "is-gap");

  renderChipList(resumeChips, data.resume_skills, "default");
  renderChipList(matchedChips, data.matched_skills, "matched");
  renderChipList(missingChips, data.missing_skills, "missing");

  renderAtsGauge(data.ats_score, data.ats_label);
  atsExplanation.textContent = data.ats_explanation || "";

  renderFixesList(data.fixes);

  inputCard.style.display = "none";
  results.hidden = false;
}

function renderAtsGauge(score, label) {
  const safeScore = Math.max(0, Math.min(100, score || 0));

  // Animate the arc fill: dashoffset goes from full length (0% shown) to 0 (100% shown)
  const offset = GAUGE_ARC_LENGTH * (1 - safeScore / 100);

  // Reset to empty first so the fill animates from 0 every time, then apply the real value
  atsGaugeFill.style.transition = "none";
  atsGaugeFill.style.strokeDashoffset = GAUGE_ARC_LENGTH;
  // Force a reflow so the browser registers the reset before re-enabling the transition
  atsGaugeFill.getBoundingClientRect();
  atsGaugeFill.style.transition = "";

  requestAnimationFrame(() => {
    atsGaugeFill.style.strokeDashoffset = offset;
  });

  atsGaugeFill.classList.remove("is-weak", "is-moderate", "is-good", "is-strong");
  if (safeScore < 40) atsGaugeFill.classList.add("is-weak");
  else if (safeScore < 70) atsGaugeFill.classList.add("is-moderate");
  else if (safeScore < 100) atsGaugeFill.classList.add("is-good");
  else atsGaugeFill.classList.add("is-strong");

  // Animate the number ticking up
  animateNumber(atsScoreNumber, safeScore);
  atsLabel.textContent = label || "";
}

function animateNumber(el, target) {
  const duration = 700;
  const start = performance.now();

  function tick(now) {
    const progress = Math.min(1, (now - start) / duration);
    const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
    el.textContent = Math.round(target * eased);
    if (progress < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

function renderFixesList(fixes) {
  fixesList.innerHTML = "";

  if (!fixes || fixes.length === 0) {
    const empty = document.createElement("li");
    empty.className = "fixes-list-empty";
    empty.textContent = "No fixes needed — every skill in the job description is already on the resume.";
    fixesList.appendChild(empty);
    return;
  }

  fixes.forEach((fix) => {
    const item = document.createElement("li");
    item.className = "fix-item";

    const icon = document.createElement("span");
    icon.className = "fix-item-icon";
    icon.textContent = "→";

    const text = document.createElement("span");
    text.textContent = fix.suggestion;

    item.appendChild(icon);
    item.appendChild(text);
    fixesList.appendChild(item);
  });
}

function renderChipList(container, skills, variant) {
  container.innerHTML = "";

  if (!skills || skills.length === 0) {
    const empty = document.createElement("span");
    empty.className = "chip-empty";
    empty.textContent = variant === "missing" ? "None — fully covered" : "None found";
    container.appendChild(empty);
    return;
  }

  skills.forEach((skill) => {
    const chip = document.createElement("span");
    chip.className =
      variant === "matched" ? "chip chip-matched" : variant === "missing" ? "chip chip-missing" : "chip";
    chip.textContent = skill;
    container.appendChild(chip);
  });
}

// ---------- Reset ----------

resetBtn.addEventListener("click", () => {
  selectedFile = null;
  resumeInput.value = "";
  jdInput.value = "";
  dropzoneContent.hidden = false;
  dropzoneFile.hidden = true;
  hideError();

  results.hidden = true;
  inputCard.style.display = "block";
});
