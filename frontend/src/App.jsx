/**
 * BA Copilot - Main Application Component
 * ========================================
 * React frontend for the Business Analyst AI Assistant
 */

import React, { useState, useEffect } from 'react';
import './App.css';
import Sidebar from './components/Sidebar';
import InputSection from './components/InputSection';
import RequirementsSection from './components/RequirementsSection';
import StoriesSection from './components/StoriesSection';
import CriteriaSection from './components/CriteriaSection';
import { healthApi, projectApi } from './services/api';
import { AlertCircle } from 'lucide-react';

function App() {
  // Project management state
  const [projects, setProjects] = useState([]);
  const [currentProject, setCurrentProject] = useState(null);
  
  // Workflow state
  const [inputData, setInputData] = useState(null);
  const [requirements, setRequirements] = useState(null);
  const [userStories, setUserStories] = useState(null);
  const [criteria, setCriteria] = useState(null);
  
  // API status
  const [apiStatus, setApiStatus] = useState({ healthy: false, apis: {} });

  // Load projects and check API health on mount
  useEffect(() => {
    checkHealth();
    loadProjects();
  }, []);

  const checkHealth = async () => {
    try {
      const health = await healthApi.check();
      const apis = await healthApi.checkApis();
      setApiStatus({ 
        healthy: health.status === 'healthy' || health.status === 'connected', 
        apis: apis 
      });
    } catch (error) {
      console.error('Health check failed:', error);
      setApiStatus({ healthy: false, apis: {} });
    }
  };

  const loadProjects = async () => {
    try {
      const allProjects = await projectApi.getAll();
      setProjects(allProjects || []);
    } catch (error) {
      console.error('Failed to load projects:', error);
      setProjects([]);
    }
  };

  // Project management handlers
  const handleCreateProject = async (projectData) => {
    try {
      const newProject = await projectApi.create(projectData);
      setProjects([...projects, newProject]);
      setCurrentProject(newProject);
    } catch (error) {
      console.error('Failed to create project:', error);
      alert('Failed to create project. Please try again.');
    }
  };

  const handleSelectProject = (project) => {
    setCurrentProject(project);
    // Reset workflow
    setInputData(null);
    setRequirements(null);
    setUserStories(null);
    setCriteria(null);
  };

  const handleDeleteProject = async (projectId) => {
    try {
      await projectApi.delete(projectId);
      // Filter by both possible id properties
      setProjects(projects.filter(p => 
        (p.id !== projectId && p.project_id !== projectId)
      ));
      // Clear current project if it was deleted
      if (currentProject?.id === projectId || currentProject?.project_id === projectId) {
        setCurrentProject(null);
      }
    } catch (error) {
      console.error('Failed to delete project:', error);
      alert('Failed to delete project. Please try again.');
    }
  };

  // Workflow handlers
  const handleInputComplete = (data) => {
    setInputData(data);
  };

  const handleRequirementsComplete = (data) => {
    setRequirements(data);
  };

  const handleStoriesComplete = (data) => {
    setUserStories(data);
  };

  const handleCriteriaComplete = (data) => {
    setCriteria(data);
    console.log('Criteria generated:', data);
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <div className="app-logo">🤖</div>
          <div>
            <h1>BA Copilot</h1>
            <p className="subtitle">AI Assistant for Business Analysts</p>
          </div>
        </div>
        
        {/* API Status */}
        <div className="api-status">
          {apiStatus.healthy ? (
            <div className="status-badge status-success">
              <span className="status-dot"></span>
              <span>Connected</span>
            </div>
          ) : (
            <div className="status-badge status-error">
              <AlertCircle size={16} />
              <span>Disconnected</span>
            </div>
          )}
        </div>
      </header>

      <div className="app-container">
        {/* Sidebar */}
        <Sidebar
          projects={projects}
          selectedProject={currentProject}
          onSelectProject={handleSelectProject}
          onCreateProject={handleCreateProject}
          onDeleteProject={handleDeleteProject}
        />

        {/* Main Content */}
        <main className="main-content">
          {!currentProject ? (
            <div className="welcome-screen">
              <span className="welcome-icon">👋</span>
              <h2>Welcome to BA Copilot</h2>
              <p>Create or select a project from the sidebar to get started</p>
              <div className="features-grid">
                <div className="feature-card">
                  <span className="feature-icon">📄</span>
                  <h3>Upload Documents</h3>
                  <p>Process .txt, .docx, and .pdf files</p>
                </div>
                <div className="feature-card">
                  <span className="feature-icon">📋</span>
                  <h3>Extract Requirements</h3>
                  <p>AI-powered requirement identification</p>
                </div>
                <div className="feature-card">
                  <span className="feature-icon">📖</span>
                  <h3>Generate User Stories</h3>
                  <p>Agile stories in Scrum format</p>
                </div>
                <div className="feature-card">
                  <span className="feature-icon">✅</span>
                  <h3>Acceptance Criteria</h3>
                  <p>Given-When-Then test scenarios</p>
                </div>
              </div>
            </div>
          ) : (
            <div className="workflow">
              {/* Step 1: Input Source */}
              <InputSection
                projectId={currentProject.id || currentProject.project_id}
                projectType={currentProject.type || currentProject.project_type}
                industry={currentProject.industry}
                onComplete={handleInputComplete}
              />

              {/* Step 2: Extract Requirements */}
              {inputData && (
                <RequirementsSection
                  inputId={inputData.input_id}
                  projectType={currentProject.type || currentProject.project_type}
                  industry={currentProject.industry}
                  onComplete={handleRequirementsComplete}
                />
              )}

              {/* Step 3: Generate User Stories */}
              {requirements && (
                <StoriesSection
                  inputId={inputData.input_id}
                  projectType={currentProject.type || currentProject.project_type}
                  requirements={requirements}
                  onComplete={handleStoriesComplete}
                />
              )}

              {/* Step 4: Generate Acceptance Criteria */}
              {userStories && (
                <CriteriaSection
                  userStories={userStories}
                  onComplete={handleCriteriaComplete}
                />
              )}

              {/* Show completion message when criteria is generated */}
              {criteria && (
                <div className="alert alert-success" style={{ marginTop: '2rem' }}>
                  <span>✅ Workflow complete! All acceptance criteria have been generated.</span>
                </div>
              )}
            </div>
          )}
        </main>
      </div>

      {/* Footer */}
      <footer className="app-footer">
        <p>BA Copilot MVP | Built with React & FastAPI | © 2025</p>
      </footer>
    </div>
  );
}

export default App;