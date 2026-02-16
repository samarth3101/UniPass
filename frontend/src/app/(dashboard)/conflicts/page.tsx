"use client";

import { useState, useEffect } from 'react';
import './conflicts.scss';

interface Conflict {
  type: string;
  severity: string;
  message: string;
  field?: string;
}

interface ConflictStudent {
  student_prn: string;
  canonical_status: string;
  conflicts: Conflict[];
  trust_score: number;
}

export default function ConflictDashboard() {
  const [events, setEvents] = useState<any[]>([]);
  const [selectedEvent, setSelectedEvent] = useState<number | null>(null);
  const [conflicts, setConflicts] = useState<ConflictStudent[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingEvents, setLoadingEvents] = useState(true);
  const [eventsError, setEventsError] = useState<string | null>(null);
  const [filter, setFilter] = useState<string>('all');
  const [fraudData, setFraudData] = useState<any>(null);
  const [loadingFraud, setLoadingFraud] = useState(false);
  
  // Fetch events on mount
  useEffect(() => {
    fetchEvents();
  }, []);
  
  const fetchEvents = async () => {
    setLoadingEvents(true);
    setEventsError(null);
    
    try {
      const token = localStorage.getItem('unipass_token');
      
      if (!token) {
        setEventsError('Please log in to view events');
        setLoadingEvents(false);
        return;
      }
      
      const response = await fetch('http://localhost:8000/events/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to fetch events: ${response.status} - ${errorText}`);
      }
      
      const data = await response.json();
      console.log('Events fetched:', data);
      
      // Handle different response formats
      let eventsList = [];
      if (Array.isArray(data)) {
        eventsList = data;
      } else if (data.items && Array.isArray(data.items)) {
        eventsList = data.items;
      } else if (data.events && Array.isArray(data.events)) {
        eventsList = data.events;
      }
      
      setEvents(eventsList);
      
      if (eventsList.length === 0) {
        setEventsError('No events found. Please create an event first.');
      }
    } catch (error: any) {
      console.error('Error fetching events:', error);
      setEventsError(error.message || 'Failed to load events. Please check your connection and try again.');
    } finally {
      setLoadingEvents(false);
    }
  };
  
  const fetchConflicts = async (eventId: number) => {
    setLoading(true);
    setConflicts([]);
    
    try {
      const token = localStorage.getItem('unipass_token');
      
      if (!token) {
        alert('Please log in to view conflicts');
        setLoading(false);
        return;
      }
      
      const response = await fetch(`http://localhost:8000/ps1/participation/conflicts/${eventId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to fetch conflicts: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Conflicts fetched:', data);
      setConflicts(Array.isArray(data) ? data : []);
    } catch (error: any) {
      console.error('Error fetching conflicts:', error);
      alert(`Failed to load conflicts: ${error.message}`);
      setConflicts([]);
    } finally {
      setLoading(false);
    }
  };
  
  const runFraudDetection = async () => {
    if (!selectedEvent) return;
    
    setLoadingFraud(true);
    setFraudData(null);
    
    try {
      const token = localStorage.getItem('unipass_token');
      
      if (!token) {
        alert('Please log in to run fraud detection');
        setLoadingFraud(false);
        return;
      }
      
      const response = await fetch(`http://localhost:8000/ps1/fraud/detect/${selectedEvent}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to run fraud detection: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Fraud detection results:', data);
      setFraudData(data);
    } catch (error: any) {
      console.error('Error running fraud detection:', error);
      alert(`Failed to run fraud detection: ${error.message}`);
    } finally {
      setLoadingFraud(false);
    }
  };
  
  const handleEventChange = (eventId: number) => {
    setSelectedEvent(eventId);
    fetchConflicts(eventId);
  };
  
  const getSeverityColor = (severity: string) => {
    switch (severity.toUpperCase()) {
      case 'HIGH': return 'severity-high';
      case 'MEDIUM': return 'severity-medium';
      case 'LOW': return 'severity-low';
      default: return '';
    }
  };
  
  const getTrustScoreColor = (score: number) => {
    if (score >= 80) return 'trust-high';
    if (score >= 50) return 'trust-medium';
    return 'trust-low';
  };
  
  const filteredConflicts = conflicts.filter(item => {
    if (filter === 'all') return true;
    return item.conflicts.some(c => c.severity.toUpperCase() === filter.toUpperCase());
  });
  
  const conflictStats = {
    total: conflicts.length,
    high: conflicts.filter(c => c.conflicts.some(conf => conf.severity === 'HIGH')).length,
    medium: conflicts.filter(c => c.conflicts.some(conf => conf.severity === 'MEDIUM')).length,
    low: conflicts.filter(c => c.conflicts.some(conf => conf.severity === 'LOW')).length,
  };
  
  return (
    <div className="conflict-dashboard">
      <div className="dashboard-header">
        <h1>Participation Conflict Dashboard</h1>
        <p>Identify and resolve data inconsistencies across registrations, attendance, and certificates</p>
      </div>
      
      <div className="event-selector">
        <label htmlFor="event-select">Select Event:</label>
        {loadingEvents ? (
          <div className="loading-events">
            <div className="spinner"></div>
            <span>Loading events...</span>
          </div>
        ) : eventsError ? (
          <div className="error-message">
            <span>⚠️ {eventsError}</span>
            <button onClick={fetchEvents} className="btn-retry">Retry</button>
          </div>
        ) : (
          <select 
            id="event-select"
            value={selectedEvent || ''}
            onChange={(e) => handleEventChange(Number(e.target.value))}
            disabled={events.length === 0}
          >
            <option value="">
              {events.length === 0 ? 'No events available' : 'Choose an event...'}
            </option>
            {events.map(event => (
              <option key={event.id} value={event.id}>
                {event.title} - {event.start_time ? new Date(event.start_time).toLocaleDateString() : event.start_date ? new Date(event.start_date).toLocaleDateString() : 'Date N/A'}
              </option>
            ))}
          </select>
        )}
      </div>
      
      {selectedEvent && (
        <>
          <div className="conflict-stats">
            <div className="stat-card">
              <span className="stat-number">{conflictStats.total}</span>
              <span className="stat-label">Total Conflicts</span>
            </div>
            <div className="stat-card high">
              <span className="stat-number">{conflictStats.high}</span>
              <span className="stat-label">High Severity</span>
            </div>
            <div className="stat-card medium">
              <span className="stat-number">{conflictStats.medium}</span>
              <span className="stat-label">Medium Severity</span>
            </div>
            <div className="stat-card low">
              <span className="stat-number">{conflictStats.low}</span>
              <span className="stat-label">Low Severity</span>
            </div>
          </div>
          
          {/* Fraud Detection Section */}
          <div className="fraud-detection-section">
            <div className="fraud-header">
              <div>
                <h2>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                  </svg>
                  Fraud Detection
                </h2>
                <p>Scan for suspicious patterns and potential fraud</p>
              </div>
              <button 
                onClick={runFraudDetection}
                disabled={loadingFraud}
                className="btn btn-fraud-scan"
              >
                {loadingFraud ? 'Scanning...' : 'Run Fraud Scan'}
              </button>
            </div>
            
            {fraudData && (
              <div className="fraud-results">
                <div className="fraud-summary">
                  <div className="fraud-stat total">
                    <span className="number">{fraudData.summary.total_alerts}</span>
                    <span className="label">Total Alerts</span>
                  </div>
                  <div className="fraud-stat high">
                    <span className="number">{fraudData.summary.high_severity}</span>
                    <span className="label">High Priority</span>
                  </div>
                  <div className="fraud-stat medium">
                    <span className="number">{fraudData.summary.medium_severity}</span>
                    <span className="label">Medium Priority</span>
                  </div>
                  <div className="fraud-stat low">
                    <span className="number">{fraudData.summary.low_severity}</span>
                    <span className="label">Low Priority</span>
                  </div>
                </div>
                
                {fraudData.fraud_alerts.length > 0 && (
                  <div className="fraud-alerts">
                    {fraudData.fraud_alerts.map((alert: any, idx: number) => (
                      <div key={idx} className={`fraud-alert ${alert.severity.toLowerCase()}`}>
                        <div className="alert-icon">
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                            <line x1="12" y1="9" x2="12" y2="13"/>
                            <line x1="12" y1="17" x2="12.01" y2="17"/>
                          </svg>
                        </div>
                        <div className="alert-content">
                          <div className="alert-header">
                            <span className="severity-badge">{alert.severity}</span>
                            <strong>{alert.type.replace(/_/g, ' ')}</strong>
                          </div>
                          <p>{alert.description}</p>
                          <div className="alert-recommendation">
                            <strong>Action:</strong> {alert.recommendation}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
          
          <div className="filter-bar">
            <button 
              className={filter === 'all' ? 'active' : ''}
              onClick={() => setFilter('all')}
            >
              All ({conflicts.length})
            </button>
            <button 
              className={filter === 'high' ? 'active severity-high' : 'severity-high'}
              onClick={() => setFilter('high')}
            >
              High ({conflictStats.high})
            </button>
            <button 
              className={filter === 'medium' ? 'active severity-medium' : 'severity-medium'}
              onClick={() => setFilter('medium')}
            >
              Medium ({conflictStats.medium})
            </button>
            <button 
              className={filter === 'low' ? 'active severity-low' : 'severity-low'}
              onClick={() => setFilter('low')}
            >
              Low ({conflictStats.low})
            </button>
          </div>
          
          {loading ? (
            <div className="loading">Loading conflicts...</div>
          ) : filteredConflicts.length === 0 ? (
            <div className="no-conflicts">
              <div className="success-icon">✓</div>
              <h2>No Conflicts Found!</h2>
              <p>All participation data is consistent for this event.</p>
            </div>
          ) : (
            <div className="conflicts-list">
              {filteredConflicts.map((item, index) => (
                <div key={index} className="conflict-card">
                  <div className="conflict-header">
                    <div className="student-info">
                      <h3>{item.student_prn}</h3>
                      <span className="status-badge">{item.canonical_status}</span>
                    </div>
                    <div className={`trust-score ${getTrustScoreColor(item.trust_score)}`}>
                      <span className="score-value">{item.trust_score}</span>
                      <span className="score-label">Trust Score</span>
                    </div>
                  </div>
                  
                  <div className="conflicts">
                    {item.conflicts.map((conflict, cIndex) => (
                      <div key={cIndex} className={`conflict-item ${getSeverityColor(conflict.severity)}`}>
                        <div className="conflict-badge">{conflict.severity}</div>
                        <div className="conflict-details">
                          <strong>{conflict.type.replace(/_/g, ' ')}</strong>
                          <p>{conflict.message}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                  
                  <div className="conflict-actions">
                    <button className="btn btn-view">View Details</button>
                    <button className="btn btn-fix">Fix Attendance</button>
                    <button className="btn btn-revoke">Revoke Certificate</button>
                    <button className="btn btn-resolve">Mark Resolved</button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
