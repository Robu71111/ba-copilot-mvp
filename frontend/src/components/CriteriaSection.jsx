import React, { useState } from 'react';
import { criteriaApi } from '../services/api';
import { CheckSquare, Download } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

const CriteriaSection = ({ userStories, onComplete }) => {
  const [selectedStory, setSelectedStory] = useState(null);
  const [loading, setLoading] = useState(false);
  const [criteria, setCriteria] = useState(null);

  const handleGenerate = async () => {
    if (!selectedStory) return;
    
    setLoading(true);
    try {
      const storyText = `${selectedStory.story_code}: ${selectedStory.title}\n${selectedStory.user_story}`;
      const data = await criteriaApi.generate(selectedStory.story_id || 1, storyText);
      setCriteria(data);
      onComplete(data);
    } catch (error) {
      alert('Generation failed: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const downloadText = () => {
    const text = formatForDisplay(criteria);
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'acceptance_criteria.txt';
    a.click();
  };

  const downloadGherkin = async () => {
    try {
      const result = await criteriaApi.exportGherkin(criteria, selectedStory.title);
      const blob = new Blob([result.gherkin], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'acceptance_criteria.feature';
      a.click();
    } catch (error) {
      alert('Export failed: ' + error.message);
    }
  };

  const formatForDisplay = (data) => {
    let text = '## Acceptance Criteria (Given-When-Then)\n\n';
    data.criteria.forEach((c, idx) => {
      text += `### Scenario ${idx + 1}: ${c.scenario_name}\n\n`;
      text += `**GIVEN** ${c.given}\n\n`;
      text += `**WHEN** ${c.when}\n\n`;
      text += `**THEN** ${c.then}\n\n`;
      text += '---\n\n';
    });
    text += `**Total**: ${data.total_scenarios} scenarios`;
    return text;
  };

  if (criteria) {
    return (
      <div className="section">
        <div className="section-header">
          <h2 className="section-title"><CheckSquare size={24} /> Step 4: Acceptance Criteria Generated</h2>
          <div>
            <button className="btn btn-secondary" onClick={() => setCriteria(null)}>
              Generate More
            </button>
            <button className="btn btn-primary" onClick={downloadText} style={{marginLeft: '0.5rem'}}>
              <Download size={16} /> Text
            </button>
            <button className="btn btn-primary" onClick={downloadGherkin} style={{marginLeft: '0.5rem'}}>
              <Download size={16} /> Gherkin
            </button>
          </div>
        </div>
        <div className="markdown-content">
          <ReactMarkdown>{formatForDisplay(criteria)}</ReactMarkdown>
        </div>
      </div>
    );
  }

  return (
    <div className="section">
      <div className="section-header">
        <h2 className="section-title">✅ Step 4: Generate Acceptance Criteria</h2>
      </div>
      <div className="form-group">
        <label className="form-label">Select a user story:</label>
        <select 
          className="form-select"
          onChange={(e) => setSelectedStory(userStories.stories[e.target.value])}
        >
          <option value="">Choose a story...</option>
          {userStories.stories.map((story, idx) => (
            <option key={idx} value={idx}>
              {story.story_code}: {story.title}
            </option>
          ))}
        </select>
      </div>
      {selectedStory && (
        <div className="alert alert-info">
          <strong>Selected Story:</strong> {selectedStory.user_story}
        </div>
      )}
      <button 
        className="btn btn-primary" 
        onClick={handleGenerate} 
        disabled={loading || !selectedStory}
      >
        {loading ? 'Generating...' : '🚀 Generate Acceptance Criteria'}
      </button>
    </div>
  );
};

export default CriteriaSection;