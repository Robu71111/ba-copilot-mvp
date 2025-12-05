import React, { useState } from 'react';
import { storiesApi } from '../services/api';
import { BookOpen, Download } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

const StoriesSection = ({ inputId, projectType, onComplete }) => {
  const [loading, setLoading] = useState(false);
  const [stories, setStories] = useState(null);

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const data = await storiesApi.generate(inputId, projectType);
      setStories(data);
      onComplete(data);
    } catch (error) {
      alert('Generation failed: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const downloadText = () => {
    const text = formatForDisplay(stories);
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'user_stories.txt';
    a.click();
  };

  const downloadJira = async () => {
    try {
      const result = await storiesApi.exportJira(stories);
      const blob = new Blob([result.csv], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'user_stories_jira.csv';
      a.click();
    } catch (error) {
      alert('Export failed: ' + error.message);
    }
  };

  const formatForDisplay = (data) => {
    let text = '## User Stories\n\n';
    data.stories.forEach(story => {
      text += `### ${story.story_code}: ${story.title}\n\n`;
      text += `**User Story**: ${story.user_story}\n\n`;
      text += `**Priority**: ${story.priority} | **Story Points**: ${story.story_points} | **Dependencies**: ${story.dependencies}\n\n`;
      if (story.notes) text += `**Notes**: ${story.notes}\n\n`;
      text += '---\n\n';
    });
    text += `**Total**: ${data.total_count} user stories`;
    return text;
  };

  if (stories) {
    return (
      <div className="section">
        <div className="section-header">
          <h2 className="section-title"><BookOpen size={24} /> Step 3: User Stories Generated</h2>
          <div>
            <button className="btn btn-secondary" onClick={() => setStories(null)}>
              Regenerate
            </button>
            <button className="btn btn-primary" onClick={downloadText} style={{marginLeft: '0.5rem'}}>
              <Download size={16} /> Text
            </button>
            <button className="btn btn-primary" onClick={downloadJira} style={{marginLeft: '0.5rem'}}>
              <Download size={16} /> JIRA CSV
            </button>
          </div>
        </div>
        <div className="markdown-content">
          <ReactMarkdown>{formatForDisplay(stories)}</ReactMarkdown>
        </div>
      </div>
    );
  }

  return (
    <div className="section">
      <div className="section-header">
        <h2 className="section-title">📖 Step 3: Generate User Stories</h2>
      </div>
      <button className="btn btn-primary" onClick={handleGenerate} disabled={loading}>
        {loading ? 'Generating...' : '🚀 Generate User Stories'}
      </button>
    </div>
  );
};

export default StoriesSection;