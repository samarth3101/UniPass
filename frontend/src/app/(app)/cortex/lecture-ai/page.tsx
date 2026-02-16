"use client";

import { useState, useEffect } from 'react';
import { getAuth, getUser } from '@/lib/auth';
import api from '@/services/api';
import HelpGuide from '@/components/HelpGuide/HelpGuide';
import { getHelpContent } from '@/components/HelpGuide/helpGuideConfig';
import './lecture-ai.scss';

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

      // Upload audio file
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/ai/lecture/upload/${selectedEventId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Upload failed');
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
        <h2>📤 Upload Lecture Audio</h2>
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
              ✅ Audio uploaded and processing initiated successfully!
            </div>
          )}

          <button 
            className="upload-btn" 
            onClick={handleUpload}
            disabled={loading || !selectedEventId || !selectedFile}
          >
            {loading ? '⏳ Processing...' : '🚀 Upload & Process'}
          </button>

          <button 
            className="upload-btn" 
            onClick={handleViewReport}
            disabled={loading || !selectedEventId}
            style={{ background: 'linear-gradient(135deg, #10b981, #3b82f6)' }}
          >
            📊 View Existing Report
          </button>
        </div>
      </div>

      {/* Report Section */}
      <div className="report-section">
        <h2>📋 Lecture Intelligence Report</h2>

        {loading && (
          <div className="loading">
            <p>⏳ Loading report...</p>
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
                  {report.status === 'completed' && '✅ Completed'}
                  {report.status === 'processing' && '⏳ Processing'}
                  {report.status === 'failed' && '❌ Failed'}
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
                    <h3>🏷️ Extracted Keywords</h3>
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
                    <h3>🤖 AI-Generated Summary</h3>
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
                    <h3>📝 Full Transcript</h3>
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
