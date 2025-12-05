import React, { useState } from 'react';
import { requirementsApi } from '../services/api';
import { FileCheck, Download } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

const RequirementsSection = ({ inputId, projectType, industry, onComplete }) => {
  const [loading, setLoading] = useState(false);
  const [requirements, setRequirements] = useState(null);

  const handleExtract = async () => {
    setLoading(true);
    try {
      const data = await requirementsApi.extract(inputId, projectType, industry);
      setRequirements(data);
      onComplete(data);
    } catch (error) {
      alert('Extraction failed: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const downloadText = () => {
    const text = formatForDisplay(requirements);
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'requirements.txt';
    a.click();
  };

  const formatForDisplay = (reqs) => {
    let text = '## Functional Requirements\n\n';
    reqs.functional.forEach(req => {
      text += `**${req.req_code}**: ${req.description}\n\n`;
    });
    text += '\n## Non-Functional Requirements\n\n';
    reqs.non_functional.forEach(req => {
      text += `**${req.req_code}**: ${req.description}\n\n`;
    });
    text += `\n---\n**Total**: ${reqs.total_count} requirements`;
    return text;
  };

  if (requirements) {
    return (
      <div className="section">
        <div className="section-header">
          <h2 className="section-title"><FileCheck size={24} /> Step 2: Requirements Extracted</h2>
          <div>
            <button className="btn btn-secondary" onClick={() => setRequirements(null)}>
              Regenerate
            </button>
            <button className="btn btn-primary" onClick={downloadText} style={{marginLeft: '0.5rem'}}>
              <Download size={16} /> Download
            </button>
          </div>
        </div>
        <div className="markdown-content">
          <ReactMarkdown>{formatForDisplay(requirements)}</ReactMarkdown>
        </div>
      </div>
    );
  }

  return (
    <div className="section">
      <div className="section-header">
        <h2 className="section-title">📋 Step 2: Extract Requirements</h2>
      </div>
      <button className="btn btn-primary" onClick={handleExtract} disabled={loading}>
        {loading ? 'Extracting...' : '🚀 Extract Requirements'}
      </button>
    </div>
  );
};

export default RequirementsSection;