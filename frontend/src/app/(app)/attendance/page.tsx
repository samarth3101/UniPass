"use client";

import { useEffect, useState } from "react";
import api from "@/services/api";
import StudentModal from "./student-modal";
import { toast } from "@/components/Toast";
import "./attendance.scss";

type Event = {
  id: number;
  title: string;
};

type Student = {
  ticket_id?: number;
  attendance_id?: number;
  prn: string;
  name: string;
  email: string;
  branch: string;
  year: number;
  division: string;
  registered_at?: string;
  scanned_at: string;
  attended?: boolean;
};

type Summary = {
  total_registered: number;
  total_attended: number;
  total_present: number;
};

export default function AttendancePage() {
  const [events, setEvents] = useState<Event[]>([]);
  const [eventId, setEventId] = useState<number | null>(null);
  const [registeredStudents, setRegisteredStudents] = useState<Student[]>([]);
  const [attendedStudents, setAttendedStudents] = useState<Student[]>([]);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [activeTab, setActiveTab] = useState<"registered" | "attended">("registered");
  const [selectedPrn, setSelectedPrn] = useState<string | null>(null);
  const [overrideMode, setOverrideMode] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authUsername, setAuthUsername] = useState("");
  const [authPassword, setAuthPassword] = useState("");
  const [authError, setAuthError] = useState("");

  useEffect(() => {
    api.get("/events/").then((response) => {
      setEvents(response.events || response);
    });

    const params = new URLSearchParams(window.location.search);
    const id = params.get("event_id");
    if (id) setEventId(Number(id));
  }, []);

  useEffect(() => {
    if (!eventId) return;

    fetchData();
    const interval = setInterval(fetchData, 4000); // auto refresh
    return () => clearInterval(interval);
  }, [eventId]);

  async function fetchData() {
    const [registered, attended, summaryData] = await Promise.all([
      api.get(`/attendance/event/${eventId}/registered`),
      api.get(`/attendance/event/${eventId}/attended`),
      api.get(`/attendance/event/${eventId}/summary`)
    ]);

    setRegisteredStudents(registered.students);
    setAttendedStudents(attended.students);
    setSummary(summaryData);
  }

  function handleOverrideToggle() {
    if (overrideMode) {
      // Disable override mode
      setOverrideMode(false);
    } else {
      // Enable override mode - show auth modal
      setShowAuthModal(true);
      setAuthError("");
      setAuthUsername("");
      setAuthPassword("");
    }
  }

  function handleAuthSubmit(e: React.FormEvent) {
    e.preventDefault();
    
    // Simple authentication - in production, verify against backend
    if (authUsername === "admin" && authPassword === "admin123") {
      setOverrideMode(true);
      setShowAuthModal(false);
      setAuthError("");
    } else {
      setAuthError("Invalid credentials");
    }
  }

  async function handleMarkPresent(studentPrn: string, studentName: string) {
    if (!confirm(`Mark ${studentName} (${studentPrn}) as present?\n\nThis will override event time restrictions.`)) {
      return;
    }

    try {
      const response = await api.post(`/attendance/event/${eventId}/override?student_prn=${studentPrn}`, {});
      toast.success(response.message || "Attendance marked successfully");
      fetchData();
    } catch (error: any) {
      toast.error(error.message || "Failed to mark attendance");
    }
  }

  async function handleRemoveStudent(studentPrn: string, studentName: string, ticketId: number) {
    if (!confirm(`Remove ${studentName} (${studentPrn}) from this event?\n\nThis will delete their registration and ticket.`)) {
      return;
    }

    try {
      await api.delete(`/tickets/${ticketId}`);
      toast.success("Student removed from event");
      fetchData();
    } catch (error: any) {
      toast.error(error.message || "Failed to remove student");
    }
  }

  function exportCSV() {
    window.open(
      `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/export/attendance/event/${eventId}/csv`
    );
  }

  function formatDateTime(isoString: string) {
    if (!isoString) return "N/A";
    const date = new Date(isoString);
    return date.toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  return (
    <div className="attendance-page">
      <h1>Attendance Dashboard</h1>

      <select 
        onChange={(e) => setEventId(Number(e.target.value))}
        value={eventId || ""}
      >
        <option value="">Select Event</option>
        {events.map((e) => (
          <option key={e.id} value={e.id}>
            {e.title}
          </option>
        ))}
      </select>

      {eventId && summary && (
        <>
          <div className="summary-cards">
            <div className="summary-card">
              <h3>{summary.total_registered}</h3>
              <p>Total Registered</p>
            </div>
            <div className="summary-card attended">
              <h3>{summary.total_attended}</h3>
              <p>Total Attended</p>
            </div>
            <div className="summary-card pending">
              <h3>{summary.total_registered - summary.total_attended}</h3>
              <p>Not Attended</p>
            </div>
          </div>

          <div className="tabs">
            <button 
              className={activeTab === "registered" ? "active" : ""}
              onClick={() => setActiveTab("registered")}
            >
              Registered Students ({registeredStudents.length})
            </button>
            <button 
              className={activeTab === "attended" ? "active" : ""}
              onClick={() => setActiveTab("attended")}
            >
              Attended Students ({attendedStudents.length})
            </button>
            
            <button 
              onClick={handleOverrideToggle} 
              className={`override-mode-btn ${overrideMode ? "active" : ""}`}
              title={overrideMode ? "Disable override mode" : "Enable override mode"}
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
              </svg>
              {overrideMode ? "Override: ON" : "Override Mode"}
            </button>

            <button onClick={exportCSV} className="export-btn">
              Export CSV
            </button>
          </div>

          <div className="table-container">
            {activeTab === "registered" && (
              <div className="table">
                <div className={`thead ${overrideMode ? "with-actions" : ""}`}>
                  <span>PRN</span>
                  <span>Name</span>
                  <span>Email</span>
                  <span>Branch</span>
                  <span>Year</span>
                  <span>Division</span>
                  <span>Registered At</span>
                  <span>Status</span>
                  {overrideMode && <span>Actions</span>}
                </div>

                {registeredStudents.length === 0 ? (
                  <div className="empty-state">No students registered yet</div>
                ) : (
                  registeredStudents.map((student, i) => (
                    <div 
                      key={i} 
                      className={`row ${overrideMode ? "with-actions" : ""}`}
                    >
                      <span className="clickable" onClick={() => setSelectedPrn(student.prn)}>{student.prn}</span>
                      <span className="clickable" onClick={() => setSelectedPrn(student.prn)}>{student.name}</span>
                      <span>{student.email || "N/A"}</span>
                      <span>{student.branch || "N/A"}</span>
                      <span>{student.year || "N/A"}</span>
                      <span>{student.division || "N/A"}</span>
                      <span>{formatDateTime(student.registered_at || "")}</span>
                      <span className={student.attended ? "badge-attended" : "badge-pending"}>
                        {student.attended ? "✓ Attended" : "Pending"}
                      </span>
                      {overrideMode && (
                        <span className="action-buttons">
                          {!student.attended && (
                            <button 
                              className="mark-present-btn"
                              onClick={() => handleMarkPresent(student.prn, student.name)}
                              title="Mark as present"
                            >
                              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <polyline points="20 6 9 17 4 12"/>
                              </svg>
                              Present
                            </button>
                          )}
                          <button 
                            className="remove-btn"
                            onClick={() => handleRemoveStudent(student.prn, student.name, student.ticket_id!)}
                            title="Remove from event"
                          >
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                              <line x1="18" y1="6" x2="6" y2="18"/>
                              <line x1="6" y1="6" x2="18" y2="18"/>
                            </svg>
                            Remove
                          </button>
                        </span>
                      )}
                    </div>
                  ))
                )}
              </div>
            )}

            {activeTab === "attended" && (
              <div className="table">
                <div className="thead">
                  <span>PRN</span>
                  <span>Name</span>
                  <span>Email</span>
                  <span>Branch</span>
                  <span>Year</span>
                  <span>Division</span>
                  <span>Scanned At</span>
                </div>

                {attendedStudents.length === 0 ? (
                  <div className="empty-state">No attendance marked yet</div>
                ) : (
                  attendedStudents.map((student, i) => (
                    <div 
                      key={i} 
                      className="row clickable" 
                      onClick={() => setSelectedPrn(student.prn)}
                    >
                      <span>{student.prn}</span>
                      <span>{student.name}</span>
                      <span>{student.email || "N/A"}</span>
                      <span>{student.branch || "N/A"}</span>
                      <span>{student.year || "N/A"}</span>
                      <span>{student.division || "N/A"}</span>
                      <span>{formatDateTime(student.scanned_at)}</span>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        </>
      )}

      {/* Student Detail Modal */}
      {selectedPrn && (
        <StudentModal 
          prn={selectedPrn} 
          onClose={() => setSelectedPrn(null)}
          overrideMode={overrideMode}
          onAuthRequired={async () => {
            if (overrideMode) return true; // Already authenticated
            
            // Show auth modal
            setShowAuthModal(true);
            setAuthError("");
            setAuthUsername("");
            setAuthPassword("");
            
            // Return a promise that resolves when auth is complete
            return new Promise((resolve) => {
              const checkAuth = setInterval(() => {
                if (!showAuthModal && overrideMode) {
                  clearInterval(checkAuth);
                  resolve(true);
                } else if (!showAuthModal && !overrideMode) {
                  clearInterval(checkAuth);
                  resolve(false);
                }
              }, 100);
            });
          }}
        />
      )}

      {/* Admin Authentication Modal */}
      {showAuthModal && (
        <div className="modal-overlay" onClick={() => setShowAuthModal(false)}>
          <div className="auth-modal" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setShowAuthModal(false)}>
              ×
            </button>
            
            <div className="auth-header">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
              </svg>
              <h2>Admin Authentication</h2>
              <p>Enter credentials to enable override mode</p>
            </div>

            <form onSubmit={handleAuthSubmit}>
              <div className="form-group">
                <label>Username</label>
                <input
                  type="text"
                  value={authUsername}
                  onChange={(e) => setAuthUsername(e.target.value)}
                  placeholder="Enter admin username"
                  autoFocus
                  required
                />
              </div>

              <div className="form-group">
                <label>Password</label>
                <input
                  type="password"
                  value={authPassword}
                  onChange={(e) => setAuthPassword(e.target.value)}
                  placeholder="Enter admin password"
                  required
                />
              </div>

              {authError && (
                <div className="auth-error">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="10"/>
                    <line x1="12" y1="8" x2="12" y2="12"/>
                    <line x1="12" y1="16" x2="12.01" y2="16"/>
                  </svg>
                  {authError}
                </div>
              )}

              <div className="auth-actions">
                <button type="button" className="cancel-btn" onClick={() => setShowAuthModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="submit-btn">
                  Authenticate
                </button>
              </div>
            </form>

            <div className="auth-note">
              Override mode allows you to:
              <ul>
                <li>Mark attendance after event has ended</li>
                <li>Remove student registrations</li>
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}