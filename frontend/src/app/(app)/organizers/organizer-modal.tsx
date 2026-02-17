import { useEffect, useState } from "react";
import api from "@/services/api";
import { toast } from "@/components/Toast";
import "./organizer-modal.scss";

interface OrganizerAnalytics {
  organizer: {
    id: number;
    email: string;
    full_name: string;
    role: string;
  };
  statistics: {
    total_events: number;
    total_registrations: number;
    total_attended: number;
    attendance_rate: number;
  };
  events: Array<{
    event_id: number;
    event_title: string;
    event_location: string;
    event_start_time: string;
    event_end_time: string;
    created_at: string;
    total_registered: number;
    total_attended: number;
    attendance_rate: number;
    status: "completed" | "upcoming";
  }>;
  monthly_stats: Array<{
    month: string;
    count: number;
  }>;
}

interface OrganizerModalProps {
  organizerId: number;
  onClose: () => void;
  onUpdate: () => void;
}

export default function OrganizerModal({ organizerId, onClose, onUpdate }: OrganizerModalProps) {
  const [data, setData] = useState<OrganizerAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingName, setEditingName] = useState(false);
  const [newName, setNewName] = useState("");
  const [savingName, setSavingName] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleting, setDeleting] = useState(false);

  async function fetchData() {
    try {
      setError(null);
      const res = await api.get(`/organizers/${organizerId}/analytics`);
      setData(res);
      setNewName(res.organizer.full_name);
    } catch (e: any) {
      console.error("Failed to load organizer analytics:", e);
      setError(e?.message || "Failed to load organizer data");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchData();
  }, [organizerId]);

  async function handleSaveName() {
    if (!newName.trim()) {
      toast.error("Name cannot be empty");
      return;
    }

    setSavingName(true);
    try {
      await api.put(`/admin/users/${organizerId}/name?full_name=${encodeURIComponent(newName.trim())}`);
      toast.success("Name updated successfully");
      setEditingName(false);
      await fetchData();
      onUpdate();
    } catch (e: any) {
      console.error("Failed to update name:", e);
      toast.error(e?.message || "Failed to update name");
    } finally {
      setSavingName(false);
    }
  }

  async function handleDelete() {
    setDeleting(true);
    try {
      await api.delete(`/admin/users/${organizerId}`);
      toast.success("Organizer deleted successfully");
      onUpdate();
      onClose();
    } catch (e: any) {
      console.error("Failed to delete organizer:", e);
      toast.error(e?.message || "Failed to delete organizer");
      setShowDeleteConfirm(false);
    } finally {
      setDeleting(false);
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
      <div className="modal-content organizer-modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>
          ✕
        </button>

        {loading ? (
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Loading organizer data...</p>
          </div>
        ) : error ? (
          <div className="error-container">
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
            {/* Organizer Header */}
            <div className="modal-header">
              <div className="organizer-avatar">
                <svg width="50" height="50" viewBox="0 0 24 24" fill="none">
                  <circle cx="12" cy="8" r="4" stroke="currentColor" strokeWidth="2"/>
                  <path d="M6 21v-2a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                </svg>
              </div>
              <div className="organizer-info">
                {editingName ? (
                  <div className="name-edit-form">
                    <input
                      type="text"
                      value={newName}
                      onChange={(e) => setNewName(e.target.value)}
                      placeholder="Enter organizer name"
                      className="name-input"
                      autoFocus
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          handleSaveName();
                        }
                      }}
                    />
                    <div className="name-actions">
                      <button onClick={handleSaveName} disabled={savingName} className="save-btn">
                        {savingName ? "Saving..." : "Save"}
                      </button>
                      <button onClick={() => {
                        setEditingName(false);
                        setNewName(data.organizer.full_name);
                      }} className="cancel-btn">
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  <>
                    <h2>
                      {data.organizer.full_name}
                      <button 
                        onClick={() => setEditingName(true)} 
                        className="edit-name-btn"
                        title="Edit name"
                      >
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                          <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                        </svg>
                      </button>
                    </h2>
                    <div className="organizer-meta">
                      <span className="organizer-email">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                          <polyline points="22,6 12,13 2,6"/>
                        </svg>
                        {data.organizer.email}
                      </span>
                      <span className="role-badge">{data.organizer.role}</span>
                    </div>
                  </>
                )}
              </div>
            </div>

            {/* Statistics Cards */}
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-content">
                  <div className="stat-icon">
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <rect x="3" y="4" width="18" height="18" rx="2"/>
                      <line x1="16" y1="2" x2="16" y2="6" strokeLinecap="round"/>
                      <line x1="8" y1="2" x2="8" y2="6" strokeLinecap="round"/>
                      <line x1="3" y1="10" x2="21" y2="10"/>
                    </svg>
                  </div>
                  <div className="stat-value">{data.statistics.total_events}</div>
                  <div className="stat-label">Events Created</div>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-content">
                  <div className="stat-icon">
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                      <circle cx="9" cy="7" r="4"/>
                      <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                      <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                    </svg>
                  </div>
                  <div className="stat-value">{data.statistics.total_registrations}</div>
                  <div className="stat-label">Total<br/>Registrations</div>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-content">
                  <div className="stat-icon">
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                      <polyline points="22 4 12 14.01 9 11.01"/>
                    </svg>
                  </div>
                  <div className="stat-value">{data.statistics.total_attended}</div>
                  <div className="stat-label">Total<br/>Attended</div>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-content">
                  <div className="stat-icon">
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/>
                      <polyline points="17 6 23 6 23 12"/>
                    </svg>
                  </div>
                  <div className="stat-value">{data.statistics.attendance_rate.toFixed(1)}%</div>
                  <div className="stat-label">Attendance<br/>Rate</div>
                </div>
              </div>
            </div>

            {/* Delete Button */}
            <div className="modal-actions">
              <button 
                onClick={() => setShowDeleteConfirm(true)} 
                className="delete-user-btn"
                title={data.statistics.total_events > 0 
                  ? `Cannot delete organizer with ${data.statistics.total_events} event(s)` 
                  : "Delete organizer"}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M3 6h18"/>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                  <line x1="10" y1="11" x2="10" y2="17"/>
                  <line x1="14" y1="11" x2="14" y2="17"/>
                </svg>
                Delete Organizer
              </button>
            </div>

            {/* Events List */}
            <div className="events-section">
              <h3>Events ({data.events.length})</h3>
              <div className="events-list">
                {data.events.length === 0 ? (
                  <div className="no-events">No events created yet</div>
                ) : (
                  data.events.map((event) => (
                    <div key={event.event_id} className="event-item">
                      <div className="event-header">
                        <div className="event-title-section">
                          <h4>{event.event_title}</h4>
                          <span className={`event-status ${event.status}`}>
                            {event.status === "completed" ? "Completed" : "Upcoming"}
                          </span>
                        </div>
                        <div className="event-meta">
                          <span className="event-location">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                              <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                              <circle cx="12" cy="10" r="3"/>
                            </svg>
                            {event.event_location}
                          </span>
                          <span className="event-date">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                              <circle cx="12" cy="12" r="10"/>
                              <polyline points="12 6 12 12 16 14"/>
                            </svg>
                            {formatDateTime(event.event_start_time)}
                          </span>
                        </div>
                      </div>
                      <div className="event-stats">
                        <div className="event-stat">
                          <span className="event-stat-value">{event.total_registered}</span>
                          <span className="event-stat-label">Registered</span>
                        </div>
                        <div className="event-stat">
                          <span className="event-stat-value">{event.total_attended}</span>
                          <span className="event-stat-label">Attended</span>
                        </div>
                        <div className="event-stat">
                          <span className="event-stat-value">{event.attendance_rate.toFixed(1)}%</span>
                          <span className="event-stat-label">Rate</span>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </>
        ) : null}

        {/* Delete Confirmation Dialog */}
        {showDeleteConfirm && (
          <div className="confirm-dialog">
            <div className="confirm-content">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
              <h3>Delete Organizer?</h3>
              <p>Are you sure you want to delete <strong>{data?.organizer.full_name}</strong>? 
              {data && data.statistics.total_events > 0 && (
                <span style={{color: '#dc2626', display: 'block', marginTop: '8px', fontWeight: 600}}>
                  ⚠️ This organizer has {data.statistics.total_events} event(s) and cannot be deleted.
                </span>
              )}
              </p>
              <div className="confirm-actions">
                <button onClick={() => setShowDeleteConfirm(false)} className="cancel-btn" disabled={deleting}>
                  Cancel
                </button>
                <button 
                  onClick={handleDelete} 
                  className="confirm-delete-btn" 
                  disabled={deleting || !!(data && data.statistics.total_events > 0)}
                >
                  {deleting ? "Deleting..." : "Delete"}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
