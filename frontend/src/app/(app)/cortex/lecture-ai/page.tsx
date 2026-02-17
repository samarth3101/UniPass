"use client";

import { useState, useEffect } from 'react';
import { getAuth, getUser } from '@/lib/auth';
import api from '@/services/api';
import HelpGuide from '@/components/HelpGuide/HelpGuide';
import { getHelpContent } from '@/components/HelpGuide/helpGuideConfig';
import './lecture-ai.scss';

// Icon components
const UploadIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ display: 'inline-block', verticalAlign: 'middle', marginRight: '6px' }}>
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
    <polyline points="17 8 12 3 7 8"></polyline>
    <line x1="12" y1="3" x2="12" y2="15"></line>
  </svg>
);

const RocketIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ display: 'inline-block', verticalAlign: 'middle', marginRight: '6px' }}>
    <path d="M4.5 16.5c-1.5 1.25-2 5-2 5s3.75-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"></path>
    <path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"></path>
    <path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"></path>
    <path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"></path>
  </svg>
);

const ChartIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ display: 'inline-block', verticalAlign: 'middle', marginRight: '6px' }}>
    <line x1="12" y1="20" x2="12" y2="10"></line>
    <line x1="18" y1="20" x2="18" y2="4"></line>
    <line x1="6" y1="20" x2="6" y2="16"></line>
  </svg>
);

const ClipboardIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ display: 'inline-block', verticalAlign: 'middle', marginRight: '6px' }}>
    <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path>
    <rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect>
  </svg>
);

const CheckIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ display: 'inline-block', verticalAlign: 'middle', marginRight: '4px' }}>
    <polyline points="20 6 9 17 4 12"></polyline>
  </svg>
);

const ClockIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ display: 'inline-block', verticalAlign: 'middle', marginRight: '4px' }}>
    <circle cx="12" cy="12" r="10"></circle>
    <polyline points="12 6 12 12 16 14"></polyline>
  </svg>
);

const XIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ display: 'inline-block', verticalAlign: 'middle', marginRight: '4px' }}>
    <line x1="18" y1="6" x2="6" y2="18"></line>
    <line x1="6" y1="6" x2="18" y2="18"></line>
  </svg>
);

const TagIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ display: 'inline-block', verticalAlign: 'middle', marginRight: '6px' }}>
    <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path>
    <line x1="7" y1="7" x2="7.01" y2="7"></line>
  </svg>
);

const BotIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ display: 'inline-block', verticalAlign: 'middle', marginRight: '6px' }}>
    <rect x="3" y="11" width="18" height="10" rx="2"></rect>
    <circle cx="12" cy="5" r="2"></circle>
    <path d="M12 7v4"></path>
    <line x1="8" y1="16" x2="8" y2="16"></line>
    <line x1="16" y1="16" x2="16" y2="16"></line>
  </svg>
);

const FileTextIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ display: 'inline-block', verticalAlign: 'middle', marginRight: '6px' }}>
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
    <polyline points="14 2 14 8 20 8"></polyline>
    <line x1="16" y1="13" x2="8" y2="13"></line>
    <line x1="16" y1="17" x2="8" y2="17"></line>
    <polyline points="10 9 9 9 8 9"></polyline>
  </svg>
);

interface LectureReport {
  report_id: number;
  event: {
    id: number;
    title: string;
    description: string;
    start_time: string;
  };
  status: 'processing' | 'completed' | 'failed';
  error_message?: string;
  transcript?: string;
  keywords?: string[];
  summary?: {
    event_overview?: string;
    key_topics_discussed?: string[];
    important_quotes?: string[];
    technical_highlights?: string;
    audience_engagement_summary?: string;
    recommended_followup_actions?: string[];
  };
  audio_filename: string;
  generated_at: string;
  generated_by: {
    id: number;
    email: string;
    full_name: string;
  };
}

