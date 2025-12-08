/**
 * API Service
 * ===========
 * Handles all API calls to the FastAPI backend
 */

import axios from 'axios';

// Use environment variable if available, fallback to production URL
const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";


const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ========================================
// PROJECT ENDPOINTS
// ========================================

export const projectApi = {
  // Create new project
  create: async (projectData) => {
    const response = await api.post('/api/projects', projectData);
    return response.data;
  },

  // Get all projects
  getAll: async () => {
    const response = await api.get('/api/projects');
    return response.data;
  },

  // Get single project
  get: async (projectId) => {
    const response = await api.get(`/api/projects/${projectId}`);
    return response.data;
  },

  // Delete project
  delete: async (projectId) => {
    const response = await api.delete(`/api/projects/${projectId}`);
    return response.data;
  },

  // Get project summary
  getSummary: async (projectId) => {
    const response = await api.get(`/api/projects/${projectId}/summary`);
    return response.data;
  },
};

// ========================================
// INPUT ENDPOINTS
// ========================================

export const inputApi = {
  // Upload document
  uploadDocument: async (projectId, file) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('project_id', projectId);

    const response = await api.post('/api/input/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Submit text input
  submitText: async (projectId, text, inputType = 'text') => {
    const response = await api.post('/api/input/text', {
      project_id: projectId,
      text: text,
      input_type: inputType,
    });
    return response.data;
  },

  // Get mock transcript
  getMockTranscript: async () => {
    const response = await api.get('/api/input/mock-transcript');
    return response.data;
  },
};

// ========================================
// REQUIREMENTS ENDPOINTS
// ========================================

export const requirementsApi = {
  // Extract requirements from text
  extract: async (inputId, projectType, industry) => {
    const response = await api.post('/api/requirements/extract', {
      input_id: inputId,
      project_type: projectType,
      industry: industry,
    });
    return response.data;
  },

  // Get requirements for input
  get: async (inputId) => {
    const response = await api.get(`/api/requirements/${inputId}`);
    return response.data;
  },
};

// ========================================
// USER STORIES ENDPOINTS
// ========================================

export const storiesApi = {
  // Generate user stories
  generate: async (inputId, projectType) => {
    const response = await api.post('/api/stories/generate', {
      input_id: inputId,
      project_type: projectType,
    });
    return response.data;
  },

  // Get user stories
  get: async (inputId) => {
    const response = await api.get(`/api/stories/${inputId}`);
    return response.data;
  },

  // Export to JIRA CSV
  exportJira: async (stories) => {
    const response = await api.post('/api/stories/export/jira', {
      stories: stories,
    });
    return response.data;
  },
};

// ========================================
// ACCEPTANCE CRITERIA ENDPOINTS
// ========================================

export const criteriaApi = {
  // Generate acceptance criteria
  generate: async (storyId, userStoryText) => {
    const response = await api.post('/api/criteria/generate', {
      story_id: storyId,
      user_story: userStoryText,
    });
    return response.data;
  },

  // Get acceptance criteria
  get: async (storyId) => {
    const response = await api.get(`/api/criteria/${storyId}`);
    return response.data;
  },

  // Export to Gherkin
  exportGherkin: async (criteria, featureName) => {
    const response = await api.post('/api/criteria/export/gherkin', {
      criteria: criteria,
      feature_name: featureName,
    });
    return response.data;
  },
};

// ========================================
// HEALTH CHECK
// ========================================

export const healthApi = {
  check: async () => {
    const response = await api.get('/api/health');
    return response.data;
  },

  checkApis: async () => {
    const response = await api.get('/api/health/apis');
    return response.data;
  },
};

// Error handler
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error
      console.error('API Error:', error.response.data);
      throw new Error(error.response.data.detail || 'An error occurred');
    } else if (error.request) {
      // Request made but no response
      console.error('Network Error:', error.request);
      throw new Error('Network error. Please check your connection.');
    } else {
      // Something else happened
      console.error('Error:', error.message);
      throw new Error(error.message);
    }
  }
);

export default API_BASE_URL;