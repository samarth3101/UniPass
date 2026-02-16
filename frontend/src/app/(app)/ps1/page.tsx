"use client";

import { useState, useEffect } from 'react';
import { getAuth, getUser, isAuthenticated } from '@/lib/auth';
import api from '@/services/api';
import './ps1.scss';

export default function CortexCorePage() {
  const [selectedStudent, setSelectedStudent] = useState('SOE23201020038');
  const [transcriptData, setTranscriptData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [snapshotData, setSnapshotData] = useState<any[]>([]);
  const [userEmail, setUserEmail] = useState<string | null>(null);
  const [certificateId, setCertificateId] = useState('');
  
  // New Phase 3 State
  const [selectedEvent, setSelectedEvent] = useState('');
  const [auditHistory, setAuditHistory] = useState<any>(null);
  const [fraudReport, setFraudReport] = useState<any>(null);
  const [attendanceId, setAttendanceId] = useState('');
  const [invalidationReason, setInvalidationReason] = useState('');
  const [correctionData, setCorrectionData] = useState({
    type: 'attendance',
    oldValue: '',
    newValue: '',
    reason: ''
  });
  
  // Check authentication on mount
  useEffect(() => {
    const user = getUser();
    if (user) {
      setUserEmail(user.email);
    }
  }, []);
  
  // Test Transcript Generator
  const fetchTranscript = async () => {
    if (!selectedStudent) {
      alert('Please enter a student PRN');
      return;
    }
    
    setLoading(true);
    try {
      const token = getAuth();
      if (!token) {
        alert('⚠️ Please login first to access Cortex CORE features');
        setLoading(false);
        return;
      }
      
      const data = await api.get(`/ps1/transcript/${selectedStudent}`);
      setTranscriptData(data);
    } catch (error: any) {
      console.error('Error:', error);
      if (error.message.includes('401')) {
        alert('🔒 Authentication required. Please login to access this feature.');
      } else {
        alert(`Failed to fetch transcript: ${error.message || 'Unknown error'}`);
      }
    } finally {
      setLoading(false);
    }
  };
  
  // Download PDF Transcript
  const downloadTranscriptPDF = async () => {
    if (!selectedStudent) {
      alert('Please enter a student PRN');
      return;
    }
    
    setLoading(true);
    try {
      const token = getAuth();
      if (!token) {
        alert('⚠️ Please login first to access Cortex CORE features');
        setLoading(false);
        return;
      }
      
      const response = await fetch(`http://localhost:8000/ps1/transcript/${selectedStudent}/pdf`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        if (response.status === 401) {
          alert('🔒 Authentication required. Please login to access this feature.');
        } else {
          alert('Failed to download PDF');
        }
        setLoading(false);
        return;
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `transcript_${selectedStudent}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      alert('✅ PDF downloaded successfully!');
    } catch (error) {
      console.error('Error:', error);
      alert('Error downloading PDF. Please check your connection.');
    } finally {
      setLoading(false);
    }
  };
  
  // Fetch Student Snapshots
  const fetchSnapshots = async () => {
    if (!selectedStudent) {
      alert('Please enter a student PRN');
      return;
    }
    
    setLoading(true);
    try {
      const token = getAuth();
      if (!token) {
        alert('⚠️ Please login first to access Cortex CORE features');
        setLoading(false);
        return;
      }
      
      const data = await api.get(`/ps1/snapshots/student/${selectedStudent}`);
      setSnapshotData(data);
    } catch (error: any) {
      console.error('Error:', error);
      if (error.message.includes('401')) {
        alert('🔒 Authentication required. Please login to access this feature.');
      } else {
        alert(`Failed to fetch snapshots: ${error.message || 'Unknown error'}`);
      }
    } finally {
      setLoading(false);
    }
  };
  
  // Fetch Audit History (Phase 3)
  const fetchAuditHistory = async () => {
    if (!selectedEvent || !selectedStudent) {
      alert('Please enter both Event ID and Student PRN');
      return;
    }
    
    setLoading(true);
    try {
      const token = getAuth();
      if (!token) {
        alert('⚠️ Please login first to access Cortex CORE features');
        setLoading(false);
        return;
      }
      
      const data = await api.get(`/ps1/audit/${selectedEvent}/${selectedStudent}`);
      setAuditHistory(data);
    } catch (error: any) {
      console.error('Error:', error);
      if (error.message.includes('401')) {
        alert('🔒 Authentication required. Please login to access this feature.');
      } else {
        alert(`Failed to fetch audit history: ${error.message || 'Unknown error'}`);
      }
    } finally {
      setLoading(false);
    }
  };
  
  // Run Fraud Detection (Phase 3)
  const runFraudDetection = async () => {
    if (!selectedEvent) {
      alert('Please enter an Event ID');
      return;
    }
    
    setLoading(true);
    try {
      const token = getAuth();
      if (!token) {
        alert('⚠️ Please login first to access Cortex CORE features');
        setLoading(false);
        return;
      }
      
      const data = await api.get(`/ps1/fraud/detect/${selectedEvent}`);
      setFraudReport(data);
    } catch (error: any) {
      console.error('Error:', error);
      if (error.message.includes('401')) {
        alert('🔒 Authentication required. Please login to access this feature.');
      } else {
        alert(`Failed to run fraud detection: ${error.message || 'Unknown error'}`);
      }
    } finally {
      setLoading(false);
    }
  };
  
  // Invalidate Attendance (Phase 3)
  const invalidateAttendance = async () => {
    if (!attendanceId || !invalidationReason) {
      alert('Please provide both Attendance ID and reason');
      return;
    }
    
    setLoading(true);
    try {
      const token = getAuth();
      if (!token) {
        alert('⚠️ Please login first to access Cortex CORE features');
        setLoading(false);
        return;
      }
      
      const data = await api.post(`/ps1/attendance/${attendanceId}/invalidate`, {
        reason: invalidationReason
      });
      alert(`✅ ${data.message}`);
      setAttendanceId('');
      setInvalidationReason('');
    } catch (error: any) {
      console.error('Error:', error);
      if (error.message.includes('401')) {
        alert('🔒 Authentication required. Please login to access this feature.');
      } else {
        alert(`❌ ${error.message}`);
      }
    } finally {
      setLoading(false);
    }
  };
  
  // Submit Correction (Phase 3)
  const submitCorrection = async () => {
    if (!selectedEvent || !selectedStudent || !correctionData.reason) {
      alert('Please fill all correction fields');
      return;
    }
    
    setLoading(true);
    try {
      const token = getAuth();
      if (!token) {
        alert('⚠️ Please login first to access Cortex CORE features');
        setLoading(false);
        return;
      }
      
      const data = await api.post(`/ps1/participation/${selectedEvent}/${selectedStudent}/correct`, {
        correction_type: correctionData.type,
        old_value: correctionData.oldValue,
        new_value: correctionData.newValue,
        reason: correctionData.reason
      });
      alert(`✅ ${data.message}`);
      setCorrectionData({ type: 'attendance', oldValue: '', newValue: '', reason: '' });
    } catch (error: any) {
      console.error('Error:', error);
      if (error.message.includes('401')) {
        alert('🔒 Authentication required. Please login to access this feature.');
      } else {
        alert(`❌ ${error.message}`);
      }
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="ps1-features-page">
      <div className="page-header">
        <h1 className="cortex-title">
          Cortex <span className="core-gradient">CORE</span>
        </h1>
        <p className="subtitle">Campus Organization & Record Engine - Advanced Intelligence System</p>
        
        <div className="auth-info">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10"/>
            <path d="M12 8v4"/>
            <path d="M12 16h.01"/>
          </svg>
          {userEmail ? (
            <span>Logged in as <strong>{userEmail}</strong> • Sample PRN: <strong>SOE23201020038</strong></span>
          ) : (
            <span>⚠️ Login required to access features • Sample PRN: <strong>SOE23201020038</strong></span>
          )}
        </div>
      </div>
      
      {/* Feature Cards Grid - All Features */}
      <div className="feature-grid">
        
        {/* Feature 1: Participation Reconciliation */}
        <div className="feature-card">
          <div className="feature-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="8"/>
              <path d="m21 21-4.35-4.35"/>
            </svg>
          </div>
          <h2>Conflict Detection</h2>
          <p>Participation reconciliation with trust scoring</p>
          <a href="/conflicts" className="btn btn-primary">
            <span>Open Dashboard</span>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="m9 18 6-6-6-6"/>
            </svg>
          </a>
        </div>
        
        {/* Feature 2: Longitudinal Identity */}
        <div className="feature-card">
          <div className="feature-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 3h18v18H3z"/>
              <path d="m3 9 9-7 9 7"/>
            </svg>
          </div>
          <h2>Student Snapshots</h2>
          <p>Historical profile tracking with temporal queries</p>
          <div className="test-section">
            <input
              type="text"
              placeholder="Student PRN"
              value={selectedStudent}
              onChange={(e) => setSelectedStudent(e.target.value)}
              className="input"
            />
            <button 
              onClick={fetchSnapshots}
              disabled={loading}
              className="btn btn-secondary"
            >
              {loading ? 'Loading...' : 'View History'}
            </button>
          </div>
        </div>
        
        {/* Feature 3: Verifiable Certificates */}
        <div className="feature-card">
          <div className="feature-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
              <polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
          </div>
          <h2>Certificate System</h2>
          <p>SHA-256 verification + fraud detection</p>
          <div className="test-section">
            <input
              type="text"
              placeholder="Certificate ID"
              value={certificateId}
              onChange={(e) => setCertificateId(e.target.value)}
              className="input"
            />
            <a 
              href={certificateId ? `/verify?cert=${certificateId}` : '/verify'} 
              target="_blank"
              className="btn btn-primary"
            >
              Verify
            </a>
          </div>
        </div>
        
        {/* Feature 4: Retroactive Changes */}
        <div className="feature-card">
          <div className="feature-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="1 4 1 10 7 10"/>
              <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/>
            </svg>
          </div>
          <h2>Audit Trail</h2>
          <p>Change history, revocations, invalidations</p>
          <div className="test-section">
            <input
              type="text"
              placeholder="Event ID"
              value={selectedEvent}
              onChange={(e) => setSelectedEvent(e.target.value)}
              className="input"
            />
            <input
              type="text"
              placeholder="Student PRN"
              value={selectedStudent}
              onChange={(e) => setSelectedStudent(e.target.value)}
              className="input"
            />
            <button 
              onClick={fetchAuditHistory}
              disabled={loading}
              className="btn btn-secondary"
            >
              View Audit
            </button>
          </div>
        </div>
        
        {/* Feature 5: Multi-Role */}
        <div className="feature-card">
          <div className="feature-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
            </svg>
          </div>
          <h2>Multi-Role Engine</h2>
          <p>Track multiple roles per student</p>
          <div className="role-badges">
            <span className="role-badge">PARTICIPANT</span>
            <span className="role-badge">VOLUNTEER</span>
            <span className="role-badge">SPEAKER</span>
            <span className="role-badge">ORGANIZER</span>
            <span className="role-badge">JUDGE</span>
            <span className="role-badge">MENTOR</span>
          </div>
        </div>
        
        {/* Transcript Generator */}
        <div className="feature-card">
          <div className="feature-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
              <polyline points="10 9 9 9 8 9"/>
            </svg>
          </div>
          <h2>Transcript Generator</h2>
          <p>JSON & PDF participation transcripts</p>
          <div className="test-section">
            <input
              type="text"
              placeholder="Student PRN"
              value={selectedStudent}
              onChange={(e) => setSelectedStudent(e.target.value)}
              className="input"
            />
            <div className="button-group">
              <button 
                onClick={fetchTranscript}
                disabled={loading}
                className="btn btn-secondary"
              >
                View JSON
              </button>
              <button 
                onClick={downloadTranscriptPDF}
                disabled={loading}
                className="btn btn-primary"
              >
                Download PDF
              </button>
            </div>
          </div>
        </div>
        
      </div>

      {/* Cortex Exclusive Features */}
      <div className="phase3-section">
        <h2 className="section-title">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 2L2 7l10 5 10-5-10-5z"/>
            <path d="M2 17l10 5 10-5"/>
            <path d="M2 12l10 5 10-5"/>
          </svg>
          Cortex <span className="core-gradient">Exclusives</span>
        </h2>

        <div className="phase3-grid">
          
          {/* Attendance Invalidation */}
          <div className="phase3-card">
            <h3>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="15" y1="9" x2="9" y2="15"/>
                <line x1="9" y1="9" x2="15" y2="15"/>
              </svg>
              Attendance Invalidation
            </h3>
            <p>Mark fraudulent attendance as invalid while preserving records</p>
            <div className="form-group">
              <input
                type="number"
                placeholder="Attendance Record ID"
                value={attendanceId}
                onChange={(e) => setAttendanceId(e.target.value)}
                className="input"
              />
              <textarea
                placeholder="Reason for invalidation"
                value={invalidationReason}
                onChange={(e) => setInvalidationReason(e.target.value)}
                className="textarea"
                rows={3}
              />
              <button 
                onClick={invalidateAttendance}
                disabled={loading}
                className="btn btn-danger"
              >
                {loading ? 'Processing...' : 'Invalidate Attendance'}
              </button>
            </div>
          </div>
          
          {/* Data Correction Workflow */}
          <div className="phase3-card">
            <h3>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
              </svg>
              Data Correction
            </h3>
            <p>Apply retroactive corrections with audit trail</p>
            <div className="form-group">
              <div className="input-row">
                <input
                  type="text"
                  placeholder="Event ID"
                  value={selectedEvent}
                  onChange={(e) => setSelectedEvent(e.target.value)}
                  className="input"
                />
                <input
                  type="text"
                  placeholder="Student PRN"
                  value={selectedStudent}
                  onChange={(e) => setSelectedStudent(e.target.value)}
                  className="input"
                />
              </div>
              <select 
                value={correctionData.type}
                onChange={(e) => setCorrectionData({...correctionData, type: e.target.value})}
                className="select"
              >
                <option value="attendance">Attendance</option>
                <option value="certificate">Certificate</option>
                <option value="registration">Registration</option>
              </select>
              <div className="input-row">
                <input
                  type="text"
                  placeholder="Old Value"
                  value={correctionData.oldValue}
                  onChange={(e) => setCorrectionData({...correctionData, oldValue: e.target.value})}
                  className="input"
                />
                <input
                  type="text"
                  placeholder="New Value"
                  value={correctionData.newValue}
                  onChange={(e) => setCorrectionData({...correctionData, newValue: e.target.value})}
                  className="input"
                />
              </div>
              <textarea
                placeholder="Reason for correction"
                value={correctionData.reason}
                onChange={(e) => setCorrectionData({...correctionData, reason: e.target.value})}
                className="textarea"
                rows={2}
              />
              <button 
                onClick={submitCorrection}
                disabled={loading}
                className="btn btn-warning"
              >
                {loading ? 'Processing...' : 'Submit Correction'}
              </button>
            </div>
          </div>
          
          {/* Fraud Detection */}
          <div className="phase3-card">
            <h3>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                <path d="M9 12h6"/>
              </svg>
              Fraud Detection
            </h3>
            <p>AI-powered pattern detection for suspicious activity</p>
            <div className="form-group">
              <input
                type="text"
                placeholder="Event ID to Scan"
                value={selectedEvent}
                onChange={(e) => setSelectedEvent(e.target.value)}
                className="input"
              />
              <button 
                onClick={runFraudDetection}
                disabled={loading}
                className="btn btn-alert"
              >
                {loading ? 'Scanning...' : 'Run Fraud Detection'}
              </button>
            </div>
          </div>
          
        </div>
      </div>

      {/* Audit History Display */}
      {auditHistory && (
        <div className="data-display audit-display">
          <h2>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
            </svg>
            Change History & Audit Trail
          </h2>
          
          <div className="audit-summary">
            <div className="summary-card">
              <span className="summary-value">{auditHistory.summary.total_changes}</span>
              <span className="summary-label">Total Changes</span>
            </div>
            <div className="summary-card">
              <span className="summary-value revocations">{auditHistory.summary.revocations}</span>
              <span className="summary-label">Revocations</span>
            </div>
            <div className="summary-card">
              <span className="summary-value invalidations">{auditHistory.summary.invalidations}</span>
              <span className="summary-label">Invalidations</span>
            </div>
            <div className="summary-card">
              <span className="summary-value corrections">{auditHistory.summary.corrections}</span>
              <span className="summary-label">Corrections</span>
            </div>
          </div>

          <div className="audit-timeline">
            {auditHistory.changes.map((change: any, i: number) => (
              <div key={i} className={`audit-item ${change.action_type}`}>
                <div className="audit-icon">
                  {change.action_type === 'revocation' && (
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <circle cx="12" cy="12" r="10"/>
                      <line x1="15" y1="9" x2="9" y2="15"/>
                      <line x1="9" y1="9" x2="15" y2="15"/>
                    </svg>
                  )}
                  {change.action_type === 'invalidation' && (
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                      <line x1="12" y1="9" x2="12" y2="13"/>
                      <line x1="12" y1="17" x2="12.01" y2="17"/>
                    </svg>
                  )}
                  {change.action_type === 'audit' && (
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <circle cx="12" cy="12" r="10"/>
                      <polyline points="12 6 12 12 16 14"/>
                    </svg>
                  )}
                </div>
                <div className="audit-content">
                  <div className="audit-header">
                    <strong>{change.action.replace('_', ' ').toUpperCase()}</strong>
                    <span className="audit-time">{new Date(change.timestamp).toLocaleString()}</span>
                  </div>
                  <p className="audit-performer">by {change.performed_by_name}</p>
                  {change.details.reason && (
                    <p className="audit-reason"><strong>Reason:</strong> {change.details.reason}</p>
                  )}
                  {change.old_state && change.new_state && (
                    <div className="state-comparison">
                      <div className="old-state">
                        <span className="state-label">Before:</span>
                        <code>{JSON.stringify(change.old_state, null, 2)}</code>
                      </div>
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <line x1="5" y1="12" x2="19" y2="12"/>
                        <polyline points="12 5 19 12 12 19"/>
                      </svg>
                      <div className="new-state">
                        <span className="state-label">After:</span>
                        <code>{JSON.stringify(change.new_state, null, 2)}</code>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Fraud Detection Report */}
      {fraudReport && (
        <div className="data-display fraud-display">
          <h2>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            </svg>
            Fraud Detection Report
          </h2>
          
          <div className="fraud-summary">
            <div className="summary-card alert-total">
              <span className="summary-value">{fraudReport.summary.total_alerts}</span>
              <span className="summary-label">Total Alerts</span>
            </div>
            <div className="summary-card alert-high">
              <span className="summary-value">{fraudReport.summary.high_severity}</span>
              <span className="summary-label">High Severity</span>
            </div>
            <div className="summary-card alert-medium">
              <span className="summary-value">{fraudReport.summary.medium_severity}</span>
              <span className="summary-label">Medium Severity</span>
            </div>
            <div className="summary-card alert-low">
              <span className="summary-value">{fraudReport.summary.low_severity}</span>
              <span className="summary-label">Low Severity</span>
            </div>
          </div>

          <div className="fraud-alerts">
            {fraudReport.fraud_alerts.map((alert: any, i: number) => (
              <div key={i} className={`fraud-alert severity-${alert.severity.toLowerCase()}`}>
                <div className="alert-header">
                  <div className="alert-badge">{alert.severity}</div>
                  <strong>{alert.type.replace(/_/g, ' ')}</strong>
                </div>
                <p className="alert-description">{alert.description}</p>
                <div className="alert-details">
                  <strong>Evidence:</strong>
                  <pre>{JSON.stringify(alert.evidence, null, 2)}</pre>
                </div>
                <p className="alert-recommendation">
                  <strong>Recommendation:</strong> {alert.recommendation}
                </p>
                {alert.student_prn !== 'N/A' && alert.student_prn !== 'MULTIPLE' && (
                  <p className="alert-student">
                    <strong>Student PRN:</strong> {alert.student_prn}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Transcript Data Display */}
      {transcriptData && (
        <div className="data-display">
          <h2>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
            </svg>
            Participation Transcript
          </h2>
          <div className="stats-grid">
            <div className="stat-box">
              <span className="stat-value">{transcriptData.statistics.total_registered}</span>
              <span className="stat-label">Registered</span>
            </div>
            <div className="stat-box">
              <span className="stat-value">{transcriptData.statistics.total_attended}</span>
              <span className="stat-label">Attended</span>
            </div>
            <div className="stat-box">
              <span className="stat-value">{transcriptData.statistics.total_certified}</span>
              <span className="stat-label">Certified</span>
            </div>
            <div className="stat-box">
              <span className="stat-value">{transcriptData.statistics.attendance_rate}%</span>
              <span className="stat-label">Attendance Rate</span>
            </div>
          </div>
          
          <div className="table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Event</th>
                  <th>Date</th>
                  <th>Registered</th>
                  <th>Attended</th>
                  <th>Certified</th>
                  <th>Roles</th>
                </tr>
              </thead>
              <tbody>
                {transcriptData.participations.map((p: any, i: number) => (
                  <tr key={i}>
                    <td>{p.event_name}</td>
                    <td>{new Date(p.event_date).toLocaleDateString()}</td>
                    <td className={p.registered ? 'success' : 'fail'}>{p.registered ? '✓' : '✗'}</td>
                    <td className={p.attended ? 'success' : 'fail'}>{p.attended ? '✓' : '✗'}</td>
                    <td className={p.certified ? 'success' : 'fail'}>{p.certified ? '✓' : '✗'}</td>
                    <td>{p.roles.join(', ') || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
      
      {/* Snapshots Display */}
      {snapshotData.length > 0 && (
        <div className="data-display">
          <h2>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 3h18v18H3z"/>
              <path d="m3 9 9-7 9 7"/>
            </svg>
            Student Profile Timeline
          </h2>
          <p className="snapshot-count">Total snapshots captured: {snapshotData.length}</p>
          <div className="snapshots-list">
            {snapshotData.map((snapshot, i) => (
              <div key={i} className="snapshot-card">
                <div className="snapshot-header">
                  <div className="snapshot-id">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <circle cx="12" cy="12" r="10"/>
                      <polyline points="12 6 12 12 16 14"/>
                    </svg>
                    Snapshot #{snapshot.id}
                  </div>
                  <span className="snapshot-date">
                    {new Date(snapshot.captured_at).toLocaleString()}
                  </span>
                </div>
                <div className="snapshot-body">
                  <div className="snapshot-info">
                    <span><strong>Event:</strong> {snapshot.event_id}</span>
                    <span><strong>Trigger:</strong> {snapshot.trigger}</span>
                  </div>
                  {snapshot.profile_data && (
                    <div className="profile-data">
                      <p><strong>Name:</strong> {snapshot.profile_data.name || 'N/A'}</p>
                      <p><strong>Email:</strong> {snapshot.profile_data.email || 'N/A'}</p>
                      <p><strong>Branch:</strong> {snapshot.profile_data.branch || 'N/A'}</p>
                      <p><strong>Year:</strong> {snapshot.profile_data.year || 'N/A'}</p>
                    </div>
                  )}
                  {snapshot.participation_status && (
                    <div className="participation-stats">
                      <span>📊 {snapshot.participation_status.total_events || 0} Events</span>
                      <span>✓ {snapshot.participation_status.attended_events || 0} Attended</span>
                      <span>🏆 {snapshot.participation_status.certificates_earned || 0} Certificates</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* API Documentation Links */}
      <div className="api-docs-section">
        <h2>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
            <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
          </svg>
          Complete API Reference
        </h2>
        <div className="api-grid">
          <a href="http://localhost:8000/docs#/PS1%20-%20Participation%20Intelligence" target="_blank" className="api-card">
            <strong>PS1 Endpoints</strong>
            <span>21 comprehensive APIs</span>
          </a>
          <a href="/conflicts" className="api-card">
            <strong>Conflict Dashboard</strong>
            <span>Visual reconciliation</span>
          </a>
          <a href="/verify" target="_blank" className="api-card">
            <strong>Public Verification</strong>
            <span>Certificate validation</span>
          </a>
          <a href="/students" className="api-card">
            <strong>Student Management</strong>
            <span>Profile administration</span>
          </a>
        </div>
      </div>
    </div>
  );
}