export default function LectureAIPage() {
  const [loading, setLoading] = useState(false);
  const [selectedEventId, setSelectedEventId] = useState<string>('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [report, setReport] = useState<LectureReport | null>(null);
  const [error, setError] = useState<string>('');
  const [uploadSuccess, setUploadSuccess] = useState(false);

  const user = getUser();
  const helpContent = getHelpContent('lecture-intelligence');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file type
      const validTypes = ['audio/mpeg', 'audio/wav', 'audio/mp4', 'audio/x-m4a'];
      const validExtensions = ['.mp3', '.wav', '.m4a'];
      const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
      
      if (!validExtensions.includes(fileExtension)) {
        setError('Invalid file format. Please upload MP3, WAV, or M4A files only.');
        setSelectedFile(null);
        return;
      }

      // Validate file size (100MB)
      const maxSize = 100 * 1024 * 1024;
      if (file.size > maxSize) {
        setError('File size exceeds 100MB limit.');
        setSelectedFile(null);
        return;
      }

      setSelectedFile(file);
      setError('');
    }
  };

  const handleUpload = async () => {
    if (!selectedEventId) {
      setError('Please enter an Event ID');
      return;
    }

    if (!selectedFile) {
      setError('Please select an audio file');
      return;
    }

    setLoading(true);
    setError('');
    setUploadSuccess(false);

    try {
      const token = getAuth();
      if (!token) {
        setError('Please login first');
        setLoading(false);
        return;
      }

      // Create FormData for file upload
      const formData = new FormData();
      formData.append('file', selectedFile);

      // Upload audio file (use /api proxy for HTTPS compatibility)
      const apiBase = typeof window !== 'undefined' && window.location.protocol === 'https:' ? '/api' : 'http://localhost:8000';
      const response = await fetch(`${apiBase}/ai/lecture/upload/${selectedEventId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        let errorMessage = 'Upload failed';
        const contentType = response.headers.get('content-type');
        
        if (contentType && contentType.includes('application/json')) {
          try {
            const errorData = await response.json();
            errorMessage = errorData.detail || errorMessage;
          } catch (e) {
            errorMessage = `Server error: ${response.status} ${response.statusText}`;
          }
        } else {
          const textError = await response.text();
          errorMessage = textError || `Server error: ${response.status} ${response.statusText}`;
        }
        
        throw new Error(errorMessage);
      }

      const data = await response.json();
      setUploadSuccess(true);
      
      // Fetch the generated report
      await fetchReport(selectedEventId);

      // Reset form
      setSelectedFile(null);
      const fileInput = document.getElementById('audio-file') as HTMLInputElement;
      if (fileInput) fileInput.value = '';

    } catch (err: any) {
      console.error('Upload error:', err);
      setError(err.message || 'Failed to upload audio file');
    } finally {
      setLoading(false);
    }
  };

  const fetchReport = async (eventId: string) => {
    setLoading(true);
    setError('');

    try {
      const data = await api.get(`/ai/lecture/report/${eventId}`);
      setReport(data);
    } catch (err: any) {
      console.error('Fetch report error:', err);
      setError(err.message || 'Failed to fetch report');
      setReport(null);
    } finally {
      setLoading(false);
    }
  };

  const handleViewReport = () => {
    if (selectedEventId) {
      fetchReport(selectedEventId);
    } else {
      setError('Please enter an Event ID');
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const renderSummaryContent = (content: any) => {
    if (Array.isArray(content)) {
      return (
        <ul>
          {content.map((item, idx) => (
            <li key={idx}>{item}</li>
          ))}
        </ul>
      );
    }
    return <p>{content}</p>;
  };

  return (
    <div className="cortex-lie-page">
      <h1>Cortex LIE</h1>
      <p className="subtitle">Lecture Intelligence Engine - AI-Powered Event Analysis</p>

      {/* Upload Section */}
      <div className="upload-section">
        <h2><UploadIcon /> Upload Lecture Audio</h2>
        <div className="upload-form">
          <div className="form-group">
            <label htmlFor="event-id">Event ID</label>
            <input
              id="event-id"
              type="number"
              placeholder="Enter Event ID"
              value={selectedEventId}
              onChange={(e) => setSelectedEventId(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label htmlFor="audio-file">Audio File (MP3, WAV, M4A - Max 100MB)</label>
            <input
              id="audio-file"
              type="file"
              accept=".mp3,.wav,.m4a"
              onChange={handleFileChange}
              className="file-input"
            />
            {selectedFile && (
              <p style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                Selected: {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
              </p>
            )}
          </div>

          {error && <div className="error-alert">{error}</div>}
          {uploadSuccess && (
            <div style={{ 
              background: '#d1fae5', 
              borderLeft: '4px solid #10b981', 
              padding: '1rem', 
              borderRadius: '8px',
              color: '#065f46'
            }}>
              <CheckIcon /> Audio uploaded and processing initiated successfully!
            </div>
          )}

          <button 
            className="upload-btn" 
            onClick={handleUpload}
            disabled={loading || !selectedEventId || !selectedFile}
          >
            {loading ? <><ClockIcon /> Processing...</> : <><RocketIcon /> Upload & Process</>}
          </button>

          <button 
            className="upload-btn" 
            onClick={handleViewReport}
            disabled={loading || !selectedEventId}
            style={{ background: 'linear-gradient(135deg, #10b981, #3b82f6)' }}
          >
            <ChartIcon /> View Existing Report
          </button>
        </div>
      </div>

      {/* Report Section */}
      <div className="report-section">
        <h2><ClipboardIcon /> Lecture Intelligence Report</h2>

        {loading && (
          <div className="loading">
            <p><ClockIcon /> Loading report...</p>
          </div>
        )}

        {!loading && !report && !error && (
          <div className="no-data">
            <p>No report data. Upload an audio file or enter an Event ID to view the report.</p>
          </div>
        )}

        {!loading && report && (
          <div className="report-content">
            {/* Meta Information */}
            <div className="meta-info">
              <div className="meta-item">
                <span className="label">Event</span>
                <span className="value">{report.event.title}</span>
              </div>
              <div className="meta-item">
                <span className="label">Event ID</span>
                <span className="value">#{report.event.id}</span>
              </div>
              <div className="meta-item">
                <span className="label">Status</span>
                <span className={`status-badge ${report.status}`}>
                  {report.status === 'completed' && <><CheckIcon /> Completed</>}
                  {report.status === 'processing' && <><ClockIcon /> Processing</>}
                  {report.status === 'failed' && <><XIcon /> Failed</>}
                </span>
              </div>
              <div className="meta-item">
                <span className="label">Generated</span>
                <span className="value">{formatDate(report.generated_at)}</span>
              </div>
              <div className="meta-item">
                <span className="label">Generated By</span>
                <span className="value">{report.generated_by.full_name || report.generated_by.email}</span>
              </div>
            </div>

            {report.status === 'failed' && report.error_message && (
              <div className="error-alert">
                <strong>Error:</strong> {report.error_message}
              </div>
            )}

            {report.status === 'completed' && (
              <>
                {/* Keywords */}
                {report.keywords && report.keywords.length > 0 && (
                  <div className="keywords-section">
                    <h3><TagIcon /> Extracted Keywords</h3>
                    <div className="keywords-grid">
                      {report.keywords.map((keyword, idx) => (
                        <span key={idx} className="keyword-badge">
                          {keyword}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* AI Summary */}
                {report.summary && (
                  <div className="summary-section">
                    <h3><BotIcon /> AI-Generated Summary</h3>
                    <div className="summary-cards">
                      {Object.entries(report.summary).map(([key, value]) => (
                        <div key={key} className="summary-card">
                          <div className="card-title">
                            {key.replace(/_/g, ' ')}
                          </div>
                          <div className="card-content">
                            {renderSummaryContent(value)}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Transcript */}
                {report.transcript && (
                  <div className="transcript-section">
                    <h3><FileTextIcon /> Full Transcript</h3>
                    <div className="transcript-box">
                      {report.transcript}
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </div>
      
      {helpContent && <HelpGuide content={helpContent} />}
    </div>
  );
}
