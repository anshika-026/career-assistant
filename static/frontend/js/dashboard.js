let currentResumeId = null;
let currentJobId = null;
let currentMatchId = null;

function el(id) { return document.getElementById(id); }
function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

document.addEventListener("DOMContentLoaded", async () => {
  if (!Api.isLoggedIn()) {
    window.location.href = "/login/";
    return;
  }

  try {
    const user = await Api.me();
    el("user-tag").textContent = user.username;
  } catch (e) { /* interceptor will redirect on 401 */ }

  wireTabs();
  wireLogout();
  wireUpload();
  wireJobForm();
  loadSummary();
  loadResumes();
});

function wireTabs() {
  document.querySelectorAll(".tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
      document.querySelectorAll(".tab-panel").forEach((p) => (p.style.display = "none"));
      tab.classList.add("active");
      el(tab.dataset.target).style.display = "block";
    });
  });
}

function wireLogout() {
  el("logout-btn").addEventListener("click", () => {
    Api.clearTokens();
    window.location.href = "/login/";
  });
}

/* ---------- Overview / dashboard summary ---------- */
async function loadSummary() {
  try {
    const s = await Api.dashboardSummary();
    el("stat-resumes").textContent = s.resume_count;
    el("stat-analyses").textContent = s.analysis_count;
    el("stat-matches").textContent = s.job_match_count;
    el("stat-latest-score").textContent = s.latest_ats_score ?? "--";

    const gapsEl = el("top-skill-gaps");
    if (s.top_skill_gaps.length === 0) {
      gapsEl.innerHTML = '<p class="empty-state">No skill gaps yet -- match a resume against a job description to see this.</p>';
    } else {
      gapsEl.innerHTML = '<div class="tag-row">' +
        s.top_skill_gaps.map(g => `<span class="tag missing">${escapeHtml(g.skill)} &times;${g.count}</span>`).join("") +
        "</div>";
    }
  } catch (err) {
    console.error(err);
  }
}

/* ---------- Resume upload + list ---------- */
function wireUpload() {
  const zone = el("upload-zone");
  const input = el("file-input");
  zone.addEventListener("click", () => input.click());
  input.addEventListener("change", async () => {
    if (!input.files.length) return;
    zone.textContent = "Uploading + parsing...";
    try {
      const resume = await Api.uploadResume(input.files[0]);
      zone.textContent = "Drop a PDF or DOCX here, or click to browse";
      currentResumeId = resume.id;
      await loadResumes();
      await selectResume(resume.id);
    } catch (err) {
      zone.textContent = "Upload failed: " + err.message;
    }
  });
}

async function loadResumes() {
  const resumes = await Api.listResumes();
  const list = el("resume-list");
  const jobResumeSelect = el("match-resume-select");
  const interviewResumeSelect = el("interview-resume-select");

  if (resumes.length === 0) {
    list.innerHTML = '<p class="empty-state">No resumes uploaded yet.</p>';
  } else {
    list.innerHTML = resumes.map(r => `
      <li>
        <div>
          <strong>${escapeHtml(r.original_filename)}</strong>
          <div class="muted mono">${r.parsing_status} &middot; ${r.word_count} words</div>
        </div>
        <button class="btn small secondary" data-resume-id="${r.id}">Select</button>
      </li>
    `).join("");
    list.querySelectorAll("button[data-resume-id]").forEach((btn) => {
      btn.addEventListener("click", () => selectResume(parseInt(btn.dataset.resumeId, 10)));
    });
  }

  const options = resumes.map(r => `<option value="${r.id}">${escapeHtml(r.original_filename)}</option>`).join("");
  if (jobResumeSelect) jobResumeSelect.innerHTML = options || '<option value="">No resumes yet</option>';
  if (interviewResumeSelect) interviewResumeSelect.innerHTML = options || '<option value="">No resumes yet</option>';
}

async function selectResume(id) {
  currentResumeId = id;
  el("selected-resume-banner").textContent = `Selected resume ID: ${id}`;
  const matchSelect = el("match-resume-select");
  const interviewSelect = el("interview-resume-select");
  if (matchSelect) matchSelect.value = id;
  if (interviewSelect) interviewSelect.value = id;

  try {
    const analysis = await Api.analyzeResume(id);
    renderAnalysis(analysis);
    loadSummary();
  } catch (err) {
    el("score-panel-body").innerHTML = `<p class="empty-state">Analysis failed: ${escapeHtml(err.message)}</p>`;
  }
}

