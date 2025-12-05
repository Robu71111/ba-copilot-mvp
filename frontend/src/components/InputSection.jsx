import React, { useState, useRef, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { inputApi } from '../services/api';
import { Upload, FileText, Mic, Square } from 'lucide-react';
import axios from 'axios';

const InputSection = ({ projectId, onComplete }) => {
  const [activeTab, setActiveTab] = useState('upload');
  const [textInput, setTextInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [inputData, setInputData] = useState(null);
  
  // Audio recording state
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioApiAvailable, setAudioApiAvailable] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const timerRef = useRef(null);

  // Check if audio API is available
  useEffect(() => {
    checkAudioApi();
  }, []);

  const checkAudioApi = async () => {
    try {
      const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
      const response = await axios.get(`${API_URL}/api/audio/check`);
      
      if (response.data.transcription_api_configured) {
        setAudioApiAvailable(true);
      }
    } catch (error) {
      console.error('Audio API check failed:', error);
      setAudioApiAvailable(false);
    }
  };

  // File upload with drag & drop
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'text/plain': ['.txt'],
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    maxFiles: 1,
    onDrop: handleFileDrop
  });

  async function handleFileDrop(acceptedFiles) {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    setLoading(true);

    try {
      const data = await inputApi.uploadDocument(projectId, file);
      setInputData(data);
      onComplete(data);
    } catch (error) {
      alert('Upload failed: ' + error.message);
    } finally {
      setLoading(false);
    }
  }

  const handleTextSubmit = async () => {
    if (!textInput.trim() || textInput.length < 50) {
      alert('Please enter at least 50 characters');
      return;
    }

    setLoading(true);
    try {
      const data = await inputApi.submitText(projectId, textInput, 'text');
      setInputData(data);
      onComplete(data);
    } catch (error) {
      alert('Submit failed: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleMockTranscript = async () => {
    setLoading(true);
    try {
      const mockData = await inputApi.getMockTranscript();
      const data = await inputApi.submitText(projectId, mockData.transcript, 'voice_mock');
      setInputData(data);
      onComplete(data);
    } catch (error) {
      alert('Failed to load mock transcript: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  // Audio recording functions
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          channelCount: 1,
          sampleRate: 16000
        } 
      });
      
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm'
      });
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        setAudioBlob(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
      setRecordingTime(0);

      // Start timer
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);

    } catch (error) {
      alert('Microphone access denied. Please allow microphone access and try again.\n\nError: ' + error.message);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    }
  };

  const handleTranscribe = async () => {
    if (!audioBlob) {
      alert('No audio recorded');
      return;
    }

    if (recordingTime < 3) {
      alert('Recording too short. Please record at least 3 seconds of audio.');
      return;
    }

    setLoading(true);
    try {
      // Convert blob to base64
      const reader = new FileReader();
      reader.readAsDataURL(audioBlob);
      
      reader.onloadend = async () => {
        const base64Audio = reader.result.split(',')[1];
        
        // Send to backend for transcription
        const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
        const response = await axios.post(`${API_URL}/api/audio/transcribe`, {
          audio_data: base64Audio,
          project_id: projectId,
          audio_format: 'webm'
        });

        setInputData(response.data);
        onComplete(response.data);
        
        // Clear audio
        setAudioBlob(null);
        setRecordingTime(0);
      };

      reader.onerror = () => {
        alert('Failed to read audio file');
        setLoading(false);
      };
    } catch (error) {
      console.error('Transcription error:', error);
      alert('Transcription failed: ' + (error.response?.data?.detail || error.message));
      setLoading(false);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (inputData) {
    return (
      <div className="section">
        <div className="alert alert-success">
          <FileText size={20} />
          <div>
            <strong>✅ Input loaded successfully!</strong>
            <p>Text length: {inputData.text_length} characters</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="section">
      <div className="section-header">
        <h2 className="section-title">
          📥 Step 1: Input Source
        </h2>
      </div>

      <div className="tabs">
        <button
          className={`tab ${activeTab === 'upload' ? 'active' : ''}`}
          onClick={() => setActiveTab('upload')}
        >
          <Upload size={16} /> Upload Document
        </button>
        <button
          className={`tab ${activeTab === 'text' ? 'active' : ''}`}
          onClick={() => setActiveTab('text')}
        >
          <FileText size={16} /> Paste Text
        </button>
        <button
          className={`tab ${activeTab === 'voice' ? 'active' : ''}`}
          onClick={() => setActiveTab('voice')}
        >
          <Mic size={16} /> Voice Recording
        </button>
      </div>

      <div className="section-content">
        {activeTab === 'upload' && (
          <div {...getRootProps()} className={`dropzone ${isDragActive ? 'active' : ''}`}>
            <input {...getInputProps()} />
            <Upload size={48} className="dropzone-icon" />
            <p>
              {isDragActive
                ? 'Drop the file here...'
                : 'Drag & drop a file here, or click to select'}
            </p>
            <p className="dropzone-hint">Supported: .txt, .docx, .pdf</p>
          </div>
        )}

        {activeTab === 'text' && (
          <div className="text-input-section">
            <textarea
              className="form-textarea"
              placeholder="Paste your meeting transcript or requirements here..."
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              rows={10}
            />
            <button
              className="btn btn-primary"
              onClick={handleTextSubmit}
              disabled={loading || textInput.length < 50}
            >
              {loading ? 'Processing...' : 'Use This Text'}
            </button>
          </div>
        )}

        {activeTab === 'voice' && (
          <div className="voice-section">
            {audioApiAvailable ? (
              <>
                <div className="alert alert-info">
                  <Mic size={20} />
                  <div>
                    <strong>🎤 Real-Time Audio Recording</strong>
                    <p>Click "Start Recording" to record your meeting or requirements discussion. Powered by Gemini 2.0 Flash.</p>
                  </div>
                </div>

                {!isRecording && !audioBlob && (
                  <button 
                    className="btn btn-record" 
                    onClick={startRecording}
                    disabled={loading}
                  >
                    <Mic size={24} />
                    Start Recording
                  </button>
                )}

                {isRecording && (
                  <div style={{textAlign: 'center'}}>
                    <div className="recording-indicator">
                      <Mic size={48} color="white" />
                    </div>
                    <p style={{fontSize: '2rem', fontWeight: 'bold', margin: '1rem 0'}}>
                      {formatTime(recordingTime)}
                    </p>
                    <button 
                      className="btn btn-stop" 
                      onClick={stopRecording}
                    >
                      <Square size={20} />
                      Stop Recording
                    </button>
                  </div>
                )}

                {audioBlob && !isRecording && (
                  <div style={{textAlign: 'center'}}>
                    <div className="alert alert-success">
                      <p><strong>Recording complete!</strong> Duration: {formatTime(recordingTime)}</p>
                    </div>
                    <div className="btn-group" style={{justifyContent: 'center'}}>
                      <button 
                        className="btn btn-primary" 
                        onClick={handleTranscribe}
                        disabled={loading}
                      >
                        {loading ? 'Transcribing with Gemini AI...' : '🎯 Transcribe Audio'}
                      </button>
                      <button 
                        className="btn btn-secondary" 
                        onClick={() => {
                          setAudioBlob(null);
                          setRecordingTime(0);
                        }}
                      >
                        🔄 Record Again
                      </button>
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div className="alert alert-warning">
                <Mic size={20} />
                <div>
                  <strong>Audio API Not Configured</strong>
                  <p>Real-time audio transcription requires Gemini API configuration. Please check backend logs.</p>
                </div>
              </div>
            )}

            <div style={{marginTop: '2rem', textAlign: 'center'}}>
              <button className="btn btn-secondary" onClick={handleMockTranscript} disabled={loading}>
                {loading ? 'Loading...' : 'Or Load Mock Transcript for Testing'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default InputSection;