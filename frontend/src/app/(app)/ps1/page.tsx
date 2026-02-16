"use client";

import { useState, useEffect } from 'react';
import { getAuth, getUser } from '@/lib/auth';
import api, { checkBackendHealth } from '@/services/api';
import Modal from '@/components/Modal/Modal';
import HelpGuide from '@/components/HelpGuide/HelpGuide';
import { getHelpContent } from '@/components/HelpGuide/helpGuideConfig';
import './ps1.scss';

export default function CortexCorePage() {
  // State Management
  const [loading, setLoading] = useState(false);
  const [userEmail, setUserEmail] = useState<string | null>(null);
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);

  // Input States
  const [studentPRN, setStudentPRN] = useState('');
  const [eventID, setEventID] = useState('');
  const [certificateID, setCertificateID] = useState('');

  // Modal States
  const [activeModal, setActiveModal] = useState<string | null>(null);
  const [modalContent, setModalContent] = useState<any>(null);

  // Help Guide
  const cortexCoreHelp = getHelpContent('cortex-core');

  useEffect(() => {
    const user = getUser();
    if (user) {
      setUserEmail(user.email);
    }
    
    // Check backend health
    checkBackendHealth().then(setBackendOnline);

    // Cleanup function to ensure body overflow is restored on unmount
    return () => {
      document.body.style.overflow = '';
    };
  }, []);

  const closeModal = () => {
    setActiveModal(null);
    setModalContent(null);
    // Ensure body overflow is restored
    document.body.style.overflow = '';
  };
  
  const retryBackendConnection = async () => {
    setBackendOnline(null);
    const isOnline = await checkBackendHealth();
    setBackendOnline(isOnline);
  };

  // 1. Conflict Detection
  const openConflictDashboard = () => {
    window.open('/conflicts', '_blank');
  };

  // 2. Student Snapshots
  const fetchSnapshots = async () => {
    if (!studentPRN) {
      alert('Please enter a student PRN');
      return;
    }

    setLoading(true);
    try {
      const token = getAuth();
      if (!token) {
        alert('⚠️ Please login first');
        setLoading(false);
        return;
      }

      const data = await api.get(`/ps1/snapshots/student/${studentPRN}`);
      setModalContent(data);
      setActiveModal('snapshots');
    } catch (error: any) {
      console.error('Error:', error);
      alert(`Failed to fetch snapshots: ${error.message || 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  // 3. Certificate Verification
  const verifyCertificate = () => {
    if (certificateID) {
      window.open(`/verify?cert=${certificateID}`, '_blank');
    } else {
      window.open('/verify', '_blank');
    }
  };

  // 4. Audit Trail
  const fetchAuditTrail = async () => {
    if (!eventID || !studentPRN) {
      alert('Please enter both Event ID and Student PRN');
      return;
    }

    setLoading(true);
    try {
      const token = getAuth();
      if (!token) {
        alert('⚠️ Please login first');
        setLoading(false);
        return;
      }

      const data = await api.get(`/ps1/audit/${eventID}/${studentPRN}`);
      setModalContent(data);
      setActiveModal('audit');
    } catch (error: any) {
      console.error('Error:', error);
      alert(`Failed to fetch audit trail: ${error.message || 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  // 5. Multi-Role Engine
  const fetchStudentRoles = async () => {
    if (!studentPRN) {
      alert('Please enter a student PRN');
      return;
    }

    setLoading(true);
    try {
      const token = getAuth();
      if (!token) {
        alert('⚠️ Please login first');
        setLoading(false);
        return;
      }

      // Fetch transcript which contains role information
      const data = await api.get(`/ps1/transcript/${studentPRN}`);
      
      // Validate response structure
      if (!data || typeof data !== 'object') {
        throw new Error('Invalid response from server');
      }
      
      // Ensure statistics exists
      if (!data.statistics) {
        data.statistics = {
          total_registered: 0,
          total_attended: 0,
          total_certified: 0,
          attendance_rate: 0,
          unique_roles: [],
          total_roles: 0
        };
      }
      
      // Ensure participations exists
      if (!data.participations) {
        data.participations = [];
      }
      
      setModalContent(data);
      setActiveModal('roles');
    } catch (error: any) {
      console.error('Error:', error);
      alert(`Failed to fetch roles: ${error.message || 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  // 6. Transcript Generator
  const fetchTranscript = async (format: 'json' | 'pdf') => {
    if (!studentPRN) {
      alert('Please enter a student PRN');
      return;
    }

    setLoading(true);
    try {
      const token = getAuth();
      if (!token) {
        alert('⚠️ Please login first');
        setLoading(false);
        return;
      }

      if (format === 'json') {
        const data = await api.get(`/ps1/transcript/${studentPRN}`);
        
        // Validate response structure
        if (!data || typeof data !== 'object') {
          throw new Error('Invalid response from server');
        }
        
        // Ensure statistics exists
        if (!data.statistics) {
          data.statistics = {
            total_registered: 0,
            total_attended: 0,
            total_certified: 0,
            attendance_rate: 0,
            unique_roles: [],
            total_roles: 0
          };
        }
        
        // Ensure participations exists
        if (!data.participations) {
          data.participations = [];
        }
        
        setModalContent(data);
        setActiveModal('transcript');
      } else {
        const response = await fetch(`/api/ps1/transcript/${studentPRN}/pdf`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(errorText || 'Failed to download PDF');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `transcript_${studentPRN}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        alert('✅ PDF downloaded successfully!');
      }
    } catch (error: any) {
      console.error('Error:', error);
      alert(`Failed to fetch transcript: ${error.message || 'Unknown error'}`);
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
      </div>

      {/* Backend Status Banner */}
      {backendOnline === false && (
        <div className="backend-offline-banner">
          <div className="banner-content">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8" x2="12" y2="12"/>
              <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            <div className="banner-text">
              <strong>Backend Server Offline</strong>
              <p>Unable to connect to the backend. Please start the backend server.</p>
            </div>
            <button onClick={retryBackendConnection} className="btn-retry-small">
              Retry
            </button>
          </div>
        </div>
      )}

      {/* Feature Cards Grid */}
      <div className="feature-grid-uniform">
        
        {/* 1. Conflict Detection */}
        <div className="feature-card-uniform">
          <div className="feature-icon-uniform">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="8"/>
              <path d="m21 21-4.35-4.35"/>
            </svg>
          </div>
          <h2>Conflict Detection</h2>
          <p>Participation reconciliation with trust scoring</p>
          <div className="input-section">
            <button 
              onClick={openConflictDashboard}
              className="btn-uniform"
            >
              Open Dashboard
            </button>
          </div>
        </div>

        {/* 2. Student Snapshots */}
        <div className="feature-card-uniform">
          <div className="feature-icon-uniform">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 3h18v18H3z"/>
              <path d="m3 9 9-7 9 7"/>
            </svg>
          </div>
          <h2>Student Snapshots</h2>
          <p>Historical profile tracking with temporal queries</p>
          <div className="input-section">
            <input
              type="text"
              placeholder="Student PRN"
              value={studentPRN}
              onChange={(e) => setStudentPRN(e.target.value.toUpperCase())}
              className="input-uniform"
            />
            <button 
              onClick={fetchSnapshots}
              disabled={loading}
              className="btn-uniform"
            >
              {loading ? 'Loading...' : 'View History'}
            </button>
          </div>
        </div>

        {/* 3. Certificate System */}
        <div className="feature-card-uniform">
          <div className="feature-icon-uniform">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
              <polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
          </div>
          <h2>Certificate System</h2>
          <p>SHA-256 verification + fraud detection</p>
          <div className="input-section">
            <input
              type="text"
              placeholder="Certificate ID"
              value={certificateID}
              onChange={(e) => setCertificateID(e.target.value)}
              className="input-uniform"
            />
            <button 
              onClick={verifyCertificate}
              className="btn-uniform"
            >
              Verify
            </button>
          </div>
        </div>

        {/* 4. Audit Trail */}
        <div className="feature-card-uniform">
          <div className="feature-icon-uniform">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="1 4 1 10 7 10"/>
              <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/>
            </svg>
          </div>
          <h2>Audit Trail</h2>
          <p>Change history, revocations, invalidations</p>
          <div className="input-section">
            <input
              type="text"
              placeholder="Event ID"
              value={eventID}
              onChange={(e) => setEventID(e.target.value)}
              className="input-uniform"
            />
            <input
              type="text"
              placeholder="Student PRN"
              value={studentPRN}
              onChange={(e) => setStudentPRN(e.target.value.toUpperCase())}
              className="input-uniform"
            />
            <button 
              onClick={fetchAuditTrail}
              disabled={loading}
              className="btn-uniform"
            >
              {loading ? 'Loading...' : 'View Audit'}
            </button>
          </div>
        </div>

        {/* 5. Multi-Role Engine */}
        <div className="feature-card-uniform">
          <div className="feature-icon-uniform">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M17 21v-2a4 4 0 0 0-4-4 H5a4 4 0 0 0-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
            </svg>
          </div>
          <h2>Multi-Role Engine</h2>
          <p>Track multiple roles per student across events</p>
          <div className="input-section">
            <input
              type="text"
              placeholder="Student PRN"
              value={studentPRN}
              onChange={(e) => setStudentPRN(e.target.value.toUpperCase())}
              className="input-uniform"
            />
            <button 
              onClick={fetchStudentRoles}
              disabled={loading}
              className="btn-uniform"
            >
              {loading ? 'Loading...' : 'View Roles'}
            </button>
          </div>
        </div>

        {/* 6. Transcript Generator */}
        <div className="feature-card-uniform">
          <div className="feature-icon-uniform">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
            </svg>
          </div>
          <h2>Transcript Generator</h2>
          <p>JSON & PDF participation transcripts</p>
          <div className="input-section">
            <input
              type="text"
              placeholder="Student PRN"
              value={studentPRN}
              onChange={(e) => setStudentPRN(e.target.value.toUpperCase())}
              className="input-uniform"
            />
            <div className="button-row">
              <button 
                onClick={() => fetchTranscript('json')}
                disabled={loading}
                className="btn-uniform"
              >
                View JSON
              </button>
              <button 
                onClick={() => fetchTranscript('pdf')}
                disabled={loading}
                className="btn-uniform-outline"
              >
                Download PDF
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Modal: Snapshots */}
      <Modal
        isOpen={activeModal === 'snapshots'}
        onClose={closeModal}
        title="Student Profile Snapshots"
        size="large"
      >
        {modalContent && Array.isArray(modalContent) && (
          <>
            {modalContent.length === 0 ? (
              <div className="empty-state">
                <p>📄 No snapshots found for this student. Snapshots are captured during event participation.</p>
              </div>
            ) : (
              <>
                <p className="snapshot-count">Total snapshots: {modalContent.length}</p>
                <div className="snapshots-list">
                  {modalContent.map((snapshot: any, i: number) => (
                    <div key={i} className="snapshot-item">
                      <div className="snapshot-header">
                        <span className="snapshot-id">Snapshot #{snapshot.id}</span>
                        <span className="snapshot-date">
                          {new Date(snapshot.captured_at).toLocaleString()}
                        </span>
                      </div>
                      <div className="snapshot-details">
                        <p><strong>Event:</strong> {snapshot.event_id}</p>
                        <p><strong>Trigger:</strong> {snapshot.trigger}</p>
                        {snapshot.profile_data && (
                          <div className="profile-info">
                            <p><strong>Name:</strong> {snapshot.profile_data.name || 'N/A'}</p>
                            <p><strong>Email:</strong> {snapshot.profile_data.email || 'N/A'}</p>
                            <p><strong>Branch:</strong> {snapshot.profile_data.branch || 'N/A'}</p>
                            <p><strong>Year:</strong> {snapshot.profile_data.year || 'N/A'}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </>
            )}
          </>
        )}
      </Modal>

      {/* Modal: Audit Trail */}
      <Modal
        isOpen={activeModal === 'audit'}
        onClose={closeModal}
        title="Audit Trail & Change History"
        size="large"
      >
        {modalContent && (
          <>
            <div className="audit-summary">
              <div className="stat-item">
                <span className="stat-value">{modalContent.summary?.total_changes || 0}</span>
                <span className="stat-label">Total Changes</span>
              </div>
              <div className="stat-item">
                <span className="stat-value">{modalContent.summary?.revocations || 0}</span>
                <span className="stat-label">Revocations</span>
              </div>
              <div className="stat-item">
                <span className="stat-value">{modalContent.summary?.invalidations || 0}</span>
                <span className="stat-label">Invalidations</span>
              </div>
              <div className="stat-item">
                <span className="stat-value">{modalContent.summary?.corrections || 0}</span>
                <span className="stat-label">Corrections</span>
              </div>
            </div>

            {modalContent.changes && modalContent.changes.length > 0 ? (
              <div className="audit-timeline">
                {modalContent.changes.map((change: any, i: number) => (
                  <div key={i} className="audit-item">
                    <div className="audit-header">
                      <strong>{change.action}</strong>
                      <span className="audit-time">
                        {new Date(change.timestamp).toLocaleString()}
                      </span>
                    </div>
                    <p className="audit-user">by {change.performed_by_name}</p>
                    {change.details?.reason && (
                      <p className="audit-reason"><strong>Reason:</strong> {change.details.reason}</p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="empty-state">No audit history found for this student in the specified event.</p>
            )}
          </>
        )}
      </Modal>

      {/* Modal: Multi-Role Engine */}
      <Modal
        isOpen={activeModal === 'roles'}
        onClose={closeModal}
        title="Multi-Role Participation Analysis"
        size="large"
      >
        {modalContent && modalContent.participations && modalContent.statistics ? (
          <>
            <div className="roles-summary">
              <h4>Participation Statistics</h4>
              <div className="stats-grid">
                <div className="stat-box">
                  <span className="stat-value">{modalContent.statistics?.total_registered ?? 0}</span>
                  <span className="stat-label">Events Registered</span>
                </div>
                <div className="stat-box">
                  <span className="stat-value">{modalContent.statistics?.total_attended ?? 0}</span>
                  <span className="stat-label">Events Attended</span>
                </div>
                <div className="stat-box">
                  <span className="stat-value">{modalContent.statistics?.total_certified ?? 0}</span>
                  <span className="stat-label">Certificates Earned</span>
                </div>
              </div>
            </div>

            <div className="roles-breakdown">
              <h4>Role Breakdown by Event</h4>
              <div className="table-wrapper">
                <table className="role-table">
                  <thead>
                    <tr>
                      <th>Event</th>
                      <th>Date</th>
                      <th>Roles</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {modalContent.participations.map((p: any, i: number) => (
                      <tr key={i}>
                        <td>{p.event_name || 'Unknown Event'}</td>
                        <td>{p.event_date ? new Date(p.event_date).toLocaleDateString() : 'N/A'}</td>
                        <td>
                          <div className="role-tags">
                            {p.roles && p.roles.length > 0 ? (
                              p.roles.map((role: string, idx: number) => (
                                <span key={idx} className={`role-tag role-${role.toLowerCase()}`}>
                                  {role}
                                </span>
                              ))
                            ) : (
                              <span className="role-tag role-participant">PARTICIPANT</span>
                            )}
                          </div>
                        </td>
                        <td>
                          <div className="status-indicators">
                            {p.attended && <span className="status-badge success">✓ Attended</span>}
                            {p.certified && <span className="status-badge certified">🏆 Certified</span>}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="roles-legend">
              <h4>Available Roles</h4>
              <div className="legend-grid">
                <span className="legend-item"><span className="legend-dot participant"></span> PARTICIPANT</span>
                <span className="legend-item"><span className="legend-dot volunteer"></span> VOLUNTEER</span>
                <span className="legend-item"><span className="legend-dot speaker"></span> SPEAKER</span>
                <span className="legend-item"><span className="legend-dot organizer"></span> ORGANIZER</span>
                <span className="legend-item"><span className="legend-dot judge"></span> JUDGE</span>
                <span className="legend-item"><span className="legend-dot mentor"></span> MENTOR</span>
              </div>
            </div>
          </>
        ) : (
          <div className="error-state">
            <p>⚠️ Unable to load role data. Please ensure the student has valid participation records.</p>
          </div>
        )}
      </Modal>

      {/* Modal: Transcript */}
      <Modal
        isOpen={activeModal === 'transcript'}
        onClose={closeModal}
        title="Participation Transcript"
        size="large"
      >
        {modalContent ? (
          modalContent.statistics && modalContent.participations ? (
            <>
              <div className="transcript-stats">
                <div className="stat-box">
                  <span className="stat-value">{modalContent.statistics?.total_registered ?? 0}</span>
                  <span className="stat-label">Registered</span>
                </div>
                <div className="stat-box">
                  <span className="stat-value">{modalContent.statistics?.total_attended ?? 0}</span>
                  <span className="stat-label">Attended</span>
                </div>
                <div className="stat-box">
                  <span className="stat-value">{modalContent.statistics?.total_certified ?? 0}</span>
                  <span className="stat-label">Certified</span>
                </div>
                <div className="stat-box">
                  <span className="stat-value">{modalContent.statistics?.attendance_rate ?? 0}%</span>
                  <span className="stat-label">Attendance Rate</span>
                </div>
              </div>

              {modalContent.participations && modalContent.participations.length > 0 ? (
                <div className="transcript-table">
                  <table>
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
                      {modalContent.participations.map((p: any, i: number) => (
                        <tr key={i}>
                          <td>{p.event_name || 'Unknown Event'}</td>
                          <td>{p.event_date ? new Date(p.event_date).toLocaleDateString() : 'N/A'}</td>
                          <td className={p.registered ? 'success' : 'fail'}>
                            {p.registered ? '✓' : '✗'}
                          </td>
                          <td className={p.attended ? 'success' : 'fail'}>
                            {p.attended ? '✓' : '✗'}
                          </td>
                          <td className={p.certified ? 'success' : 'fail'}>
                            {p.certified ? '✓' : '✗'}
                          </td>
                          <td>{p.roles?.join(', ') || 'PARTICIPANT'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="empty-state">No participation records found for this student.</p>
              )}

              <div className="json-preview">
                <h4>JSON Data Preview</h4>
                <pre>{JSON.stringify(modalContent, null, 2)}</pre>
              </div>
            </>
          ) : (
            <div className="error-state">
              <p>⚠️ Unable to load transcript data. Please try again.</p>
              {modalContent && <pre>{JSON.stringify(modalContent, null, 2)}</pre>}
            </div>
          )
        ) : (
          <div className="loading-state">
            <p>Loading transcript data...</p>
          </div>
        )}
      </Modal>

      {/* Help Guide */}
      {cortexCoreHelp && <HelpGuide content={cortexCoreHelp} />}
    </div>
  );
}
