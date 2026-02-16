"use client";

import { useState, useEffect } from "react";
import api from "@/services/api";
import { toast } from "@/components/Toast";
import { isAdmin } from "@/lib/auth";
import "./volunteers.scss";

type Volunteer = {
  id: number;
  event_id: number;
  name: string;
  email: string;
  added_at: string;
  certificate_sent: boolean;
  certificate_sent_at: string | null;
};

type Event = {
  id: number;
  title: string;
};

export default function VolunteersPage() {
  const [events, setEvents] = useState<Event[]>([]);
  const [selectedEventId, setSelectedEventId] = useState<number | null>(null);
  const [volunteers, setVolunteers] = useState<Volunteer[]>([]);
  const [loading, setLoading] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newVolunteer, setNewVolunteer] = useState({ name: "", email: "" });
  const userIsAdmin = isAdmin();

  useEffect(() => {
    loadEvents();
  }, []);

  useEffect(() => {
    if (selectedEventId) {
      loadVolunteers();
    }
  }, [selectedEventId]);

  async function loadEvents() {
    try {
      const response = await api.get("/events/?skip=0&limit=100");
      const data = response.events || response;
      setEvents(data);
      if (data.length > 0) {
        setSelectedEventId(data[0].id);
      }
    } catch (error) {
      console.error("Error loading events:", error);
      toast.error("Failed to load events");
    }
  }

  async function loadVolunteers() {
    if (!selectedEventId) return;

    setLoading(true);
    try {
      const data = await api.get(`/volunteers/${selectedEventId}`);
      setVolunteers(data.volunteers || []);
    } catch (error: any) {
      console.error("Error loading volunteers:", error);
      if (error.response?.status !== 403) {
        toast.error("Failed to load volunteers");
      }
    } finally {
      setLoading(false);
    }
  }

  async function handleAddVolunteer(e: React.FormEvent) {
    e.preventDefault();

    if (!newVolunteer.name || !newVolunteer.email) {
      toast.error("Please fill in all fields");
      return;
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(newVolunteer.email)) {
      toast.error("Please enter a valid email address");
      return;
    }

    setLoading(true);
    try {
      await api.post(`/volunteers/${selectedEventId}`, newVolunteer);
      toast.success("Volunteer added successfully!");
      setNewVolunteer({ name: "", email: "" });
      setShowAddForm(false);
      loadVolunteers();
    } catch (error: any) {
      console.error("Error adding volunteer:", error);
      toast.error(error.response?.data?.detail || "Failed to add volunteer");
    } finally {
      setLoading(false);
    }
  }

  async function handleDeleteVolunteer(volunteerId: number, volunteerName: string) {
    if (!confirm(`Remove ${volunteerName} from volunteers?`)) return;

    setLoading(true);
    try {
      await api.delete(`/volunteers/${volunteerId}`);
      toast.success(`${volunteerName} removed successfully`);
      loadVolunteers();
    } catch (error: any) {
      console.error("Error removing volunteer:", error);
      toast.error(error.response?.data?.detail || "Failed to remove volunteer");
    } finally {
      setLoading(false);
    }
  }

  async function handleResendCertificate(volunteerId: number, volunteerName: string) {
    if (!confirm(`Resend certificate to ${volunteerName}?`)) return;

    setLoading(true);
    try {
      await api.post(`/volunteers/${volunteerId}/resend-certificate`);
      toast.success(`Certificate resent to ${volunteerName}`);
      loadVolunteers();
    } catch (error: any) {
      console.error("Error resending certificate:", error);
      toast.error(error.response?.data?.detail || "Failed to resend certificate");
    } finally {
      setLoading(false);
    }
  }

  const selectedEvent = events.find(e => e.id === selectedEventId);

  return (
    <div className="volunteers-page">
      <div className="page-header">
        <div>
          <h1>❤️ Volunteer Management</h1>
          <p className="subtitle">Manage event volunteers and send certificates</p>
        </div>
        
        {selectedEventId && (
          <button 
            className="btn btn-primary"
            onClick={() => setShowAddForm(!showAddForm)}
            disabled={loading}
          >
            {showAddForm ? "Cancel" : "+ Add Volunteer"}
          </button>
        )}
      </div>

      <div className="event-selector">
        <label htmlFor="event-select">Select Event:</label>
        <select
          id="event-select"
          value={selectedEventId || ""}
          onChange={(e) => setSelectedEventId(Number(e.target.value))}
          disabled={loading}
        >
          {events.map(event => (
            <option key={event.id} value={event.id}>
              {event.title}
            </option>
          ))}
        </select>
      </div>

      {showAddForm && selectedEventId && (
        <div className="add-volunteer-form">
          <h3>Add New Volunteer</h3>
          <form onSubmit={handleAddVolunteer}>
            <div className="form-row">
              <div className="form-group">
                <label>Name *</label>
                <input
                  type="text"
                  value={newVolunteer.name}
                  onChange={(e) => setNewVolunteer({ ...newVolunteer, name: e.target.value })}
                  placeholder="John Doe"
                  required
                />
              </div>
              <div className="form-group">
                <label>Email *</label>
                <input
                  type="email"
                  value={newVolunteer.email}
                  onChange={(e) => setNewVolunteer({ ...newVolunteer, email: e.target.value })}
                  placeholder="john@example.com"
                  required
                />
              </div>
            </div>
            <div className="form-actions">
              <button type="submit" className="btn btn-primary" disabled={loading}>
                {loading ? "Adding..." : "Add Volunteer"}
              </button>
            </div>
          </form>
        </div>
      )}

      {loading && volunteers.length === 0 ? (
        <div className="loading-state">Loading volunteers...</div>
      ) : volunteers.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">❤️</div>
          <h3>No Volunteers Yet</h3>
          <p>Add volunteers who helped organize this event to send them appreciation certificates.</p>
          {selectedEventId && (
            <button className="btn btn-primary" onClick={() => setShowAddForm(true)}>
              Add First Volunteer
            </button>
          )}
        </div>
      ) : (
        <div className="volunteers-table">
          <div className="table-header">
            <h3>{volunteers.length} Volunteer{volunteers.length !== 1 ? 's' : ''}</h3>
            {selectedEvent && <p className="event-name">{selectedEvent.title}</p>}
          </div>
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Added On</th>
                <th>Certificate</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {volunteers.map((volunteer) => (
                <tr key={volunteer.id}>
                  <td className="name-cell">{volunteer.name}</td>
                  <td className="email-cell">{volunteer.email}</td>
                  <td className="date-cell">
                    {new Date(volunteer.added_at).toLocaleDateString()}
                  </td>
                  <td className="status-cell">
                    {volunteer.certificate_sent ? (
                      <span className="badge badge-success">✓ Sent</span>
                    ) : (
                      <span className="badge badge-pending">Pending</span>
                    )}
                  </td>
                  <td className="actions-cell">
                    {volunteer.certificate_sent && (
                      <button
                        className="btn btn-sm btn-resend"
                        onClick={() => handleResendCertificate(volunteer.id, volunteer.name)}
                        disabled={loading}
                      >
                        📧 Resend
                      </button>
                    )}
                    <button
                      className="btn btn-sm btn-delete"
                      onClick={() => handleDeleteVolunteer(volunteer.id, volunteer.name)}
                      disabled={loading}
                    >
                      🗑️ Remove
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="help-section">
        <h4>💡 About Volunteers</h4>
        <ul>
          <li>Volunteers are external helpers who don't have student accounts</li>
          <li>They receive special appreciation certificates via email</li>
          <li>Use "Push Certificates" in Event Control Center to send certificates to all roles</li>
          <li>Certificates are automatically sent when you push with "Volunteer" role selected</li>
        </ul>
      </div>
    </div>
  );
}
