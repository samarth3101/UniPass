"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import api from "@/services/api";
import { isAdmin } from "@/lib/auth";
import AuditLogs from "./audit-logs";
import FeedbackModal from "./feedback-modal";
import { toast } from "@/components/Toast";

type Event = {
  id: number;
  title: string;
  description: string;
  location: string;
  start_time: string;
  end_time: string;
};

type Props = {
  event: Event;
  onClose: () => void;
};

// Helper to convert ISO string to datetime-local format (in local timezone)
function isoToDatetimeLocal(isoString: string): string {
  const date = new Date(isoString);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  return `${year}-${month}-${day}T${hours}:${minutes}`;
}

export default function EventModal({ event, onClose }: Props) {
  const router = useRouter();
  const userIsAdmin = isAdmin();

  const [edit, setEdit] = useState(false);
  const [form, setForm] = useState({
    ...event,
    start_time: isoToDatetimeLocal(event.start_time),
    end_time: isoToDatetimeLocal(event.end_time),
  });
  const [loading, setLoading] = useState(false);
  const [shareLink, setShareLink] = useState<string | null>(null);
  const [loadingShare, setLoadingShare] = useState(false);
  const [showEmailForm, setShowEmailForm] = useState(false);
  const [teacherEmail, setTeacherEmail] = useState("");
  const [teacherName, setTeacherName] = useState("Professor");
  const [sendingEmail, setSendingEmail] = useState(false);
  const [certificateStats, setCertificateStats] = useState<any>(null);
  const [pushingCertificates, setPushingCertificates] = useState(false);
  const [showCertificateInfo, setShowCertificateInfo] = useState(false);
  const [sendingFeedback, setSendingFeedback] = useState(false);
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);

  async function handleUpdate() {
    setLoading(true);
    try {
      // Convert datetime-local to ISO format with timezone
      const startDate = new Date(form.start_time);
      const endDate = new Date(form.end_time);
      
      const payload = {
        ...form,
        start_time: startDate.toISOString(),
        end_time: endDate.toISOString(),
      };
      
      await api.put(`/events/${event.id}`, payload);
      setEdit(false);
      router.refresh();
    } catch (error) {
      console.error("Failed to update event:", error);
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete() {
    if (!confirm("Delete this event?")) return;
    try {
      await api.delete(`/events/${event.id}`);
      router.refresh();
      onClose();
    } catch (error: any) {
      if (error.response?.status === 403) {
        toast.error("Only administrators can delete events");
      } else {
        toast.error("Failed to delete event");
      }
    }
  }

  async function fetchShareLink() {
    setLoadingShare(true);
    try {
      const res = await api.get(`/events/${event.id}/share`);
      setShareLink(res.share_url);
    } catch (error) {
      console.error('Error fetching share link:', error);
      toast.error('Failed to generate share link');
    } finally {
      setLoadingShare(false);
    }
  }

  function viewAttendance() {
    router.push(`/attendance?event_id=${event.id}`);
    onClose();
  }

  function exportCSV() {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    window.open(
      `${apiUrl}/export/attendance/event/${event.id}/csv`,
      "_blank"
    );
  }

  function openLiveMonitor() {
    window.open(`/monitor/${event.id}`, "_blank");
  }

  async function generateReport() {
    try {
      const token = localStorage.getItem("unipass_token");
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/events/${event.id}/report`, {
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to generate report");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `Event_Report_${event.id}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Error generating report:", error);
      toast.error("Failed to generate report. Please try again.");
    }
  }

  async function sendTeacherEmail() {
    if (!teacherEmail || !teacherEmail.includes("@")) {
      toast.error("Please enter a valid email address");
      return;
    }

    setSendingEmail(true);
    try {
      const response = await api.post(
        `/export/attendance/event/${event.id}/teacher?teacher_email=${encodeURIComponent(teacherEmail)}&teacher_name=${encodeURIComponent(teacherName)}`
      );
      
      toast.success(`Attendance report sent successfully to ${teacherEmail}`);
      setShowEmailForm(false);
      setTeacherEmail("");
      setTeacherName("Professor");
    } catch (error: any) {
      console.error("Error sending teacher email:", error);
      toast.error(error.response?.data?.detail || "Failed to send email. Check SMTP configuration.");
    } finally {
      setSendingEmail(false);
    }
  }

  async function loadCertificateStats() {
    try {
      const stats = await api.get(`/certificates/event/${event.id}/stats`);
      setCertificateStats(stats);
      setShowCertificateInfo(true);
    } catch (error: any) {
      console.error("Error loading certificate stats:", error);
      toast.error("Failed to load certificate statistics");
    }
  }

  async function pushCertificates() {
    if (!certificateStats) {
      await loadCertificateStats();
      return;
    }

    if (certificateStats.pending_certificates === 0) {
      toast.info("No new certificates to send. All eligible students have already received certificates.");
      return;
    }

    if (!confirm(`Send certificates to ${certificateStats.pending_certificates} student(s)?`)) {
      return;
    }

    setPushingCertificates(true);
    try {
      const result = await api.post(`/certificates/event/${event.id}/push`);
      
      if (result.success) {
        const message = `Successfully issued ${result.certificates_issued} certificate(s). ` +
                       `Emails sent: ${result.emails_sent}, Failed: ${result.emails_failed}`;
        toast.success(message);
        
        // Reload stats
        await loadCertificateStats();
      }
    } catch (error: any) {
      console.error("Error pushing certificates:", error);
      toast.error(error.response?.data?.detail || "Failed to push certificates");
    } finally {
      setPushingCertificates(false);
    }
  }

  async function sendFeedbackRequests() {
    if (!confirm(`Send feedback request emails to all attended students?`)) {
      return;
    }

    setSendingFeedback(true);
    try {
      const result = await api.post(`/feedback/send-requests/${event.id}`);
      
      const message = `Feedback requests sent! ` +
                     `Emails sent: ${result.emails_sent}, Failed: ${result.emails_failed}` +
                     (result.already_submitted > 0 ? `, Already submitted: ${result.already_submitted}` : '');
      toast.success(message);
    } catch (error: any) {
      console.error("Error sending feedback requests:", error);
      toast.error(error.response?.data?.detail || "Failed to send feedback requests");
    } finally {
      setSendingFeedback(false);
    }
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal large" onClick={(e) => e.stopPropagation()}>
        <h2>Event Control Center</h2>

        <div className="control-actions">
          <button type="button" onClick={fetchShareLink} className="control-btn" disabled={loadingShare}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            {loadingShare ? 'Loading...' : 'Share Link'}
          </button>

          <button type="button" onClick={viewAttendance} className="control-btn">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <path d="M18 20V10M12 20V4M6 20v-6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            View Attendance
          </button>

          <button type="button" onClick={openLiveMonitor} className="control-btn monitor-btn">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <rect x="2" y="3" width="20" height="14" rx="2" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <line x1="8" y1="21" x2="16" y2="21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <line x1="12" y1="17" x2="12" y2="21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <circle cx="12" cy="10" r="3" fill="currentColor"/>
            </svg>
            Live Monitor
          </button>

          <button type="button" onClick={exportCSV} className="control-btn">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            Export CSV
          </button>

          <button type="button" onClick={generateReport} className="control-btn report-btn">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <polyline points="14 2 14 8 20 8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <line x1="12" y1="18" x2="12" y2="12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <line x1="9" y1="15" x2="15" y2="15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            Generate Report
          </button>

          <button type="button" onClick={() => setShowEmailForm(!showEmailForm)} className="control-btn email-btn">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <polyline points="22,6 12,13 2,6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            Email Teacher
          </button>

          <button type="button" onClick={pushCertificates} className="control-btn certificate-btn" disabled={pushingCertificates}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <path d="M12 15a3 3 0 100-6 3 3 0 000 6z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            {pushingCertificates ? 'Pushing...' : 'Push Certificates'}
          </button>

          <button type="button" onClick={sendFeedbackRequests} className="control-btn feedback-btn" disabled={sendingFeedback}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <path d="M21 11.5a8.38 8.38 0 01-.9 3.8 8.5 8.5 0 01-7.6 4.7 8.38 8.38 0 01-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 01-.9-3.8 8.5 8.5 0 014.7-7.6 8.38 8.38 0 013.8-.9h.5a8.48 8.48 0 018 8v.5z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            {sendingFeedback ? 'Sending...' : 'Send Feedback Requests'}
          </button>

          <button type="button" onClick={() => setShowFeedbackModal(true)} className="control-btn view-feedback-btn">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <polyline points="14 2 14 8 20 8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <line x1="16" y1="13" x2="8" y2="13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <line x1="16" y1="17" x2="8" y2="17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <polyline points="10 9 9 9 8 9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            View Feedback
          </button>
        </div>

        {showCertificateInfo && certificateStats && (
          <div style={{
            margin: '20px 0',
            padding: '20px',
            background: '#fef3c7',
            border: '2px solid #f59e0b',
            borderRadius: '12px'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h4 style={{ margin: 0, color: '#92400e' }}>Certificate Status</h4>
              <button 
                onClick={() => setShowCertificateInfo(false)}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#78350f',
                  cursor: 'pointer',
                  fontSize: '20px',
                  lineHeight: '1',
                  padding: '0 4px'
                }}
              >
                ×
              </button>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '12px' }}>
              <div style={{ background: 'white', padding: '12px', borderRadius: '8px' }}>
                <div style={{ color: '#78350f', fontSize: '12px', fontWeight: 600, marginBottom: '4px' }}>Total Registered</div>
                <div style={{ color: '#92400e', fontSize: '24px', fontWeight: 700 }}>{certificateStats.total_registered}</div>
              </div>
              <div style={{ background: 'white', padding: '12px', borderRadius: '8px' }}>
                <div style={{ color: '#78350f', fontSize: '12px', fontWeight: 600, marginBottom: '4px' }}>Attended</div>
                <div style={{ color: '#92400e', fontSize: '24px', fontWeight: 700 }}>{certificateStats.total_attended}</div>
              </div>
              <div style={{ background: 'white', padding: '12px', borderRadius: '8px' }}>
                <div style={{ color: '#78350f', fontSize: '12px', fontWeight: 600, marginBottom: '4px' }}>Certificates Issued</div>
                <div style={{ color: '#92400e', fontSize: '24px', fontWeight: 700 }}>{certificateStats.total_certificates_issued}</div>
              </div>
              <div style={{ background: certificateStats.pending_certificates > 0 ? '#dcfce7' : 'white', padding: '12px', borderRadius: '8px' }}>
                <div style={{ color: '#78350f', fontSize: '12px', fontWeight: 600, marginBottom: '4px' }}>Pending</div>
                <div style={{ color: certificateStats.pending_certificates > 0 ? '#16a34a' : '#92400e', fontSize: '24px', fontWeight: 700 }}>{certificateStats.pending_certificates}</div>
              </div>
            </div>
            {certificateStats.pending_certificates > 0 && (
              <div style={{ marginTop: '12px', padding: '12px', background: '#dcfce7', borderRadius: '8px' }}>
                <p style={{ margin: 0, color: '#166534', fontSize: '13px' }}>
                  🎓 {certificateStats.pending_certificates} student(s) are eligible for certificates. Click "Push Certificates" to send them.
                </p>
              </div>
            )}
          </div>
        )}

        {showEmailForm && (
          <div style={{
            margin: '20px 0',
            padding: '20px',
            background: '#f0fdf4',
            border: '2px solid #10b981',
            borderRadius: '12px'
          }}>
            <h4 style={{ margin: '0 0 16px 0', color: '#1e293b' }}>Send Attendance Report to Teacher</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '6px', color: '#475569', fontSize: '14px', fontWeight: 600 }}>
                  Teacher Name
                </label>
                <input
                  type="text"
                  value={teacherName}
                  onChange={(e) => setTeacherName(e.target.value)}
                  placeholder="Professor Name"
                  style={{
                    width: '100%',
                    padding: '10px 14px',
                    border: '1px solid #e5e9f2',
                    borderRadius: '8px',
                    fontSize: '14px',
                    fontFamily: 'inherit'
                  }}
                />
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '6px', color: '#475569', fontSize: '14px', fontWeight: 600 }}>
                  Teacher Email
                </label>
                <input
                  type="email"
                  value={teacherEmail}
                  onChange={(e) => setTeacherEmail(e.target.value)}
                  placeholder="teacher@university.edu"
                  style={{
                    width: '100%',
                    padding: '10px 14px',
                    border: '1px solid #e5e9f2',
                    borderRadius: '8px',
                    fontSize: '14px',
                    fontFamily: 'inherit'
                  }}
                />
              </div>
              <div style={{ display: 'flex', gap: '10px', marginTop: '8px' }}>
                <button 
                  type="button"
                  onClick={sendTeacherEmail}
                  disabled={sendingEmail || !teacherEmail}
                  style={{
                    flex: 1,
                    padding: '12px 20px',
                    background: '#10b981',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: sendingEmail || !teacherEmail ? 'not-allowed' : 'pointer',
                    fontWeight: '600',
                    opacity: sendingEmail || !teacherEmail ? 0.6 : 1
                  }}
                >
                  {sendingEmail ? 'Sending...' : 'Send Report'}
                </button>
                <button 
                  type="button"
                  onClick={() => {
                    setShowEmailForm(false);
                    setTeacherEmail("");
                    setTeacherName("Professor");
                  }}
                  style={{
                    padding: '12px 20px',
                    background: '#f1f5f9',
                    color: '#475569',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    fontWeight: '600'
                  }}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        {shareLink && (
          <div style={{
            margin: '20px 0',
            padding: '20px',
            background: '#f0f9ff',
            border: '2px solid #3b82f6',
            borderRadius: '12px'
          }}>
            <h4 style={{ margin: '0 0 12px 0', color: '#1e293b' }}>Registration Link</h4>
            <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
              <div style={{
                flex: 1,
                padding: '12px',
                background: 'white',
                border: '1px solid #e5e9f2',
                borderRadius: '8px',
                fontSize: '13px',
                wordBreak: 'break-all',
                fontFamily: 'monospace'
              }}>
                {shareLink}
              </div>
              <button 
                type="button"
                onClick={async () => {
                  try {
                    await navigator.clipboard.writeText(shareLink);
                    toast.success('Link copied to clipboard!');
                  } catch (err) {
                    toast.error('Failed to copy link');
                  }
                }} 
                style={{
                  padding: '12px 20px',
                  background: '#4f46e5',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontWeight: '600'
                }}
              >
                Copy
              </button>
            </div>
          </div>
        )}

        <div className="divider"></div>
        <AuditLogs eventId={event.id} />

        <div className="divider"></div>
        <div className="section-header">
          <h3>Event Details</h3>
          {!edit && (
            <button type="button" onClick={() => setEdit(true)} className="edit-btn">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              Edit
            </button>
          )}
        </div>

        <div className="form-group">
          <label>Event Title</label>
          <input
            disabled={!edit}
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
          />
        </div>

        <div className="form-group">
          <label>Description</label>
          <textarea
            disabled={!edit}
            value={form.description || ""}
            onChange={(e) =>
              setForm({ ...form, description: e.target.value })
            }
          />
        </div>

        <div className="form-group">
          <label>Location</label>
          <input
            disabled={!edit}
            value={form.location}
            onChange={(e) =>
              setForm({ ...form, location: e.target.value })
            }
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Start Time</label>
            <input
              type="datetime-local"
              disabled={!edit}
              value={form.start_time}
              onChange={(e) =>
                setForm({ ...form, start_time: e.target.value })
              }
            />
          </div>

          <div className="form-group">
            <label>End Time</label>
            <input
              type="datetime-local"
              disabled={!edit}
              value={form.end_time}
              onChange={(e) =>
                setForm({ ...form, end_time: e.target.value })
              }
            />
          </div>
        </div>

        <div className="modal-actions">
          {!edit ? (
            <>
              {userIsAdmin && (
                <button type="button" className="danger-btn" onClick={handleDelete}>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                    <polyline points="3 6 5 6 21 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                  Delete Event
                </button>
              )}
              <button type="button" onClick={onClose} className="secondary-btn">Close</button>
            </>
          ) : (
            <>
              <button type="button" onClick={() => setEdit(false)} className="secondary-btn">Cancel</button>
              <button type="button" onClick={handleUpdate} disabled={loading} className="primary-btn">
                {loading ? 'Saving...' : 'Save Changes'}
              </button>
            </>
          )}
        </div>
      </div>

      {showFeedbackModal && (
        <FeedbackModal
          eventId={event.id}
          eventTitle={event.title}
          onClose={() => setShowFeedbackModal(false)}
        />
      )}
    </div>
  );
}