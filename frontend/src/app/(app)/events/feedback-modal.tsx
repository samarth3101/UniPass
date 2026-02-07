"use client";

import { useState, useEffect } from "react";
import api from "@/services/api";
import { toast } from "@/components/Toast";
import "./feedback-modal.scss";

type FeedbackItem = {
  id: number;
  student_prn: string;
  overall_rating: number;
  content_quality: number;
  organization_rating: number;
  venue_rating: number;
  speaker_rating?: number;
  what_liked: string;
  what_improve: string;
  additional_comments: string;
  would_recommend: boolean;
  sentiment_score: number;
  submitted_at: string;
  student_name?: string;
};

type FeedbackSummary = {
  event_id: number;
  total_responses: number;
  avg_overall_rating: number;
  avg_content_quality: number;
  avg_organization: number;
  avg_venue: number;
  avg_speaker?: number;
  recommendation_percentage: number;
  sentiment_positive: number;
  sentiment_neutral: number;
  sentiment_negative: number;
};

type Props = {
  eventId: number;
  eventTitle: string;
  onClose: () => void;
};

export default function FeedbackModal({ eventId, eventTitle, onClose }: Props) {
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState<FeedbackSummary | null>(null);
  const [feedbackList, setFeedbackList] = useState<FeedbackItem[]>([]);
  const [activeTab, setActiveTab] = useState<"summary" | "responses">("summary");
  const [isInitialLoad, setIsInitialLoad] = useState(true);

  useEffect(() => {
    fetchFeedbackData();
  }, [eventId]);

  async function fetchFeedbackData() {
    try {
      setLoading(true);
      const [summaryData, responsesData] = await Promise.all([
        api.get(`/feedback/event/${eventId}/summary`),
        api.get(`/feedback/event/${eventId}`)
      ]);
      setSummary(summaryData);
      setFeedbackList(responsesData);
      
      // Show info toast only when manually refreshing (not on initial load)
      if (!isInitialLoad && summaryData.total_responses === 0) {
        toast.info("No feedback submitted yet. Check back later!");
      }
      
      // Mark initial load as complete
      if (isInitialLoad) {
        setIsInitialLoad(false);
      }
    } catch (error: any) {
      // Handle actual errors (event not found, access denied, etc.)
      console.error("Failed to fetch feedback:", error);
      const errorMessage = error.message || "Failed to load feedback data";
      toast.error(errorMessage);
      
      // Set empty state on error
      setSummary({
        event_id: eventId,
        total_responses: 0,
        avg_overall_rating: 0,
        avg_content_quality: 0,
        avg_organization: 0,
        avg_venue: 0,
        recommendation_percentage: 0,
        sentiment_positive: 0,
        sentiment_neutral: 0,
        sentiment_negative: 0,
      });
      setFeedbackList([]);
      
      // Mark initial load as complete even on error
      if (isInitialLoad) {
        setIsInitialLoad(false);
      }
    } finally {
      setLoading(false);
    }
  }

  function renderStars(rating: number) {
    return (
      <div className="star-display">
        {[1, 2, 3, 4, 5].map((star) => (
          <span
            key={star}
            className={`star ${star <= rating ? "filled" : ""}`}
          >
            ★
          </span>
        ))}
      </div>
    );
  }

  function getSentimentLabel(score: number) {
    if (score === 1) return { label: "Positive", className: "positive" };
    if (score === 0) return { label: "Neutral", className: "neutral" };
    return { label: "Negative", className: "negative" };
  }

  function formatDate(dateString: string) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + " " + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  if (loading) {
    return (
      <div className="modal-backdrop" onClick={onClose}>
        <div className="modal feedback-modal large" onClick={(e) => e.stopPropagation()}>
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Loading feedback...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!summary || summary.total_responses === 0) {
    return (
      <div className="modal-backdrop" onClick={onClose}>
        <div className="modal feedback-modal" onClick={(e) => e.stopPropagation()}>
          <button className="close-btn" onClick={onClose}>×</button>
          <h2>Event Feedback</h2>
          <p className="event-title">{eventTitle}</p>
          <div className="empty-state">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M21 11.5a8.38 8.38 0 01-.9 3.8 8.5 8.5 0 01-7.6 4.7 8.38 8.38 0 01-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 01-.9-3.8 8.5 8.5 0 014.7-7.6 8.38 8.38 0 013.8-.9h.5a8.48 8.48 0 018 8v.5z" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            <h3>No Feedback Yet</h3>
            <p>No students have submitted feedback for this event yet.</p>
            <p style={{ fontSize: "0.9rem", opacity: 0.7, marginTop: "0.5rem" }}>
              Feedback can only be submitted by attendees after the event.
            </p>
            <button 
              className="btn btn-primary" 
              style={{ marginTop: "1.5rem" }}
              onClick={() => {
                setLoading(true);
                fetchFeedbackData();
              }}
            >
              Refresh
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal feedback-modal xlarge" onClick={(e) => e.stopPropagation()}>
        <button className="close-btn" onClick={onClose}>×</button>
        
        <div className="modal-header">
          <div>
            <h2>Event Feedback</h2>
            <p className="event-title">{eventTitle}</p>
          </div>
          <button 
            className="btn btn-secondary btn-sm"
            onClick={() => {
              setLoading(true);
              fetchFeedbackData();
            }}
            style={{ marginLeft: "auto" }}
            title="Refresh feedback data"
          >
            ↻ Refresh
          </button>
        </div>

        <div className="feedback-tabs">
          <button
            className={`tab ${activeTab === "summary" ? "active" : ""}`}
            onClick={() => setActiveTab("summary")}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="3" width="7" height="7"/>
              <rect x="14" y="3" width="7" height="7"/>
              <rect x="14" y="14" width="7" height="7"/>
              <rect x="3" y="14" width="7" height="7"/>
            </svg>
            Summary
          </button>
          <button
            className={`tab ${activeTab === "responses" ? "active" : ""}`}
            onClick={() => setActiveTab("responses")}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            </svg>
            Responses ({summary.total_responses})
          </button>
        </div>

        {activeTab === "summary" && (
          <div className="feedback-summary-content">
            {loading && (
              <div className="loading-overlay">
                <div className="spinner"></div>
                <p>Refreshing feedback data...</p>
              </div>
            )}
            
            <div className="summary-grid">
              <div className="summary-card highlight">
                <div className="card-icon">
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                    <circle cx="9" cy="7" r="4"/>
                    <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                    <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                  </svg>
                </div>
                <div className="card-content">
                  <span className="card-label">Total Responses</span>
                  <span className="card-value">{summary.total_responses}</span>
                </div>
              </div>

              <div className="summary-card highlight">
                <div className="card-icon">
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"/>
                  </svg>
                </div>
                <div className="card-content">
                  <span className="card-label">Would Recommend</span>
                  <span className="card-value">{summary.recommendation_percentage.toFixed(1)}%</span>
                </div>
              </div>

              <div className="summary-card">
                <div className="card-content">
                  <span className="card-label">Overall Experience</span>
                  {renderStars(Math.round(summary.avg_overall_rating))}
                  <span className="card-rating">{summary.avg_overall_rating.toFixed(2)} / 5</span>
                </div>
              </div>

              <div className="summary-card">
                <div className="card-content">
                  <span className="card-label">Content Quality</span>
                  {renderStars(Math.round(summary.avg_content_quality))}
                  <span className="card-rating">{summary.avg_content_quality.toFixed(2)} / 5</span>
                </div>
              </div>

              <div className="summary-card">
                <div className="card-content">
                  <span className="card-label">Organization</span>
                  {renderStars(Math.round(summary.avg_organization))}
                  <span className="card-rating">{summary.avg_organization.toFixed(2)} / 5</span>
                </div>
              </div>

              <div className="summary-card">
                <div className="card-content">
                  <span className="card-label">Venue & Facilities</span>
                  {renderStars(Math.round(summary.avg_venue))}
                  <span className="card-rating">{summary.avg_venue.toFixed(2)} / 5</span>
                </div>
              </div>

              {summary.avg_speaker && summary.avg_speaker > 0 && (
                <div className="summary-card">
                  <div className="card-content">
                    <span className="card-label">Speaker/Presenter</span>
                    {renderStars(Math.round(summary.avg_speaker))}
                    <span className="card-rating">{summary.avg_speaker.toFixed(2)} / 5</span>
                  </div>
                </div>
              )}
            </div>

            <div className="sentiment-analysis">
              <h3>Sentiment Analysis</h3>
              <p style={{ fontSize: "0.9rem", opacity: 0.6, marginBottom: "1.5rem" }}>
                AI-powered sentiment analysis of feedback responses
              </p>
              <div className="sentiment-bars">
                <div className="sentiment-bar">
                  <div className="bar-label">
                    <span className="sentiment-icon positive">
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <circle cx="12" cy="12" r="10"/>
                        <path d="M8 14s1.5 2 4 2 4-2 4-2"/>
                        <line x1="9" y1="9" x2="9.01" y2="9"/>
                        <line x1="15" y1="9" x2="15.01" y2="9"/>
                      </svg>
                    </span>
                    <span>Positive</span>
                  </div>
                  <div className="bar-wrapper">
                    <div 
                      className="bar positive" 
                      style={{ 
                        width: summary.total_responses > 0 
                          ? `${(summary.sentiment_positive / summary.total_responses) * 100}%` 
                          : '0%' 
                      }}
                    ></div>
                  </div>
                  <span className="bar-count">{summary.sentiment_positive}</span>
                </div>

                <div className="sentiment-bar">
                  <div className="bar-label">
                    <span className="sentiment-icon neutral">
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <circle cx="12" cy="12" r="10"/>
                        <line x1="8" y1="15" x2="16" y2="15"/>
                        <line x1="9" y1="9" x2="9.01" y2="9"/>
                        <line x1="15" y1="9" x2="15.01" y2="9"/>
                      </svg>
                    </span>
                    <span>Neutral</span>
                  </div>
                  <div className="bar-wrapper">
                    <div 
                      className="bar neutral" 
                      style={{ 
                        width: summary.total_responses > 0 
                          ? `${(summary.sentiment_neutral / summary.total_responses) * 100}%` 
                          : '0%' 
                      }}
                    ></div>
                  </div>
                  <span className="bar-count">{summary.sentiment_neutral}</span>
                </div>

                <div className="sentiment-bar">
                  <div className="bar-label">
                    <span className="sentiment-icon negative">
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <circle cx="12" cy="12" r="10"/>
                        <path d="M16 16s-1.5-2-4-2-4 2-4 2"/>
                        <line x1="9" y1="9" x2="9.01" y2="9"/>
                        <line x1="15" y1="9" x2="15.01" y2="9"/>
                      </svg>
                    </span>
                    <span>Negative</span>
                  </div>
                  <div className="bar-wrapper">
                    <div 
                      className="bar negative" 
                      style={{ 
                        width: summary.total_responses > 0 
                          ? `${(summary.sentiment_negative / summary.total_responses) * 100}%` 
                          : '0%' 
                      }}
                    ></div>
                  </div>
                  <span className="bar-count">{summary.sentiment_negative}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === "responses" && (
          <div className="feedback-responses-content">
            {loading && (
              <div className="loading-overlay">
                <div className="spinner"></div>
                <p>Refreshing feedback data...</p>
              </div>
            )}
            
            {feedbackList.length === 0 && !loading && (
              <div className="empty-state">
                <p>No individual responses to display.</p>
              </div>
            )}
            
            {feedbackList.map((feedback) => {
              const sentiment = getSentimentLabel(feedback.sentiment_score);
              return (
                <div key={feedback.id} className="feedback-item">
                  <div className="feedback-header">
                    <div className="student-info">
                      <span className="student-name">{feedback.student_name || "Anonymous"}</span>
                      <span className="student-prn">{feedback.student_prn}</span>
                    </div>
                    <div className="feedback-meta">
                      <span className={`sentiment-badge ${sentiment.className}`}>
                        {sentiment.label}
                      </span>
                      <span className="submission-date">{formatDate(feedback.submitted_at)}</span>
                    </div>
                  </div>

                  <div className="feedback-ratings">
                    <div className="rating-item">
                      <span className="rating-label">Overall</span>
                      {renderStars(feedback.overall_rating)}
                    </div>
                    <div className="rating-item">
                      <span className="rating-label">Content</span>
                      {renderStars(feedback.content_quality)}
                    </div>
                    <div className="rating-item">
                      <span className="rating-label">Organization</span>
                      {renderStars(feedback.organization_rating)}
                    </div>
                    <div className="rating-item">
                      <span className="rating-label">Venue</span>
                      {renderStars(feedback.venue_rating)}
                    </div>
                    {feedback.speaker_rating && feedback.speaker_rating > 0 && (
                      <div className="rating-item">
                        <span className="rating-label">Speaker</span>
                        {renderStars(feedback.speaker_rating)}
                      </div>
                    )}
                  </div>

                  <div className="feedback-text">
                    <div className="text-section">
                      <h4>What they liked:</h4>
                      <p>{feedback.what_liked}</p>
                    </div>

                    {feedback.what_improve && (
                      <div className="text-section">
                        <h4>What could be improved:</h4>
                        <p>{feedback.what_improve}</p>
                      </div>
                    )}

                    {feedback.additional_comments && (
                      <div className="text-section">
                        <h4>Additional comments:</h4>
                        <p>{feedback.additional_comments}</p>
                      </div>
                    )}
                  </div>

                  <div className="feedback-footer">
                    {feedback.would_recommend ? (
                      <span className="recommend-badge yes">✓ Would recommend</span>
                    ) : (
                      <span className="recommend-badge no">✗ Would not recommend</span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
