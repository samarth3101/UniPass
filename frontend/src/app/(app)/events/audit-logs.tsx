"use client";

import { useState, useEffect } from "react";
import api from "@/services/api";

type AuditLog = {
  id: number;
  action_type: string;
  details: Record<string, any>;
  user_email: string | null;
  timestamp: string;
  ip_address: string | null;
};

type Props = {
  eventId: number;
};

export default function AuditLogs({ eventId }: Props) {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchLogs();
  }, [eventId]);

  async function fetchLogs() {
    try {
      setLoading(true);
      setError(null);
      const res = await api.get(`/events/${eventId}/audit-logs`);
      setLogs(res);
    } catch (error: any) {
      console.error("Failed to fetch audit logs:", error);
      setError(error.response?.data?.detail || "Failed to load audit logs");
    } finally {
      setLoading(false);
    }
  }

  function getActionBadgeClass(actionType: string): string {
    switch (actionType) {
      case "event_created":
        return "badge badge-success";
      case "event_edited":
        return "badge badge-info";
      case "event_deleted":
        return "badge badge-danger";
      case "qr_scanned":
        return "badge badge-primary";
      case "ticket_deleted":
        return "badge badge-warning";
      case "override_used":
        return "badge badge-warning";
      case "certificates_pushed":
      case "role_certificates_pushed":
      case "certificates_resent":
        return "badge badge-certificate";
      case "feedback_sent":
        return "badge badge-feedback";
      case "volunteer_added":
      case "volunteer_removed":
        return "badge badge-info";
      default:
        return "badge";
    }
  }

  function getActionLabel(actionType: string): string {
    switch (actionType) {
      case "event_created":
        return "Created";
      case "event_edited":
        return "Edited";
      case "event_deleted":
        return "Deleted";
      case "qr_scanned":
        return "QR Scan";
      case "ticket_deleted":
        return "Ticket Deleted";
      case "override_used":
        return "Override";
      case "certificates_pushed":
        return "Certificates Pushed";
      case "role_certificates_pushed":
        return "Role Certificates Pushed";
      case "certificates_resent":
        return "Certificates Resent";
      case "feedback_sent":
        return "Feedback Requests Sent";
      case "volunteer_added":
        return "Volunteer Added";
      case "volunteer_removed":
        return "Volunteer Removed";
      default:
        return actionType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }
  }

  function formatTimestamp(timestamp: string): string {
    try {
      const date = new Date(timestamp);
      const now = new Date();
      const diff = now.getTime() - date.getTime();
      
      // Handle future timestamps (possible timezone issues)
      if (diff < 0) {
        return date.toLocaleDateString() + " " + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      }
      
      const seconds = Math.floor(diff / 1000);
      const minutes = Math.floor(diff / 60000);
      const hours = Math.floor(diff / 3600000);
      const days = Math.floor(diff / 86400000);

      if (seconds < 30) return "Just now";
      if (minutes < 1) return `${seconds}s ago`;
      if (minutes < 60) return `${minutes}m ago`;
      if (hours < 24) return `${hours}h ago`;
      if (days < 7) return `${days}d ago`;
      
      return date.toLocaleDateString() + " " + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch (error) {
      console.error('Error formatting timestamp:', timestamp, error);
      return timestamp;
    }
  }

  function renderDetails(actionType: string, details: Record<string, any>) {
    switch (actionType) {
      case "event_created":
        return (
          <div className="log-details">
            <span>Created event: {details.title}</span>
            {details.location && <span> at {details.location}</span>}
          </div>
        );
      
      case "event_edited":
        if (details.changes) {
          return (
            <div className="log-details">
              <span>Changed: </span>
              {Object.entries(details.changes).map(([field, change]: [string, any]) => (
                <div key={field} className="change-item">
                  <strong>{field}</strong>: <span className="old-value">{String(change.old)}</span> → <span className="new-value">{String(change.new)}</span>
                </div>
              ))}
            </div>
          );
        }
        return <div className="log-details">Edited event</div>;
      
      case "event_deleted":
        return (
          <div className="log-details">
            <span>Deleted event: {details.title}</span>
            {details.location && <span> at {details.location}</span>}
          </div>
        );
      
      case "qr_scanned":
        return (
          <div className="log-details">
            <span>Scanned: {details.student_name} ({details.student_prn})</span>
          </div>
        );
      
      case "ticket_deleted":
        return (
          <div className="log-details">
            <span>Deleted ticket for: {details.student_prn}</span>
          </div>
        );
      
      case "override_used":
        return (
          <div className="log-details">
            <span>Manual override for: {details.student_prn}</span>
            {details.reason && <span> - {details.reason}</span>}
          </div>
        );
      
      case "certificates_pushed":
        return (
          <div className="log-details certificate-details">
            <div className="cert-stat">
              <span className="stat-label">Total Eligible:</span>
              <span className="stat-value">{details.total_eligible || 0}</span>
            </div>
            <div className="cert-stat">
              <span className="stat-label">Certificates Issued:</span>
              <span className="stat-value success">{details.certificates_issued || 0}</span>
            </div>
            <div className="cert-stat">
              <span className="stat-label">Emails Sent:</span>
              <span className="stat-value success">{details.emails_sent || 0}</span>
            </div>
            {(details.emails_failed && details.emails_failed > 0) && (
              <div className="cert-stat">
                <span className="stat-label">Emails Failed:</span>
                <span className="stat-value error">{details.emails_failed}</span>
              </div>
            )}
          </div>
        );
      
      case "feedback_sent":
        return (
          <div className="log-details feedback-details">
            <div className="feedback-stat">
              <span className="stat-label">Total Attended:</span>
              <span className="stat-value">{details.total_attended || 0}</span>
            </div>
            <div className="feedback-stat">
              <span className="stat-label">Emails Sent:</span>
              <span className="stat-value success">{details.sent_count || 0}</span>
            </div>
            {(details.failed_count && details.failed_count > 0) && (
              <div className="feedback-stat">
                <span className="stat-label">Emails Failed:</span>
                <span className="stat-value error">{details.failed_count}</span>
              </div>
            )}
          </div>
        );
      
      case "role_certificates_pushed":
        return (
          <div className="log-details certificate-details">
            <div className="cert-stat">
              <span className="stat-label">Total Issued:</span>
              <span className="stat-value success">{details.total_issued || 0}</span>
            </div>
            <div className="cert-stat">
              <span className="stat-label">Emails Sent:</span>
              <span className="stat-value success">{details.total_emailed || 0}</span>
            </div>
            {(details.total_failed && details.total_failed > 0) && (
              <div className="cert-stat">
                <span className="stat-label">Emails Failed:</span>
                <span className="stat-value error">{details.total_failed}</span>
              </div>
            )}
            {details.roles && (
              <div className="cert-stat">
                <span className="stat-label">Roles:</span>
                <span className="stat-value">{Object.entries(details.roles).filter(([_, v]) => v).map(([k]) => k).join(', ')}</span>
              </div>
            )}
          </div>
        );
      
      case "certificates_resent":
        return (
          <div className="log-details certificate-details">
            <div className="cert-stat">
              <span className="stat-label">Total Attempted:</span>
              <span className="stat-value">{details.total_attempted || 0}</span>
            </div>
            <div className="cert-stat">
              <span className="stat-label">Emails Sent:</span>
              <span className="stat-value success">{details.emails_sent || 0}</span>
            </div>
            {(details.still_failed && details.still_failed > 0) && (
              <div className="cert-stat">
                <span className="stat-label">Still Failed:</span>
                <span className="stat-value error">{details.still_failed}</span>
              </div>
            )}
          </div>
        );
      
      case "volunteer_added":
        return (
          <div className="log-details">
            <span>Added volunteer: {details.volunteer_name} ({details.volunteer_email})</span>
          </div>
        );
      
      case "volunteer_removed":
        return (
          <div className="log-details">
            <span>Removed volunteer: {details.volunteer_name} ({details.volunteer_email})</span>
          </div>
        );
      
      default:
        return <div className="log-details">{JSON.stringify(details)}</div>;
    }
  }

  if (loading) {
    return (
      <div className="audit-logs">
        <h3>Activity Log</h3>
        <div className="loading-state">Loading activity...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="audit-logs">
        <h3>Activity Log</h3>
        <div className="error-state">{error}</div>
      </div>
    );
  }

  return (
    <div className="audit-logs">
      <h3>Activity Log</h3>
      {logs.length === 0 ? (
        <div className="empty-logs">No activity recorded yet</div>
      ) : (
        <div className="logs-list">
          {logs.map((log) => (
            <div key={log.id} className="log-entry">
              <div className="log-header">
                <span className={getActionBadgeClass(log.action_type)}>
                  {getActionLabel(log.action_type)}
                </span>
                <span className="log-time">{formatTimestamp(log.timestamp)}</span>
              </div>
              
              {renderDetails(log.action_type, log.details || {})}
              
              <div className="log-footer">
                <span className="log-user">
                  {log.user_email || "System"}
                </span>
                {log.ip_address && (
                  <span className="log-ip">{log.ip_address}</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
