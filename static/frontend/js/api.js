/* Shared fetch wrapper. Stores JWT tokens in localStorage (fine for a demo
   project; for production consider httpOnly cookies instead). */
const API_BASE = "/api";

const Api = {
  getAccess() { return localStorage.getItem("access_token"); },
  getRefresh() { return localStorage.getItem("refresh_token"); },
  setTokens(access, refresh) {
    localStorage.setItem("access_token", access);
    if (refresh) localStorage.setItem("refresh_token", refresh);
  },
  clearTokens() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  },
  isLoggedIn() { return !!this.getAccess(); },

  async request(path, { method = "GET", body = null, isForm = false, auth = true, retry = true } = {}) {
    const headers = {};
    if (!isForm) headers["Content-Type"] = "application/json";
    if (auth && this.getAccess()) headers["Authorization"] = `Bearer ${this.getAccess()}`;

    const res = await fetch(`${API_BASE}${path}`, {
      method,
      headers,
      body: body ? (isForm ? body : JSON.stringify(body)) : null,
    });

    if (res.status === 401 && retry && auth && this.getRefresh()) {
      const refreshed = await this.refreshToken();
      if (refreshed) return this.request(path, { method, body, isForm, auth, retry: false });
      this.clearTokens();
      window.location.href = "/login/";
      return null;
    }

    let data = null;
    try { data = await res.json(); } catch (e) { /* no body */ }

    if (!res.ok) {
      const message = data && (data.detail || JSON.stringify(data)) || `Request failed (${res.status})`;
      throw new Error(message);
    }
    return data;
  },

  async refreshToken() {
    try {
      const res = await fetch(`${API_BASE}/auth/login/refresh/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh: this.getRefresh() }),
      });
      if (!res.ok) return false;
      const data = await res.json();
      this.setTokens(data.access, null);
      return true;
    } catch (e) { return false; }
  },

  // --- Auth ---
  register(payload) { return this.request("/auth/register/", { method: "POST", body: payload, auth: false }); },
  login(payload) { return this.request("/auth/login/", { method: "POST", body: payload, auth: false }); },
  me() { return this.request("/auth/me/"); },

  // --- Resumes ---
  listResumes() { return this.request("/resumes/"); },
  uploadResume(file) {
    const form = new FormData();
    form.append("file", file);
    return this.request("/resumes/", { method: "POST", body: form, isForm: true });
  },
  getResume(id) { return this.request(`/resumes/${id}/`); },
  deleteResume(id) { return this.request(`/resumes/${id}/`, { method: "DELETE" }); },

  // --- Analysis ---
  analyzeResume(resumeId) { return this.request(`/analysis/analyze/${resumeId}/`, { method: "POST" }); },
  listAnalyses() { return this.request("/analysis/"); },

  // --- Jobs ---
  listJobs() { return this.request("/jobs/"); },
  createJob(payload) { return this.request("/jobs/", { method: "POST", body: payload }); },
  matchResumeToJob(jobId, resumeId) { return this.request(`/jobs/${jobId}/match/${resumeId}/`, { method: "POST" }); },
  listMatches() { return this.request("/jobs/matches/"); },

  // --- AI engine ---
  generateInterviewQuestions(resumeId, jobId) {
    return this.request(`/ai/interview-questions/${resumeId}/`, { method: "POST", body: jobId ? { job_id: jobId } : {} });
  },
  generateLearningRecs(jobMatchId) {
    return this.request(`/ai/learning-recommendations/${jobMatchId}/`, { method: "POST" });
  },

  // --- Dashboard ---
  dashboardSummary() { return this.request("/dashboard/summary/"); },
};