function renderAnalysis(a) {
  const verdict = a.ats_score >= 75 ? "pass" : a.ats_score >= 50 ? "warn" : "fail";
  const verdictLabel = a.ats_score >= 75 ? "Strong" : a.ats_score >= 50 ? "Needs work" : "Weak";

  const skillTags = Object.keys(a.skills_found).map(s => `<span class="tag neutral">${escapeHtml(s)}</span>`).join("");
  const issues = a.issues.length
    ? `<ul class="item-list issue-list">${a.issues.map(i => `<li>${escapeHtml(i)}</li>`).join("")}</ul>`
    : '<p class="empty-state">No major issues detected.</p>';

  el("score-panel-body").innerHTML = `
    <div class="dial-row">
      <div class="dial"><div class="score mono">${a.ats_score}<small>/100</small></div></div>
      <div>
        <span class="stamp ${verdict}">${verdictLabel}</span>
        <p class="muted" style="margin-top:10px;">${a.word_count} words &middot; ${Object.keys(a.skills_found).length} skills recognized</p>
      </div>
    </div>
    <h3 style="margin-top:24px;">Skills detected</h3>
    <div class="tag-row">${skillTags || '<span class="empty-state">None detected</span>'}</div>
    <h3 style="margin-top:24px;">Issues to fix</h3>
    ${issues}
  `;
}

/* ---------- Job descriptions + matching ---------- */
function wireJobForm() {
  const form = el("job-form");
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const title = el("job-title").value.trim();
    const company = el("job-company").value.trim();
    const raw_text = el("job-text").value.trim();
    try {
      const job = await Api.createJob({ title, company, raw_text });
      currentJobId = job.id;
      form.reset();
      await runMatch();
    } catch (err) {
      alert("Could not save job description: " + err.message);
    }
  });
}

async function runMatch() {
  const resumeId = parseInt(el("match-resume-select").value, 10);
  if (!resumeId || !currentJobId) {
    alert("Upload a resume and save a job description first.");
    return;
  }
  try {
    const match = await Api.matchResumeToJob(currentJobId, resumeId);
    currentMatchId = match.id;
    renderMatch(match);
    loadSummary();
  } catch (err) {
    el("match-result").innerHTML = `<p class="empty-state">Match failed: ${escapeHtml(err.message)}</p>`;
  }
}

function renderMatch(m) {
  const matched = m.matched_skills.map(s => `<span class="tag matched">${escapeHtml(s)}</span>`).join("");
  const missing = m.missing_skills.map(s => `<span class="tag missing">${escapeHtml(s)}</span>`).join("");
  el("match-result").innerHTML = `
    <div class="dial-row">
      <div class="dial"><div class="score mono">${m.match_score}<small>%</small></div></div>
      <div><p class="muted">Match against: <strong>${escapeHtml(m.job_title)}</strong></p></div>
    </div>
    <h3 style="margin-top:20px;">Matched skills</h3>
    <div class="tag-row">${matched || '<span class="empty-state">None</span>'}</div>
    <h3 style="margin-top:20px;">Missing skills (skill gap)</h3>
    <div class="tag-row">${missing || '<span class="empty-state">None -- great fit!</span>'}</div>
    <button class="btn small" style="margin-top:20px;" id="get-recs-btn">Get learning recommendations</button>
  `;
  el("get-recs-btn").addEventListener("click", loadRecommendations);
}

async function loadRecommendations() {
  if (!currentMatchId) return;
  const target = el("recs-result");
  target.innerHTML = '<p class="empty-state">Generating recommendations...</p>';
  try {
    const rec = await Api.generateLearningRecs(currentMatchId);
    if (rec.recommendations.length === 0) {
      target.innerHTML = '<p class="empty-state">No gaps to address -- nothing to recommend.</p>';
      return;
    }
    target.innerHTML = rec.recommendations.map(r => `
      <div class="qcard">
        <div class="meta">${escapeHtml(r.skill)}</div>
        <p style="margin:0 0 6px;">${escapeHtml(r.why_it_matters)}</p>
        <p class="muted" style="margin:0;">${escapeHtml(r.how_to_learn)}</p>
      </div>
    `).join("");
  } catch (err) {
    target.innerHTML = `<p class="empty-state">Failed: ${escapeHtml(err.message)}</p>`;
  }
  document.querySelector('.tab[data-target="tab-learn"]').click();
}

/* ---------- Interview questions ---------- */
document.addEventListener("DOMContentLoaded", () => {
  const btn = el("generate-questions-btn");
  if (btn) btn.addEventListener("click", async () => {
    const resumeId = parseInt(el("interview-resume-select").value, 10);
    if (!resumeId) { alert("Select a resume first."); return; }
    const target = el("interview-result");
    target.innerHTML = '<p class="empty-state">Generating questions...</p>';
    try {
      const session = await Api.generateInterviewQuestions(resumeId, currentJobId);
      target.innerHTML = session.questions.map(q => `
        <div class="qcard">
          <div class="meta">${escapeHtml(q.category)} &middot; ${escapeHtml(q.difficulty)}</div>
          <p style="margin:0;">${escapeHtml(q.question)}</p>
        </div>
      `).join("");
    } catch (err) {
      target.innerHTML = `<p class="empty-state">Failed: ${escapeHtml(err.message)}</p>`;
    }
  });
});
