import { useEffect, useState } from "react";
import api from "@/services/api";
import { toast } from "@/components/Toast";
import "./scanner-modal.scss";

interface ScannerAnalytics {
  scanner: {
    id: number;
    email: string;
    full_name: string;
    role: string;
  };
  statistics: {
    total_scans: number;
    unique_students: number;
    unique_events: number;
  };
  recent_scans: Array<{
    attendance_id: number;
    student_prn: string;
    student_name: string;
    student_email: string | null;
    student_branch: string | null;
    event_id: number;
    event_title: string;
    scanned_at: string;
  }>;
}

interface ScannerModalProps {
  scannerId: number;
  onClose: () => void;
  onUpdate: () => void;
}

export default function ScannerModal({ scannerId, onClose, onUpdate }: ScannerModalProps) {
  const [data, setData] = useState<ScannerAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingName, setEditingName] = useState(false);
  const [newName, setNewName] = useState("");
  const [savingName, setSavingName] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    fetchData();
  }, [scannerId]);

  async function fetchData() {
    try {
      setError(null);
      const res = await api.get(`/admin/scanners/${scannerId}/analytics`);
      setData(res);
      setNewName(res.scanner.full_name);
    } catch (e: any) {
      console.error("Failed to load scanner analytics:", e);
      setError(e?.message || "Failed to load scanner data");
    } finally {
      setLoading(false);
    }
  }

  async function handleSaveName() {
    if (!newName.trim()) {
      toast.error("Name cannot be empty");
      return;
    }

    setSavingName(true);
    try {
      await api.put(`/admin/users/${scannerId}/name?full_name=${encodeURIComponent(newName.trim())}`);
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
      await api.delete(`/admin/users/${scannerId}`);
      toast.success("Scanner deleted successfully");
      onUpdate();
      onClose();
    } catch (e: any) {
      console.error("Failed to delete scanner:", e);
      toast.error(e?.message || "Failed to delete scanner");
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

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content scanner-modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>
          ✕
        </button>

        {loading ? (
          <div className="modal-loading">Loading scanner analytics...</div>
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
            {/* Scanner Header */}
            <div className="modal-header">
              <div className="scanner-avatar">
                <svg width="50" height="50" viewBox="0 0 24 24" fill="none">
                  <rect x="2" y="2" width="20" height="20" rx="2" stroke="currentColor" strokeWidth="2"/>
                  <path d="M7 8h0.01M7 12h0.01M7 16h0.01M12 8h5M12 12h5M12 16h5" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                </svg>
              </div>
              <div className="scanner-info">
                {editingName ? (
                  <div className="name-edit-form">
                    <input
                      type="text"
                      value={newName}
                      onChange={(e) => setNewName(e.target.value)}
                      placeholder="Enter scanner name"
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
                        setNewName(data.scanner.full_name);
                      }} className="cancel-btn">
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  <>
                    <h2>
                      {data.scanner.full_name}
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
                    <div className="scanner-meta">
                      <span className="scanner-email">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                          <polyline points="22,6 12,13 2,6"/>
                        </svg>
                        {data.scanner.email}
                      </span>
                      <span className="role-badge">{data.scanner.role}</span>
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
                      <path d="M2 2h20v20H2z"/>
                      <path d="M7 8h0.01M7 12h0.01M7 16h0.01"/>
                    </svg>
                  </div>
                  <div className="stat-value">{data.statistics.total_scans}</div>
                  <div className="stat-label">Total Scans</div>
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
                  <div className="stat-value">{data.statistics.unique_students}</div>
                  <div className="stat-label">Unique Students</div>
                </div>
              </div>
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
                  <div className="stat-value">{data.statistics.unique_events}</div>
                  <div className="stat-label">Events Scanned</div>
                </div>
              </div>
            </div>

            {/* Delete Button */}
            <div className="modal-actions">
              <button 
                onClick={() => setShowDeleteConfirm(true)} 
                className="delete-user-btn"
                title="Delete scanner"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M3 6h18"/>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                  <line x1="10" y1="11" x2="10" y2="17"/>
                  <line x1="14" y1="11" x2="14" y2="17"/>
                </svg>
                Delete Scanner
              </button>
            </div>

            {/* Recent Scans Table */}
            <div className="scans-section">
              <h3>Recent Scans</h3>
              {data.recent_scans.length === 0 ? (
                <div className="no-data">No scan records found</div>
              ) : (
                <div className="scans-table-wrapper">
                  <table className="scans-table">
                    <thead>
                      <tr>
                        <th>Student</th>
                        <th>PRN</th>
                        <th>Branch</th>
                        <th>Event</th>
                        <th>Scanned At</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.recent_scans.map((scan) => (
                        <tr key={scan.attendance_id}>
                          <td className="student-name">{scan.student_name}</td>
                          <td className="student-prn">{scan.student_prn}</td>
                          <td className="student-branch">{scan.student_branch || "N/A"}</td>
                          <td className="event-title">{scan.event_title}</td>
                          <td className="scan-time">{formatDateTime(scan.scanned_at)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
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
              <h3>Delete Scanner?</h3>
              <p>Are you sure you want to delete <strong>{data?.scanner.full_name}</strong>? This action cannot be undone.</p>
              <div className="confirm-actions">
                <button onClick={() => setShowDeleteConfirm(false)} className="cancel-btn" disabled={deleting}>
                  Cancel
                </button>
                <button onClick={handleDelete} className="confirm-delete-btn" disabled={deleting}>
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
