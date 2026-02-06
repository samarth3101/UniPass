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
      default:
        return actionType;
    }
  }

  function formatTimestamp(timestamp: string): string {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return "Just now";
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    
    return date.toLocaleDateString() + " " + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
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
