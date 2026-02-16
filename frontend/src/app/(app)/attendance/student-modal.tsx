import { useEffect, useState } from "react";
import api from "@/services/api";
import { toast } from "@/components/Toast";
import "./student-modal.scss";

interface StudentAnalytics {
  student: {
    prn: string;
    name: string;
    email: string;
    branch: string;
    year: number;
    division: string;
  };
  statistics: {
    total_registered: number;
    total_attended: number;
    attendance_rate: number;
    events_missed: number;
  };
  attendance_history: Array<{
    attendance_id: number;
    event_id: number;
    event_title: string;
    event_location: string;
    event_start_time: string;
    scanned_at: string;
  }>;
  registered_events: Array<{
    event_id: number;
    event_title: string;
    event_location: string;
    event_start_time: string;
    registered_at: string;
    ticket_id: number;
    token: string;
    status: "pending" | "completed";
    attended_at?: string;
  }>;
  monthly_stats: Array<{
    month: string;
    count: number;
  }>;
}

interface StudentModalProps {
  prn: string;
  onClose: () => void;
  overrideMode: boolean;
  onAuthRequired: () => Promise<boolean>;
}

export default function StudentModal({ prn, onClose, overrideMode, onAuthRequired }: StudentModalProps) {
  const [data, setData] = useState<StudentAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [expandedTicket, setExpandedTicket] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [authenticatedForPending, setAuthenticatedForPending] = useState(false);

  useEffect(() => {
    async function fetchData() {
      try {
        setError(null);
        const res = await api.get(`/students/${prn}/analytics`);
        setData(res);
      } catch (e: any) {
        console.error("Failed to load student analytics:", e);
        setError(e?.message || "Failed to load student data");
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [prn]);

  async function handlePendingEventClick(ticketId: number) {
    // If already expanded, just collapse
    if (expandedTicket === ticketId) {
      setExpandedTicket(null);
      return;
    }

    // For pending events, check if override mode is enabled or we're already authenticated
    if (overrideMode || authenticatedForPending) {
      setExpandedTicket(ticketId);
    } else {
      // Need authentication
      const authenticated = await onAuthRequired();
      if (authenticated) {
        setAuthenticatedForPending(true);
        setExpandedTicket(ticketId);
      }
    }
  }

  function formatDateTime(isoString: string) {
    if (!isoString) return "N/A";
    const date = new Date(isoString);
    return date.toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  function formatMonth(monthStr: string) {
    if (!monthStr) return monthStr;
    const [year, month] = monthStr.split("-");
    const date = new Date(parseInt(year), parseInt(month) - 1);
    return date.toLocaleString("en-US", { month: "short", year: "numeric" });
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>
          ✕
        </button>

        {loading ? (
          <div className="modal-loading">Loading student analytics...</div>
        ) : error ? (
          <div className="modal-error">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="15" y1="9" x2="9" y2="15"/>
              <line x1="9" y1="9" x2="15" y2="15"/>
            </svg>
            <h3>Unable to Load Data</h3>
            <p>{error}</p>
            <button onClick={onClose} className="error-close-btn">Close</button>
          </div>
        ) : data ? (
          <>
            {/* Student Header */}
            <div className="modal-header">
              <div className="student-avatar">{data.student.name.charAt(0)}</div>
              <div className="student-info">
                <h2>{data.student.name}</h2>
                <div className="student-meta">
                  <span>PRN: {data.student.prn}</span>
                  <span>•</span>
                  <span>{data.student.branch}</span>
                  <span>•</span>
                  <span>Year {data.student.year}</span>
                  {data.student.division && (
                    <>
                      <span>•</span>
                      <span>Div {data.student.division}</span>
                    </>
                  )}
                </div>
                {data.student.email && (
                  <div className="student-email">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                      <polyline points="22,6 12,13 2,6"/>
                    </svg>
                    {data.student.email}
                  </div>
                )}
              </div>
            </div>

            {/* Statistics Cards */}
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-icon">
                  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                    <line x1="16" y1="13" x2="8" y2="13"/>
                    <line x1="16" y1="17" x2="8" y2="17"/>
                    <polyline points="10 9 9 9 8 9"/>
                  </svg>
                </div>
                <div className="stat-value">{data.statistics.total_registered}</div>
                <div className="stat-label">Registered</div>
              </div>
              <div className="stat-card">
                <div className="stat-icon">
                  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                    <polyline points="22 4 12 14.01 9 11.01"/>
                  </svg>
                </div>
                <div className="stat-value">{data.statistics.total_attended}</div>
                <div className="stat-label">Attended</div>
              </div>
              <div className="stat-card">
                <div className="stat-icon">
                  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="10"/>
                    <line x1="15" y1="9" x2="9" y2="15"/>
                    <line x1="9" y1="9" x2="15" y2="15"/>
                  </svg>
                </div>
                <div className="stat-value">{data.statistics.events_missed}</div>
                <div className="stat-label">Missed</div>
              </div>
              <div className="stat-card">
                <div className="stat-icon">
                  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <line x1="18" y1="20" x2="18" y2="10"/>
                    <line x1="12" y1="20" x2="12" y2="4"/>
                    <line x1="6" y1="20" x2="6" y2="14"/>
                  </svg>
                </div>
                <div className="stat-value">{data.statistics.attendance_rate}%</div>
                <div className="stat-label">Attendance Rate</div>
              </div>
            </div>

            {/* Attendance History */}
            {data.attendance_history.length > 0 && (
              <div className="history-section">
                <h3>Attendance History ({data.attendance_history.length})</h3>
                <div className="history-list">
                  {data.attendance_history.map((att) => (
                    <div key={att.attendance_id} className="history-item">
                      <div className="history-icon">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                          <polyline points="22 4 12 14.01 9 11.01"/>
                        </svg>
                      </div>
                      <div className="history-details">
                        <div className="history-title">{att.event_title}</div>
                        <div className="history-meta">
                          {att.event_location && (
                            <>
                              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                                <circle cx="12" cy="10" r="3"/>
                              </svg>
                              <span>{att.event_location}</span>
                            </>
                          )}
                          <span>•</span>
                          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <circle cx="12" cy="12" r="10"/>
                            <polyline points="12 6 12 12 16 14"/>
                          </svg>
                          <span>{formatDateTime(att.scanned_at)}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Registered Events - Show All */}
            {data.registered_events.length > 0 && (
              <div className="history-section">
                <h3>All Registered Events ({data.registered_events.length})</h3>
                <div className="tickets-list">
                  {data.registered_events.map((event) => (
                    <div key={event.event_id} className={`ticket-card ${event.status === "completed" ? "completed" : ""}`}>
                      <div 
                        className="ticket-card-header" 
                        onClick={() => {
                          if (event.status === "completed") {
                            // Completed events - toggle directly
                            setExpandedTicket(expandedTicket === event.ticket_id ? null : event.ticket_id);
                          } else {
                            // Pending events - need auth
                            handlePendingEventClick(event.ticket_id);
                          }
                        }}
                      >
                        <div className="ticket-card-info">
                          <div className="history-icon">
                            {event.status === "completed" ? (
                              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                                <polyline points="22 4 12 14.01 9 11.01"/>
                              </svg>
                            ) : (
                              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <circle cx="12" cy="12" r="10"/>
                                <polyline points="12 6 12 12 16 14"/>
                              </svg>
                            )}
                          </div>
                          <div className="ticket-card-details">
                            <div className="ticket-title-row">
                              <div className="history-title">{event.event_title}</div>
                              <span className={`status-badge ${event.status}`}>
                                {event.status === "completed" ? "Attended" : "Pending"}
                              </span>
                            </div>
                            <div className="history-meta">
                              {event.event_location && (
                                <>
                                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                    <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                                    <circle cx="12" cy="10" r="3"/>
                                  </svg>
                                  <span>{event.event_location}</span>
                                </>
                              )}
                              <span>•</span>
                              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                                <line x1="16" y1="2" x2="16" y2="6"/>
                                <line x1="8" y1="2" x2="8" y2="6"/>
                                <line x1="3" y1="10" x2="21" y2="10"/>
                              </svg>
                              <span>{formatDateTime(event.event_start_time)}</span>
                              {event.attended_at && (
                                <>
                                  <span>•</span>
                                  <span className="attended-time">Attended: {formatDateTime(event.attended_at)}</span>
                                </>
                              )}
                            </div>
                          </div>
                        </div>
                        <button className="expand-btn">
                          <svg 
                            width="20" 
                            height="20" 
                            viewBox="0 0 24 24" 
                            fill="none" 
                            stroke="currentColor" 
                            strokeWidth="2"
                            style={{ transform: expandedTicket === event.ticket_id ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.2s' }}
                          >
                            <polyline points="6 9 12 15 18 9"/>
                          </svg>
                        </button>
                        {event.status === "completed" && (
                          <div className="completed-label">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                              <polyline points="20 6 9 17 4 12"/>
                            </svg>
                          </div>
                        )}
                      </div>
                      
                      {expandedTicket === event.ticket_id && (
                        <div className="ticket-card-body">
                          <div className={`ticket-qr-section ${event.status === "completed" ? "compact" : ""}`}>
                            <div className="qr-container">
                              <div className="qr-label">
                                {event.status === "completed" ? "✓ Attendance Confirmed" : "Scan to Mark Attendance"}
                              </div>
                              <img 
                                src={`/api/tickets/qr?token=${event.token}`} 
                                alt="QR Code"
                                className="qr-image"
                              />
                              <div className="ticket-number">Ticket #{event.ticket_id}</div>
                            </div>
                            <div className="token-container">
                              <div className="token-label">Token (Manual Entry)</div>
                              <textarea 
                                value={event.token} 
                                readOnly 
                                className="token-textarea"
                                rows={event.status === "completed" ? 2 : 3}
                              />
                              <button 
                                className="copy-token-btn"
                                onClick={() => {
                                  navigator.clipboard.writeText(event.token);
                                  toast.success("Token copied!");
                                }}
                              >
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                  <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                                  <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                                </svg>
                                Copy Token
                              </button>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        ) : null}
      </div>
    </div>
  );
}
