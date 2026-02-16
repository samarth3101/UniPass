'use client';

import { useState } from 'react';
import './verify.scss';

interface VerificationResult {
  authentic: boolean;
  certificate_id: string;
  student_prn?: string;
  student_name?: string;
  event_title?: string;
  event_date?: string;
  issued_at?: string;
  revoked: boolean;
  revocation_reason?: string;
  verification_hash_valid: boolean;
  message: string;
}

export default function VerifyCertificatePage() {
  const [certificateId, setCertificateId] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<VerificationResult | null>(null);
  const [error, setError] = useState('');

  const handleVerify = async () => {
    if (!certificateId.trim()) {
      setError('Please enter a certificate ID');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await fetch(
        `/api/ps1/verify/certificate/${certificateId.trim()}`
      );
      
      if (!response.ok) {
        throw new Error('Verification failed');
      }

      const data: VerificationResult = await response.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message || 'Failed to verify certificate');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleVerify();
    }
  };

  return (
    <div className="verify-page">
      <div className="verify-container">
        <div className="verify-header">
          <div className="shield-icon">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
              <path d="M9 12l2 2 4-4" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <h1>Certificate Verification</h1>
          <p className="subtitle">
            Verify the authenticity of UniPass event certificates
          </p>
        </div>

        <div className="verify-input-section">
          <label htmlFor="cert-id">Certificate ID</label>
          <input
            id="cert-id"
            type="text"
            placeholder="CERT-XXXXXXXXXXXX"
            value={certificateId}
            onChange={(e) => setCertificateId(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={loading}
          />
          <button 
            onClick={handleVerify}
            disabled={loading || !certificateId.trim()}
            className="verify-btn"
          >
            {loading ? (
              <>
                <span className="spinner"></span>
                Verifying...
              </>
            ) : (
              <>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="11" cy="11" r="8"/>
                  <path d="m21 21-4.35-4.35"/>
                </svg>
                Verify Certificate
              </>
            )}
          </button>
        </div>

        {error && (
          <div className="error-message">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="15" y1="9" x2="9" y2="15"/>
              <line x1="9" y1="9" x2="15" y2="15"/>
            </svg>
            {error}
          </div>
        )}

        {result && (
          <div className={`result-card ${result.revoked ? 'revoked' : result.authentic ? 'authentic' : 'invalid'}`}>
            <div className="result-header">
              <div className="result-icon">
                {result.authentic && !result.revoked ? (
                  <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                    <path d="M9 12l2 2 4-4" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                ) : result.revoked ? (
                  <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                    <line x1="15" y1="9" x2="9" y2="15"/>
                    <line x1="9" y1="9" x2="15" y2="15"/>
                  </svg>
                ) : (
                  <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="10"/>
                    <line x1="15" y1="9" x2="9" y2="15"/>
                    <line x1="9" y1="9" x2="15" y2="15"/>
                  </svg>
                )}
              </div>
              <div className="result-title-section">
                <h2>
                  {result.revoked 
                    ? 'Certificate Revoked' 
                    : result.authentic 
                      ? 'Certificate Authentic' 
                      : 'Certificate Invalid'}
                </h2>
                <span className={`status-badge ${result.revoked ? 'revoked-badge' : result.authentic ? 'valid-badge' : 'invalid-badge'}`}>
                  {result.revoked ? 'REVOKED' : result.authentic ? 'VALID' : 'INVALID'}
                </span>
              </div>
              <p className="result-message">{result.message}</p>
            </div>

            {result.revoked && (
              <div className="revocation-warning">
                <div className="warning-header">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
                    <path d="M12 9v4"/>
                    <path d="M12 17h.01"/>
                  </svg>
                  <strong>This certificate has been revoked</strong>
                </div>
                <div className="revocation-details">
                  <div className="detail-row">
                    <span className="label">Reason:</span>
                    <span className="value">{result.revocation_reason || 'No reason provided'}</span>
                  </div>
                  <p className="revocation-note">
                    This certificate is no longer valid and should not be accepted as proof of participation.
                  </p>
                </div>
              </div>
            )}

            {result.authentic && !result.revoked && (
              <div className="result-details">
                <div className="detail-row">
                  <span className="label">Certificate ID:</span>
                  <span className="value">{result.certificate_id}</span>
                </div>
                {result.student_name && (
                  <div className="detail-row">
                    <span className="label">Student Name:</span>
                    <span className="value">{result.student_name}</span>
                  </div>
                )}
                {result.student_prn && (
                  <div className="detail-row">
                    <span className="label">Student PRN:</span>
                    <span className="value">{result.student_prn}</span>
                  </div>
                )}
                {result.event_title && (
                  <div className="detail-row">
                    <span className="label">Event:</span>
                    <span className="value">{result.event_title}</span>
                  </div>
                )}
                {result.event_date && (
                  <div className="detail-row">
                    <span className="label">Event Date:</span>
                    <span className="value">
                      {new Date(result.event_date).toLocaleDateString('en-US', {
                        month: 'long',
                        day: 'numeric',
                        year: 'numeric'
                      })}
                    </span>
                  </div>
                )}
                {result.issued_at && (
                  <div className="detail-row">
                    <span className="label">Issued On:</span>
                    <span className="value">
                      {new Date(result.issued_at).toLocaleDateString('en-US', {
                        month: 'long',
                        day: 'numeric',
                        year: 'numeric'
                      })}
                    </span>
                  </div>
                )}
              </div>
            )}

            <div className="verification-footer">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"/>
                <path d="M12 6v6l4 2"/>
              </svg>
              <span>Verified on {new Date().toLocaleString()}</span>
            </div>
          </div>
        )}

        <div className="help-section">
          <h3>How to Verify</h3>
          <ol>
            <li>Locate the certificate ID (format: CERT-XXXXXXXXXXXX)</li>
            <li>Enter the certificate ID in the field above</li>
            <li>Click "Verify Certificate" to check authenticity</li>
            <li>View the verification results</li>
          </ol>
        </div>
      </div>
    </div>
  );
}
