/**
 * API Service
 * ===========
 * Handles all API calls to the FastAPI backend
 */

import axios from "axios";

// --- Base URL --------------------------------------------------------------
// Use env when available (baked at build time in CRA), otherwise fall back
// to your Render backend. This prevents production from defaulting to localhost.
const API_BASE_URL =
  (process.env.REACT_APP_API_URL && process.env.REACT_APP_API_URL.trim()) ||
  "https://ba-copilot-backend.onrender.com";

// Visible log so you can confirm what the deployed app actually used.
console.log("[BA] API base =", API_BASE_URL);

// --- Axios instance --------------------------------------------------------
export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "application/json" },
  // With permissive CORS (allow_origins=["*"]), do NOT send cookies.
  withCredentials: false,
  timeout: 30000,
});

// Optional: request/response logs while debugging
api.interceptors.request.use((config) => {
  // Comment this out after debugging if it's noisy
  console.log("[BA] →", config.method?.toUpperCase(), config.baseURL + config.url);
  return config;
});

// Error handler
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const detail =
        error.response.data?.detail ||
        error.response.data?.message ||
        error.message ||
        "Server error";
      console.error("[BA] API Error:", {
        url: error.config?.baseURL + error.config?.url,
        status: error.response.status,
        data: error.response.data,
      });
      return Promise.reject(new Error(detail));
    }
    if (error.request) {
      console.error("[BA] Network Error (no response):", error.config?.baseURL + error.config?.url);
      return Promise.reject(new Error("Network error. Please check your connection."));
    }
    console.error("[BA] Error:", error.message);
    return Promise.reject(new Error(error.message));
  }
);

// ========================================
// PROJECT ENDPOINTS
// ========================================

export const projectApi = {
  create: async (projectData) => (await api.post("/api/projects", projectData)).data,
  getAll: async () => (await api.get("/api/projects")).data,
  get: async (projectId) => (await api.get(`/api/projects/${projectId}`)).data,
  delete: async (projectId) => (await api.delete(`/api/projects/${projectId}`)).data,
  getSummary: async (projectId) => (await api.get(`/api/projects/${projectId}/summary`)).data,
};

// ========================================
// INPUT ENDPOINTS
// ========================================

export const inputApi = {
  uploadDocument: async (projectId, file) => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("project_id", projectId);
    return (
      await api.post("/api/input/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      })
    ).data;
  },

  submitText: async (projectId, text, inputType = "text") =>
    (
      await api.post("/api/input/text", {
        project_id: projectId,
        text,
        input_type: inputType,
      })
    ).data,

  getMockTranscript: async () => (await api.get("/api/input/mock-transcript")).data,
};

// ========================================
// REQUIREMENTS ENDPOINTS
// ========================================

export const requirementsApi = {
  extract: async (inputId, projectType, industry) =>
    (
      await api.post("/api/requirements/extract", {
        input_id: inputId,
        project_type: projectType,
        industry,
      })
    ).data,

  get: async (inputId) => (await api.get(`/api/requirements/${inputId}`)).data,
};

// ========================================
// USER STORIES ENDPOINTS
// ========================================

export const storiesApi = {
  generate: async (inputId, projectType) =>
    (await api.post("/api/stories/generate", { input_id: inputId, project_type: projectType })).data,

  get: async (inputId) => (await api.get(`/api/stories/${inputId}`)).data,

  exportJira: async (stories) => (await api.post("/api/stories/export/jira", { stories })).data,
};

// ========================================
// ACCEPTANCE CRITERIA ENDPOINTS
// ========================================

export const criteriaApi = {
  generate: async (storyId, userStoryText) =>
    (await api.post("/api/criteria/generate", { story_id: storyId, user_story: userStoryText })).data,

  get: async (storyId) => (await api.get(`/api/criteria/${storyId}`)).data,

  exportGherkin: async (criteria, featureName) =>
    (await api.post("/api/criteria/export/gherkin", { criteria, feature_name: featureName })).data,
};

// ========================================
// HEALTH CHECK
// ========================================

export const healthApi = {
  check: async () => (await api.get("/api/health")).data,
  checkApis: async () => (await api.get("/api/health/apis")).data,
};

// Keep default export for any code that expects it.
export default API_BASE_URL;
