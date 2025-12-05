import React, { useState } from 'react';
import { 
  FolderPlus, 
  Trash2
} from 'lucide-react';

const Sidebar = ({ 
  projects = [],
  selectedProject = null, 
  onSelectProject = () => {}, 
  onCreateProject = () => {}, 
  onDeleteProject = () => {} 
}) => {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    type: 'Web Application',
    industry: 'Technology'
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onCreateProject(formData);
    setFormData({
      name: '',
      type: 'Web Application',
      industry: 'Technology'
    });
    setShowCreateForm(false);
  };

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="sidebar">
      {/* Sidebar Header */}
      <div className="sidebar-header">
        <h2>
          <span>Projects</span>
          <button
            className="btn-icon"
            onClick={() => setShowCreateForm(!showCreateForm)}
            title="Create new project"
          >
            <FolderPlus size={20} />
          </button>
        </h2>
        <p className="sidebar-subtitle">
          {projects.length} {projects.length === 1 ? 'project' : 'projects'}
        </p>
      </div>

      {/* Create Project Form */}
      {showCreateForm && (
        <form className="create-form" onSubmit={handleSubmit}>
          <h3>New Project</h3>
          <input
            type="text"
            name="name"
            placeholder="Project name"
            value={formData.name}
            onChange={handleInputChange}
            required
          />
          <select
            name="type"
            value={formData.type}
            onChange={handleInputChange}
          >
            <option value="Web Application">Web Application</option>
            <option value="Mobile App">Mobile App</option>
            <option value="Desktop Software">Desktop Software</option>
            <option value="API/Backend">API/Backend</option>
            <option value="E-commerce">E-commerce</option>
            <option value="Other">Other</option>
          </select>
          <select
            name="industry"
            value={formData.industry}
            onChange={handleInputChange}
          >
            <option value="Technology">Technology</option>
            <option value="Finance">Finance</option>
            <option value="Healthcare">Healthcare</option>
            <option value="E-commerce">E-commerce</option>
            <option value="Education">Education</option>
            <option value="Other">Other</option>
          </select>
          <div className="btn-group">
            <button type="submit" className="btn btn-primary">
              Create Project
            </button>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => setShowCreateForm(false)}
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      {/* Project List */}
      <div className="project-list">
        {projects.length === 0 ? (
          <div className="empty-state">
            <p>No projects yet. Create your first project to get started!</p>
          </div>
        ) : (
          projects.map((project) => {
            // Handle different property naming conventions
            const projectId = project.id || project.project_id;
            const projectName = project.name || project.project_name || 'Unnamed Project';
            const projectType = project.type || project.project_type || 'N/A';
            const projectIndustry = project.industry || 'N/A';
            
            // Check if this project is selected
            const isSelected = selectedProject && (
              selectedProject.id === projectId || 
              selectedProject.project_id === projectId
            );

            return (
              <div
                key={projectId}
                className={`project-item ${isSelected ? 'active' : ''}`}
                onClick={() => onSelectProject(project)}
              >
                <div className="project-info">
                  <div className="project-icon">
                    {projectName.charAt(0).toUpperCase()}
                  </div>
                  <div className="project-details">
                    <div className="project-name">{projectName}</div>
                    <div className="project-meta">
                      {projectType} • {projectIndustry}
                    </div>
                  </div>
                </div>
                <button
                  className="btn-icon-small"
                  onClick={(e) => {
                    e.stopPropagation();
                    if (window.confirm(`Delete project "${projectName}"?`)) {
                      onDeleteProject(projectId);
                    }
                  }}
                  title="Delete project"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            );
          })
        )}
      </div>

      {/* Project Summary (if project selected) */}
      {selectedProject && (
        <div className="project-summary">
          <h3>Project Summary</h3>
          <div className="summary-card">
            <div className="summary-title">
              {selectedProject.name || selectedProject.project_name || 'Unnamed Project'}
            </div>
            <div className="summary-details">
              <span>{selectedProject.type || selectedProject.project_type || 'N/A'}</span>
              <span>•</span>
              <span>{selectedProject.industry || 'N/A'}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Sidebar;