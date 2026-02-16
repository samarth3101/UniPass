/**
 * Certificate Push Modal Component
 * Allows admins/organizers to select which roles should receive certificates
 */
'use client';

import { useState, useEffect } from 'react';
import api from '@/services/api';
import { toast } from '@/components/Toast';
import './certificate-push-modal.scss';

type CertificateStats = {
  attendees: number;
  organizers: number;
  scanners: number;
  volunteers: number;
};

type Props = {
  eventId: number;
  eventTitle: string;
  onClose: () => void;
  onSuccess: () => void;
};

export default function CertificatePushModal({ eventId, eventTitle, onClose, onSuccess }: Props) {
  const [loading, setLoading] = useState(false);
  const [resending, setResending] = useState(false);
  const [stats, setStats] = useState<CertificateStats | null>(null);
  const [selectedRoles, setSelectedRoles] = useState({
    attendee: true,
    organizer: false,
    scanner: false,
    volunteer: false,
  });

  useEffect(() => {
    loadStats();
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = '';
    };
  }, []);

  async function loadStats() {
    try {
      const data = await api.get(`/certificates/event/${eventId}/role-stats`);
      // Ensure all stats have default values of 0 if null/undefined
      setStats({
        attendees: data.attendees || 0,
        organizers: data.organizers || 0,
        scanners: data.scanners || 0,
        volunteers: data.volunteers || 0,
      });
    } catch (error) {
      console.error('Error loading certificate stats:', error);
      toast.error('Failed to load certificate statistics');
      // Set all stats to 0 on error
      setStats({
        attendees: 0,
        organizers: 0,
        scanners: 0,
        volunteers: 0,
      });
    }
  }

  function toggleRole(role: keyof typeof selectedRoles) {
    setSelectedRoles(prev => ({ ...prev, [role]: !prev[role] }));
  }

  async function handlePushCertificates() {
    const selectedCount = Object.values(selectedRoles).filter(Boolean).length;

    if (selectedCount === 0) {
      toast.error('Please select at least one role');
      return;
    }

    const totalCertificates = Object.entries(selectedRoles)
      .filter(([_, selected]) => selected)
      .reduce((sum, [role, _]) => {
        const key = role as keyof typeof selectedRoles;
        const statKey = (key === 'attendee' ? 'attendees' : key + 's') as keyof CertificateStats;
        return sum + (stats?.[statKey] || 0);
      }, 0);

    if (totalCertificates === 0) {
      toast.info('No eligible recipients for selected roles');
      return;
    }

    if (!confirm(`Send certificates to ${totalCertificates} recipient(s) across ${selectedCount} role(s)?`)) {
      return;
    }

    setLoading(true);
    try {
      // Convert role format: {attendee: true, organizer: false} -> {attendees: true, organizers: false}
      const rolesPayload = {
        attendees: selectedRoles.attendee,
        organizers: selectedRoles.organizer,
        scanners: selectedRoles.scanner,
        volunteers: selectedRoles.volunteer,
      };

      const result = await api.post(`/certificates/event/${eventId}/push-by-roles`, rolesPayload);

      if (result.success) {
        toast.success(`Successfully sent ${result.total_emailed} certificates!`);
        onSuccess();
        onClose();
      }
    } catch (error: any) {
      console.error('Error pushing certificates:', error);
      toast.error(error.response?.data?.detail || 'Failed to push certificates');
    } finally {
      setLoading(false);
    }
  }

  async function handleResendFailed() {
    if (!confirm('Resend certificate emails that previously failed to send?')) {
      return;
    }

    setResending(true);
    try {
      const result = await api.post(`/certificates/event/${eventId}/resend-failed`);
      console.log('Resend failed certificates result:', result);

      if (result && result.success) {
        const resent = result.resent ?? 0;
        const stillFailed = result.still_failed ?? 0;
        const totalAttempted = result.total_attempted ?? 0;

        if (resent === 0) {
          toast.info('No failed certificates to resend');
        } else if (stillFailed === 0) {
          toast.success(`Successfully resent ${resent} certificate email(s)!`);
        } else {
          toast.warning(
            `Resent ${resent} certificate(s), but ${stillFailed} still failed. ` +
            `Check SMTP configuration or network connection.`
          );
        }
        
        // Reload stats to reflect updates
        await loadStats();
      } else {
        toast.error('Unexpected response from server');
      }
    } catch (error: any) {
      console.error('Error resending certificates:', error);
      toast.error(error.response?.data?.detail || error.message || 'Failed to resend certificates');
    } finally {
      setResending(false);
    }
  }

  if (!stats) {
    return (
      <div className="modal-backdrop" onClick={onClose}>
        <div className="certificate-push-modal" onClick={(e) => e.stopPropagation()}>
          <div className="loading-spinner">Loading...</div>
        </div>
      </div>
    );
  }

  const totalSelected = Object.entries(selectedRoles)
    .filter(([_, selected]) => selected)
    .reduce((sum, [role, _]) => {
      const key = role as keyof typeof selectedRoles;
      const statKey = (key === 'attendee' ? 'attendees' : key + 's') as keyof CertificateStats;
      return sum + (stats[statKey] || 0);
    }, 0);

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="certificate-push-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ display: 'inline-block', verticalAlign: 'middle', marginRight: '8px' }}>
              <path d="M22 10v6M2 10l10-5 10 5-10 5z"/>
              <path d="M6 12v5c3 3 9 3 12 0v-5"/>
            </svg>
            Push Certificates
          </h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <div className="modal-body">
          <p className="event-title">{eventTitle}</p>
          <p className="instruction">Select roles to receive certificates:</p>

          <div className="role-selection">
            <div className={`role-card ${selectedRoles.attendee ? 'selected' : ''} attendee`} onClick={() => toggleRole('attendee')}>
              <input 
                type="checkbox" 
                checked={selectedRoles.attendee}
                onChange={() => toggleRole('attendee')}
              />
              <div className="role-content">
                <div className="role-icon">
                  <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M22 10v6M2 10l10-5 10 5-10 5z"/>
                    <path d="M6 12v5c3 3 9 3 12 0v-5"/>
                  </svg>
                </div>
                <div className="role-info">
                  <h3>Attendees</h3>
                  <p className="count">{stats?.attendees || 0} eligible</p>
                  <p className="description">Students who attended the event</p>
                </div>
              </div>
            </div>

            <div className={`role-card ${selectedRoles.organizer ? 'selected' : ''} organizer`} onClick={() => toggleRole('organizer')}>
              <input 
                type="checkbox" 
                checked={selectedRoles.organizer}
                onChange={() => toggleRole('organizer')}
              />
              <div className="role-content">
                <div className="role-icon">
                  <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                    <circle cx="12" cy="7" r="4"/>
                    <path d="M12 11v10"/>
                    <path d="M8 14l4 3 4-3"/>
                  </svg>
                </div>
                <div className="role-info">
                  <h3>Organizers</h3>
                  <p className="count">{stats?.organizers || 0} eligible</p>
                  <p className="description">Event organizers and creators</p>
                </div>
              </div>
            </div>

            <div className={`role-card ${selectedRoles.scanner ? 'selected' : ''} scanner`} onClick={() => toggleRole('scanner')}>
              <input 
                type="checkbox" 
                checked={selectedRoles.scanner}
                onChange={() => toggleRole('scanner')}
              />
              <div className="role-content">
                <div className="role-icon">
                  <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="3" y="3" width="18" height="18" rx="2"/>
                    <path d="M9 3v18"/>
                    <path d="M15 3v18"/>
                    <path d="M3 9h18"/>
                    <path d="M3 15h18"/>
                  </svg>
                </div>
                <div className="role-info">
                  <h3>Scanners</h3>
                  <p className="count">{stats?.scanners || 0} eligible</p>
                  <p className="description">Team members who scanned attendees</p>
                </div>
              </div>
            </div>

            <div className={`role-card ${selectedRoles.volunteer ? 'selected' : ''} volunteer`} onClick={() => toggleRole('volunteer')}>
              <input 
                type="checkbox" 
                checked={selectedRoles.volunteer}
                onChange={() => toggleRole('volunteer')}
              />
              <div className="role-content">
                <div className="role-icon">
                  <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
                  </svg>
                </div>
                <div className="role-info">
                  <h3>Volunteers</h3>
                  <p className="count">{stats?.volunteers || 0} eligible</p>
                  <p className="description">Volunteers added to this event</p>
                </div>
              </div>
            </div>
          </div>

          <div className="summary">
            <div className="summary-count">
              {totalSelected} total recipient{totalSelected !== 1 ? 's' : ''}
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose} disabled={loading || resending}>
            Cancel
          </button>
          <button 
            className="btn btn-warning" 
            onClick={handleResendFailed}
            disabled={loading || resending}
            style={{ marginLeft: 'auto', marginRight: '8px' }}
          >
            {resending ? 'Resending...' : 'Resend Failed'}
          </button>
          <button 
            className="btn btn-primary" 
            onClick={handlePushCertificates}
            disabled={loading || resending || totalSelected === 0}
          >
            {loading ? 'Sending...' : `Send ${totalSelected} Certificate${totalSelected !== 1 ? 's' : ''}`}
          </button>
        </div>
      </div>
    </div>
  );
}
