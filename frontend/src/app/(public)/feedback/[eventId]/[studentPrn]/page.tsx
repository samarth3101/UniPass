"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import "./feedback.scss";

interface FeedbackFormData {
  overall_rating: number;
  content_quality: number;
  organization_rating: number;
  venue_rating: number;
  speaker_rating?: number;
  what_liked: string;
  what_improve: string;
  additional_comments: string;
  would_recommend: boolean;
}

export default function FeedbackPage() {
  const params = useParams();
  const router = useRouter();
  const eventId = params.eventId as string;
  const studentPrn = params.studentPrn as string;

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [eventName, setEventName] = useState("");
  const [eligible, setEligible] = useState(false);

  const [formData, setFormData] = useState<FeedbackFormData>({
    overall_rating: 0,
    content_quality: 0,
    organization_rating: 0,
    venue_rating: 0,
    speaker_rating: undefined,
    what_liked: "",
    what_improve: "",
    additional_comments: "",
    would_recommend: true,
  });

  useEffect(() => {
    checkEligibility();
  }, []);

  const checkEligibility = async () => {
    try {
      // Use /api proxy for HTTPS compatibility
      const apiBase = typeof window !== 'undefined' && window.location.protocol === 'https:' ? '/api' : 'http://localhost:8000';
      const response = await fetch(
        `${apiBase}/feedback/check-eligibility/${eventId}/${studentPrn}`
      );

      if (!response.ok) {
        const data = await response.json();
        setError(data.detail || "You are not eligible to submit feedback for this event.");
        setLoading(false);
        return;
      }

      const data = await response.json();
      setEligible(data.eligible);
      setEventName(data.event_name);
      setLoading(false);
    } catch (err) {
      setError("Failed to verify eligibility. Please try again later.");
      setLoading(false);
    }
  };

  const handleRatingClick = (field: keyof FeedbackFormData, rating: number) => {
    setFormData((prev) => ({ ...prev, [field]: rating }));
  };

  const handleInputChange = (
    field: keyof FeedbackFormData,
    value: string | boolean
  ) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const validateForm = (): string | null => {
    if (formData.overall_rating === 0) return "Please rate your overall experience";
    if (formData.content_quality === 0) return "Please rate the content quality";
    if (formData.organization_rating === 0) return "Please rate the organization";
    if (formData.venue_rating === 0) return "Please rate the venue";
    if (!formData.what_liked.trim()) return "Please share what you liked";
    
    // Check text length limits
    if (formData.what_liked.length > 1000) return "What you liked must be within 1000 characters";
    if (formData.what_improve.length > 1000) return "Improvements must be within 1000 characters";
    if (formData.additional_comments.length > 1000) return "Additional comments must be within 1000 characters";
    
    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      // Use /api proxy for HTTPS compatibility
      const apiBase = typeof window !== 'undefined' && window.location.protocol === 'https:' ? '/api' : 'http://localhost:8000';
      const response = await fetch(
        `${apiBase}/feedback/submit`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            event_id: parseInt(eventId),
            student_prn: studentPrn,
            ...formData,
          }),
        }
      );

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Failed to submit feedback");
      }

      setSuccess(true);
    } catch (err: any) {
      setError(err.message || "Failed to submit feedback. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="feedback-container">
        <div className="feedback-card">
          <div className="loading">
            <div className="spinner"></div>
            <p>Verifying eligibility...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!eligible || error) {
    return (
      <div className="feedback-container">
        <div className="feedback-card">
          <div className="error-state">
            <svg
              className="error-icon"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <h2>Unable to Submit Feedback</h2>
            <p>{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (success) {
    return (
      <div className="feedback-container">
        <div className="feedback-card">
          <div className="success-state">
            <svg
              className="success-icon"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <h2>Thank You!</h2>
            <p>Your feedback has been submitted successfully.</p>
            <p className="success-message">
              We appreciate you taking the time to help us improve future events.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="feedback-container">
      <div className="feedback-card">
        <div className="feedback-header">
          <h1>Event Feedback</h1>
          <p className="event-name">{eventName}</p>
          <p className="subtitle">
            Your feedback helps us improve future events. This will take 2-3 minutes.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="feedback-form">
          {/* Overall Rating */}
          <div className="form-section">
            <label className="required">Overall Experience</label>
            <div className="star-rating">
              {[1, 2, 3, 4, 5].map((rating) => (
                <button
                  key={rating}
                  type="button"
                  className={`star ${
                    rating <= formData.overall_rating ? "active" : ""
                  }`}
                  onClick={() => handleRatingClick("overall_rating", rating)}
                  aria-label={`Rate ${rating} stars`}
                >
                  ★
                </button>
              ))}
            </div>
          </div>

          {/* Content Quality */}
          <div className="form-section">
            <label className="required">Content Quality</label>
            <div className="star-rating">
              {[1, 2, 3, 4, 5].map((rating) => (
                <button
                  key={rating}
                  type="button"
                  className={`star ${
                    rating <= formData.content_quality ? "active" : ""
                  }`}
                  onClick={() => handleRatingClick("content_quality", rating)}
                  aria-label={`Rate ${rating} stars`}
                >
                  ★
                </button>
              ))}
            </div>
          </div>

          {/* Organization Rating */}
          <div className="form-section">
            <label className="required">Organization & Management</label>
            <div className="star-rating">
              {[1, 2, 3, 4, 5].map((rating) => (
                <button
                  key={rating}
                  type="button"
                  className={`star ${
                    rating <= formData.organization_rating ? "active" : ""
                  }`}
                  onClick={() => handleRatingClick("organization_rating", rating)}
                  aria-label={`Rate ${rating} stars`}
                >
                  ★
                </button>
              ))}
            </div>
          </div>

          {/* Venue Rating */}
          <div className="form-section">
            <label className="required">Venue & Facilities</label>
            <div className="star-rating">
              {[1, 2, 3, 4, 5].map((rating) => (
                <button
                  key={rating}
                  type="button"
                  className={`star ${
                    rating <= formData.venue_rating ? "active" : ""
                  }`}
                  onClick={() => handleRatingClick("venue_rating", rating)}
                  aria-label={`Rate ${rating} stars`}
                >
                  ★
                </button>
              ))}
            </div>
          </div>

          {/* Speaker Rating (Optional) */}
          <div className="form-section">
            <label>Speaker/Presenter (if applicable)</label>
            <div className="star-rating">
              {[1, 2, 3, 4, 5].map((rating) => (
                <button
                  key={rating}
                  type="button"
                  className={`star ${
                    rating <= (formData.speaker_rating || 0) ? "active" : ""
                  }`}
                  onClick={() => handleRatingClick("speaker_rating", rating)}
                  aria-label={`Rate ${rating} stars`}
                >
                  ★
                </button>
              ))}
            </div>
          </div>

          {/* What Liked */}
          <div className="form-section">
            <label className="required">What did you like most?</label>
            <textarea
              value={formData.what_liked}
              onChange={(e) => handleInputChange("what_liked", e.target.value)}
              placeholder="Share what you enjoyed about this event..."
              rows={4}
              maxLength={1000}
              required
            />
            <span className="char-count">
              {formData.what_liked.length}/1000
            </span>
          </div>

          {/* What to Improve */}
          <div className="form-section">
            <label>What could be improved?</label>
            <textarea
              value={formData.what_improve}
              onChange={(e) => handleInputChange("what_improve", e.target.value)}
              placeholder="Share your suggestions for improvement..."
              rows={4}
              maxLength={1000}
            />
            <span className="char-count">
              {formData.what_improve.length}/1000
            </span>
          </div>

          {/* Additional Comments */}
          <div className="form-section">
            <label>Additional Comments</label>
            <textarea
              value={formData.additional_comments}
              onChange={(e) =>
                handleInputChange("additional_comments", e.target.value)
              }
              placeholder="Any other feedback you'd like to share..."
              rows={3}
              maxLength={1000}
            />
            <span className="char-count">
              {formData.additional_comments.length}/1000
            </span>
          </div>

          {/* Would Recommend */}
          <div className="form-section checkbox-section">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={formData.would_recommend}
                onChange={(e) =>
                  handleInputChange("would_recommend", e.target.checked)
                }
              />
              <span>I would recommend this event to others</span>
            </label>
          </div>

          {error && <div className="error-message">{error}</div>}

          <button
            type="submit"
            className="submit-button"
            disabled={submitting}
          >
            {submitting ? "Submitting..." : "Submit Feedback"}
          </button>
        </form>
      </div>
    </div>
  );
}
