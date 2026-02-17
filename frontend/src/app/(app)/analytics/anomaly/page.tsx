"use client";

import { useState, useEffect } from "react";
import "./anomaly.scss";
import api from "@/services/api";
import HelpGuide, { getHelpContent } from "@/components/HelpGuide";

interface Anomaly {
  attendance_id: number;
  event_id: number;
  student_prn: string;
  scanned_at: string;
  anomaly_score: number;
  severity: "HIGH" | "MEDIUM";
  scan_source: string;
  features: Record<string, number>;
  explanation: string;
}

interface AnomalySummary {
  is_trained: boolean;
  total_checked: number;
  total_anomalies: number;
  anomaly_rate: number;
  by_severity: {
    high: number;
    medium: number;
  };
  by_source: {
    admin_override: number;
    qr_scan: number;
    other: number;
  };
  requires_review: number;
}

interface ModelStatus {
  is_trained: boolean;
  model_type: string;
  contamination_rate: number;
  n_estimators: number;
  status: string;
  message: string;
  training_info?: {
    trained_at: string;
    samples_used: number;
    features: string[];
    feature_count: number;
    anomalies_detected: number;
    anomaly_rate: number;
    feature_importance: Record<string, number>;
    score_distribution: {
      mean: number;
      std: number;
      min: number;
      max: number;
    };
    model_version: string;
  };
  model_health?: string;
}

interface ModelMetrics {
  model_metadata: any;
  current_detections: {
    total: number;
    by_severity: { HIGH: number; MEDIUM: number };
    avg_score: number;
    min_score: number;
    max_score: number;
  };
  feature_importance: Record<string, number>;
  time_distribution: Record<string, number>;
  model_confidence: string;
  last_trained: string;
}

export default function AnomalyDetectionPage() {
  const helpContent = getHelpContent('anomaly-detection');
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [summary, setSummary] = useState<AnomalySummary | null>(null);
  const [modelStatus, setModelStatus] = useState<ModelStatus>({
    is_trained: false,
    model_type: 'Isolation Forest',
    contamination_rate: 0.05,
    n_estimators: 100,
    status: 'requires_training',
    message: 'Model needs training. Click Train Model button below to start.'
  });
  const [loading, setLoading] = useState(false);
  const [training, setTraining] = useState(false);
  const [selectedAnomaly, setSelectedAnomaly] = useState<Anomaly | null>(null);
  const [eventFilter, setEventFilter] = useState<string>("");
  const [modelMetrics, setModelMetrics] = useState<ModelMetrics | null>(null);
  const [showMetrics, setShowMetrics] = useState(false);
  const [modalData, setModalData] = useState<{ show: boolean; type: 'success' | 'error'; title: string; message?: string; data?: any }>({ show: false, type: 'success', title: '' });

  useEffect(() => {
    checkModelStatus();
    loadSummary();
  }, []);

  const checkModelStatus = async () => {
    try {
      const response = await api.get("/analytics/anomaly/status");
      if (response) {
        setModelStatus(response);
        // Only load metrics if model is trained
        if (response.is_trained && response.training_info) {
          loadModelMetrics();
        }
        console.log("✅ Model status loaded:", response);
      }
    } catch (error: any) {
      console.error("⚠️ Failed to load model status - using default:", error.message);
    }
  };

  const loadModelMetrics = async () => {
    try {
      const response = await api.get("/analytics/anomaly/metrics");
      setModelMetrics(response);
      console.log("✅ Model metrics loaded:", response);
    } catch (error: any) {
      console.error("⚠️ Failed to load model metrics:", error.message);
      // Non-critical error, metrics are optional
    }
  };

  const loadSummary = async () => {
    try {
      const response = await api.get("/analytics/anomaly/summary");
      setSummary(response);
    } catch (error: any) {
      console.error("Failed to load summary:", error);
      if (error.message?.includes('400')) {
        // Model not trained yet
        setSummary(null);
      }
    }
  };

  const trainModel = async () => {
    setTraining(true);
    try {
      const response = await api.post("/analytics/anomaly/train");
      
      setModalData({ 
        show: true, 
        type: 'success', 
        title: 'Model Trained Successfully!',
        data: {
          trainingMetrics: {
            samplesAnalyzed: response.samples_used.toLocaleString(),
            featuresExtracted: response.feature_count,
            anomaliesFound: response.anomalies_in_training,
            detectionRate: response.anomaly_rate.toFixed(2)
          },
          modelPerformance: {
            confidence: response.performance_metrics?.confidence || 'GOOD',
            scoreMean: response.performance_metrics?.score_mean?.toFixed(3) || 'N/A'
          }
        }
      });
      
      await checkModelStatus();
      await loadSummary();
      await loadModelMetrics();
    } catch (error: any) {
      console.error("Training failed:", error);
      setModalData({ 
        show: true, 
        type: 'error', 
        title: 'Training Failed', 
        message: error.message || "Failed to train model. Check console for details." 
      });
    }
    setTraining(false);
  };

  const detectAnomalies = async () => {
    setLoading(true);
    try {
      const url = eventFilter
        ? `/analytics/anomaly/detect?event_id=${eventFilter}`
        : "/analytics/anomaly/detect";
      const response = await api.get(url);
      setAnomalies(response.anomalies || []);
      await loadSummary();
    } catch (error: any) {
      console.error("Anomaly detection failed:", error);
      setModalData({ 
        show: true, 
        type: 'error', 
        title: 'Detection Failed', 
        message: error.message || "Failed to detect anomalies. Model might need training first." 
      });
    }
    setLoading(false);
  };

  const showDetails = (anomaly: Anomaly) => {
    setSelectedAnomaly(anomaly);
  };

  const closeDetails = () => {
    setSelectedAnomaly(null);
  };

  const getSeverityColor = (severity: string) => {
    return severity === "HIGH" ? "#dc3545" : "#ffc107";
  };

  return (
    <div className="anomaly-detection-page">
      <div className="page-header">
        <h1>
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{display: 'inline-block', verticalAlign: 'middle', marginRight: '8px'}}>
            <circle cx="11" cy="11" r="8"/>
            <path d="m21 21-4.35-4.35"/>
          </svg>
          Anomaly Detection Dashboard
        </h1>
        <p className="subtitle">
          AI-powered detection of suspicious attendance patterns using Isolation Forest algorithm
        </p>
      </div>

      {/* Model Status Section */}
      <div className="model-status-card">
        <h2>Model Status</h2>
        <div className="status-content">
          <div className="status-indicator">
            <div
              className={`status-dot ${modelStatus.is_trained ? "trained" : "untrained"}`}
            ></div>
            <span className="status-text">{modelStatus.status}</span>
          </div>
          <p className="status-message">{modelStatus.message}</p>
          <div className="model-info">
            <span>
              <strong>Model:</strong> {modelStatus.model_type}
            </span>
            <span>
              <strong>Estimators:</strong> {modelStatus.n_estimators}
            </span>
            <span>
              <strong>Contamination:</strong>{" "}
              {(modelStatus.contamination_rate * 100).toFixed(1)}%
            </span>
          </div>
          <div className="model-actions">
            {!modelStatus.is_trained ? (
              <button
                className="train-button"
                onClick={trainModel}
                disabled={training}
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
                  <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
                </svg>
                {training ? "Training..." : "Train Model"}
              </button>
            ) : (
              <button
                className="retrain-button"
                onClick={trainModel}
                disabled={training}
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2"/>
                </svg>
                {training ? "Retraining..." : "Retrain Model"}
              </button>
            )}
          </div>
        </div>
      </div>

      {/* AI Model Performance Metrics */}
      {modelStatus.is_trained && modelStatus.training_info && (
        <div className="ai-metrics-section">
          <div className="metrics-header">
            <h2>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
              </svg>
              AI Model Performance
            </h2>
            <button 
              className="toggle-metrics"
              onClick={() => setShowMetrics(!showMetrics)}
            >
              {showMetrics ? 'Hide Details' : 'Show Details'}
            </button>
          </div>

          <div className="metrics-grid">
            <div className="metric-card">
              <svg className="metric-icon" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="18" y1="20" x2="18" y2="10"></line>
                <line x1="12" y1="20" x2="12" y2="4"></line>
                <line x1="6" y1="20" x2="6" y2="14"></line>
              </svg>
              <div className="metric-content">
                <div className="metric-label">Training Samples</div>
                <div className="metric-value">{modelStatus.training_info.samples_used.toLocaleString()}</div>
                <div className="metric-subtext">records analyzed</div>
              </div>
            </div>

            <div className="metric-card">
              <svg className="metric-icon" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>
              </svg>
              <div className="metric-content">
                <div className="metric-label">Model Health</div>
                <div className={`metric-value health-${modelStatus.model_health?.toLowerCase()}`}>
                  {modelStatus.model_health || 'GOOD'}
                </div>
                <div className="metric-subtext">confidence level</div>
              </div>
            </div>

            <div className="metric-card">
              <svg className="metric-icon" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="11" cy="11" r="8"></circle>
                <path d="m21 21-4.35-4.35"></path>
              </svg>
              <div className="metric-content">
                <div className="metric-label">Features Analyzed</div>
                <div className="metric-value">{modelStatus.training_info.feature_count}</div>
                <div className="metric-subtext">behavioral patterns</div>
              </div>
            </div>

            <div className="metric-card">
              <svg className="metric-icon" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                <line x1="16" y1="2" x2="16" y2="6"></line>
                <line x1="8" y1="2" x2="8" y2="6"></line>
                <line x1="3" y1="10" x2="21" y2="10"></line>
              </svg>
              <div className="metric-content">
                <div className="metric-label">Last Trained</div>
                <div className="metric-value small">
                  {new Date(modelStatus.training_info.trained_at).toLocaleDateString()}
                </div>
                <div className="metric-subtext">
                  {new Date(modelStatus.training_info.trained_at).toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'})}
                </div>
              </div>
            </div>
          </div>

          {showMetrics && modelMetrics && (
            <div className="detailed-metrics">
              {/* Feature Importance */}
              <div className="feature-importance-card">
                <h3>Feature Importance Analysis</h3>
                <p className="section-description">
                  Contribution of each behavioral pattern to anomaly detection
                </p>
                <div className="feature-list">
                  {Object.entries(modelStatus.training_info.feature_importance)
                    .sort(([,a], [,b]) => b - a)
                    .map(([feature, importance]) => (
                      <div key={feature} className="feature-item">
                        <div className="feature-name">
                          {feature.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </div>
                        <div className="feature-bar-container">
                          <div 
                            className="feature-bar"
                            style={{width: `${importance}%`}}
                          >
                            <span className="feature-value">{importance.toFixed(1)}%</span>
                          </div>
                        </div>
                      </div>
                    ))}
                </div>
              </div>

              {/* Score Distribution */}
              <div className="score-distribution-card">
                <h3>Anomaly Score Distribution</h3>
                <p className="section-description">
                  Statistical distribution of anomaly scores during training
                </p>
                <div className="distribution-stats">
                  <div className="stat-item">
                    <div className="stat-label">Mean Score</div>
                    <div className="stat-value">
                      {modelStatus.training_info.score_distribution.mean.toFixed(3)}
                    </div>
                  </div>
                  <div className="stat-item">
                    <div className="stat-label">Std Deviation</div>
                    <div className="stat-value">
                      {modelStatus.training_info.score_distribution.std.toFixed(3)}
                    </div>
                  </div>
                  <div className="stat-item">
                    <div className="stat-label">Min Score</div>
                    <div className="stat-value">
                      {modelStatus.training_info.score_distribution.min.toFixed(3)}
                    </div>
                  </div>
                  <div className="stat-item">
                    <div className="stat-label">Max Score</div>
                    <div className="stat-value">
                      {modelStatus.training_info.score_distribution.max.toFixed(3)}
                    </div>
                  </div>
                </div>
              </div>

              {/* Model Configuration */}
              <div className="model-config-card">
                <h3>Model Configuration</h3>
                <div className="config-grid">
                  <div className="config-item">
                    <span className="config-label">Algorithm:</span>
                    <span className="config-value">Isolation Forest</span>
                  </div>
                  <div className="config-item">
                    <span className="config-label">Version:</span>
                    <span className="config-value">{modelStatus.training_info.model_version}</span>
                  </div>
                  <div className="config-item">
                    <span className="config-label">Contamination Rate:</span>
                    <span className="config-value">{(modelStatus.contamination_rate * 100).toFixed(1)}%</span>
                  </div>
                  <div className="config-item">
                    <span className="config-label">Estimators:</span>
                    <span className="config-value">{modelStatus.n_estimators}</span>
                  </div>
                  <div className="config-item">
                    <span className="config-label">Training Anomalies:</span>
                    <span className="config-value">{modelStatus.training_info.anomalies_detected}</span>
                  </div>
                  <div className="config-item">
                    <span className="config-label">Detection Rate:</span>
                    <span className="config-value">{modelStatus.training_info.anomaly_rate.toFixed(2)}%</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Summary Cards */}
      {summary && (
        <div className="summary-cards">
          <div className="summary-card">
            <h3>Total Checked</h3>
            <div className="card-value">{summary.total_checked}</div>
            <p className="card-label">Attendance Records</p>
          </div>
          <div className="summary-card highlight">
            <h3>Anomalies Detected</h3>
            <div className="card-value">{summary.total_anomalies}</div>
            <p className="card-label">{summary.anomaly_rate.toFixed(2)}% rate</p>
          </div>
          <div className="summary-card severity-high">
            <h3>High Severity</h3>
            <div className="card-value">{summary.by_severity.high}</div>
            <p className="card-label">Requires immediate review</p>
          </div>
          <div className="summary-card severity-medium">
            <h3>Medium Severity</h3>
            <div className="card-value">{summary.by_severity.medium}</div>
            <p className="card-label">Review recommended</p>
          </div>
        </div>
      )}

      {/* Detection Controls */}
      <div className="detection-controls">
        <div className="filter-group">
          <label htmlFor="event-filter">Filter by Event ID:</label>
          <input
            type="text"
            id="event-filter"
            placeholder="Optional event ID"
            value={eventFilter}
            onChange={(e) => setEventFilter(e.target.value)}
          />
        </div>
        <button
          className="detect-button"
          onClick={detectAnomalies}
          disabled={loading || !modelStatus.is_trained}
          title={!modelStatus.is_trained ? "Please train the model first" : "Run anomaly detection"}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="11" cy="11" r="8"/>
            <path d="m21 21-4.35-4.35"/>
          </svg>
          {loading ? "Detecting..." : "Run Anomaly Detection"}
        </button>
      </div>

      {/* Anomaly List */}
      {anomalies.length > 0 ? (
        <div className="anomaly-list">
          <h2>Detected Anomalies ({anomalies.length})</h2>
          <div className="anomaly-grid">
            {anomalies.map((anomaly) => (
              <div
                key={anomaly.attendance_id}
                className={`anomaly-card severity-${anomaly.severity.toLowerCase()}`}
                onClick={() => showDetails(anomaly)}
              >
                <div className="anomaly-header">
                  <span
                    className="severity-badge"
                    style={{ backgroundColor: getSeverityColor(anomaly.severity) }}
                  >
                    {anomaly.severity}
                  </span>
                  <span className="anomaly-id">#{anomaly.attendance_id}</span>
                </div>
                <div className="anomaly-body">
                  <p>
                    <strong>Student:</strong> {anomaly.student_prn}
                  </p>
                  <p>
                    <strong>Event ID:</strong> {anomaly.event_id}
                  </p>
                  <p>
                    <strong>Scanned:</strong>{" "}
                    {new Date(anomaly.scanned_at).toLocaleString()}
                  </p>
                  <p>
                    <strong>Score:</strong> {anomaly.anomaly_score.toFixed(3)}
                  </p>
                  <p className="scan-source">
                    <strong>Source:</strong>{" "}
                    <span className={`source-${anomaly.scan_source.replace("_", "-")}`}>
                      {anomaly.scan_source}
                    </span>
                  </p>
                </div>
                <button className="details-button">View Details →</button>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="no-anomalies">
          {loading ? (
            <p>Scanning for anomalies...</p>
          ) : modelStatus.is_trained ? (
            <p>No anomalies detected. Click "Run Anomaly Detection" to scan.</p>
          ) : (
            <p>Train the model first to start detecting anomalies.</p>
          )}
        </div>
      )}

      {/* Anomaly Details Modal */}
      {selectedAnomaly && (
        <div className="modal-overlay" onClick={closeDetails}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Anomaly Details</h2>
              <button className="close-button" onClick={closeDetails}>
                ×
              </button>
            </div>
            <div className="modal-body">
              <div className="detail-section">
                <h3>Basic Information</h3>
                <p>
                  <strong>Attendance ID:</strong> {selectedAnomaly.attendance_id}
                </p>
                <p>
                  <strong>Student PRN:</strong> {selectedAnomaly.student_prn}
                </p>
                <p>
                  <strong>Event ID:</strong> {selectedAnomaly.event_id}
                </p>
                <p>
                  <strong>Scanned At:</strong>{" "}
                  {new Date(selectedAnomaly.scanned_at).toLocaleString()}
                </p>
                <p>
                  <strong>Scan Source:</strong> {selectedAnomaly.scan_source}
                </p>
                <p>
                  <strong>Severity:</strong>{" "}
                  <span
                    style={{
                      color: getSeverityColor(selectedAnomaly.severity),
                      fontWeight: "bold",
                    }}
                  >
                    {selectedAnomaly.severity}
                  </span>
                </p>
                <p>
                  <strong>Anomaly Score:</strong>{" "}
                  {selectedAnomaly.anomaly_score.toFixed(4)}
                </p>
              </div>

              <div className="detail-section">
                <h3>Explanation</h3>
                <div className="explanation-box">{selectedAnomaly.explanation}</div>
              </div>

              <div className="detail-section">
                <h3>Feature Values</h3>
                <table className="feature-table">
                  <thead>
                    <tr>
                      <th>Feature</th>
                      <th>Value</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(selectedAnomaly.features).map(([key, value]) => (
                      <tr key={key}>
                        <td>{key.replace(/_/g, " ")}</td>
                        <td>{typeof value === "number" ? value.toFixed(2) : value}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Success/Error Modal */}
      {modalData.show && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.4)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 10000
        }} onClick={() => setModalData({ ...modalData, show: false })}>
          <div style={{
            background: 'white',
            borderRadius: '8px',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.12)',
            width: '90%',
            maxWidth: '520px',
            overflow: 'hidden'
          }} onClick={(e) => e.stopPropagation()}>
            <div style={{
              padding: '2rem 2rem 1.5rem',
              borderBottom: '1px solid #e5e7eb'
            }}>
              {modalData.type === 'success' ? (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#22c55e" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" style={{ marginBottom: '0.5rem' }}>
                  <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
              ) : (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" style={{ marginBottom: '0.5rem' }}>
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              )}
              <h2 style={{
                margin: 0,
                fontSize: '1.25rem',
                fontWeight: 600,
                color: '#111827'
              }}>{modalData.title}</h2>
            </div>
            <div style={{
              padding: '2rem',
              maxHeight: '450px',
              overflowY: 'auto'
            }}>
              {modalData.message ? (
                <pre>{modalData.message}</pre>
              ) : modalData.data ? (
                <>
                  <div style={{
                    marginBottom: '1.5rem'
                  }}>
                    <div style={{
                      fontSize: '0.75rem',
                      fontWeight: 600,
                      color: '#6b7280',
                      textTransform: 'uppercase',
                      letterSpacing: '0.05em',
                      marginBottom: '1rem'
                    }}>
                      Training Metrics
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                      <div style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        padding: '0.65rem 0'
                      }}>
                        <span style={{ fontSize: '0.875rem', color: '#6b7280' }}>Samples Analyzed</span>
                        <span style={{ fontSize: '0.875rem', color: '#111827', fontWeight: 500 }}>{modalData.data.trainingMetrics.samplesAnalyzed}</span>
                      </div>
                      <div style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        padding: '0.65rem 0'
                      }}>
                        <span style={{ fontSize: '0.875rem', color: '#6b7280' }}>Features Extracted</span>
                        <span style={{ fontSize: '0.875rem', color: '#111827', fontWeight: 500 }}>{modalData.data.trainingMetrics.featuresExtracted}</span>
                      </div>
                      <div style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        padding: '0.65rem 0'
                      }}>
                        <span style={{ fontSize: '0.875rem', color: '#6b7280' }}>Anomalies Found</span>
                        <span style={{ fontSize: '0.875rem', color: '#111827', fontWeight: 500 }}>{modalData.data.trainingMetrics.anomaliesFound}</span>
                      </div>
                      <div style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        padding: '0.65rem 0'
                      }}>
                        <span style={{ fontSize: '0.875rem', color: '#6b7280' }}>Detection Rate</span>
                        <span style={{ fontSize: '0.875rem', color: '#111827', fontWeight: 500 }}>{modalData.data.trainingMetrics.detectionRate}%</span>
                      </div>
                    </div>
                  </div>
                  <div style={{
                    marginBottom: '1.5rem'
                  }}>
                    <div style={{
                      fontSize: '0.75rem',
                      fontWeight: 600,
                      color: '#6b7280',
                      textTransform: 'uppercase',
                      letterSpacing: '0.05em',
                      marginBottom: '1rem'
                    }}>
                      Model Performance
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                      <div style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        padding: '0.65rem 0'
                      }}>
                        <span style={{ fontSize: '0.875rem', color: '#6b7280' }}>Confidence</span>
                        <span style={{ fontSize: '0.875rem', color: '#111827', fontWeight: 500 }}>{modalData.data.modelPerformance.confidence}</span>
                      </div>
                      <div style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        padding: '0.65rem 0'
                      }}>
                        <span style={{ fontSize: '0.875rem', color: '#6b7280' }}>Score Mean</span>
                        <span style={{ fontSize: '0.875rem', color: '#111827', fontWeight: 500, fontFamily: 'monospace' }}>{modalData.data.modelPerformance.scoreMean}</span>
                      </div>
                    </div>
                  </div>
                  <div style={{
                    background: '#f9fafb',
                    padding: '1rem',
                    borderRadius: '6px',
                    border: '1px solid #e5e7eb',
                    marginTop: '0.5rem'
                  }}>
                    <div style={{
                      fontSize: '0.8125rem',
                      color: '#374151',
                      textAlign: 'center'
                    }}>Model is now ready for real-time anomaly detection</div>
                  </div>
                </>
              ) : null}
            </div>
            <div style={{
              padding: '1.25rem 2rem',
              borderTop: '1px solid #e5e7eb',
              display: 'flex',
              justifyContent: 'flex-end'
            }}>
              <button style={{
                background: '#111827',
                color: 'white',
                border: 'none',
                padding: '0.6rem 2rem',
                borderRadius: '6px',
                fontSize: '0.875rem',
                fontWeight: 500,
                cursor: 'pointer',
                transition: 'all 0.15s ease'
              }} 
              onMouseEnter={(e) => {
                e.currentTarget.style.background = '#1f2937';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = '#111827';
              }}
              onClick={() => setModalData({ ...modalData, show: false })}>
                OK
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Help Guide */}
      {helpContent && <HelpGuide content={helpContent} />}
    </div>
  );
}
