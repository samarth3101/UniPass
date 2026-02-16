"use client";

import { useState, useEffect } from "react";
import api from "@/services/api";
import { toast } from "@/components/Toast";
import "./sentiment.scss";

interface SentimentBreakdown {
  positive: number;
  neutral: number;
  negative: number;
}

interface Theme {
  word: string;
  count: number;
}

interface EventSentimentAnalysis {
  total_feedback: number;
  overall_sentiment: string;
  sentiment_breakdown: SentimentBreakdown;
  avg_compound_score: number;
  avg_rating: number;
  recommendation_rate: number;
  top_positive_themes: Theme[];
  top_negative_themes: Theme[];
  insights: string[];
}

interface EventAnalysisData {
  event_id: number;
  event_name: string;
  analysis: EventSentimentAnalysis;
}

interface TrendData {
  event_id: number;
  event_name: string;
  event_date: string | null;
  sentiment_score: number;
  avg_rating: number;
  total_feedback: number;
}

export default function SentimentAnalysisPage() {
  const [selectedEventId, setSelectedEventId] = useState<number | null>(null);
  const [events, setEvents] = useState<any[]>([]);
  const [eventAnalysis, setEventAnalysis] = useState<EventAnalysisData | null>(null);
  const [trends, setTrends] = useState<TrendData[]>([]);
  const [avgSentiment, setAvgSentiment] = useState<number>(0);
  const [loading, setLoading] = useState(false);
  const [loadingTrends, setLoadingTrends] = useState(false);

  useEffect(() => {
    loadEvents();
    loadTrends();
  }, []);

  const loadEvents = async () => {
    try {
      const data = await api.get("/events");
      setEvents(data);
    } catch (err) {
      console.error("Failed to load events:", err);
    }
  };

  const loadTrends = async () => {
    setLoadingTrends(true);
    try {
      const data = await api.get("/feedback/sentiment-trends?limit=10");
      setTrends(data.trends || []);
      setAvgSentiment(data.avg_sentiment_across_events || 0);
    } catch (err: any) {
      console.error("Failed to load trends:", err);
      toast.error(err.message || "Failed to load sentiment trends");
    } finally {
      setLoadingTrends(false);
    }
  };

  const analyzEvent = async (eventId: number) => {
    setLoading(true);
    setSelectedEventId(eventId);
    try {
      const data = await api.get(`/feedback/event/${eventId}/sentiment-analysis`);
      setEventAnalysis(data);
    } catch (err: any) {
      console.error("Failed to analyze event:", err);
      toast.error(err.message || "Failed to analyze event sentiment");
      setEventAnalysis(null);
    } finally {
      setLoading(false);
    }
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case "positive":
        return "#10b981";
      case "negative":
        return "#ef4444";
      default:
        return "#6b7280";
    }
  };

  const getSentimentIcon = (sentiment: string) => {
    switch (sentiment) {
      case "positive":
        return "😊";
      case "negative":
        return "😞";
      default:
        return "😐";
    }
  };

  return (
    <div className="sentiment-page">
      <div className="page-header">
        <div>
          <h1>
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
              <path d="M8 10h.01M12 10h.01M16 10h.01"/>
            </svg>
            Sentiment Analysis
          </h1>
          <p>AI-powered NLP analysis of event feedback using VADER sentiment scoring</p>
        </div>
      </div>

      {/* Event Selector */}
      <div className="card">
        <h2>Select Event to Analyze</h2>
        <div className="event-selector">
          <select
            value={selectedEventId || ""}
            onChange={(e) => {
              const id = parseInt(e.target.value);
              if (!isNaN(id)) analyzEvent(id);
            }}
            disabled={loading}
          >
            <option value="">-- Select an event --</option>
            {events.map((event) => (
              <option key={event.id} value={event.id}>
                {event.name} ({new Date(event.start_time).toLocaleDateString()})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Analysis Results */}
      {loading && (
        <div className="card loading-state">
          <div className="spinner"></div>
          <p>Analyzing feedback with NLP...</p>
        </div>
      )}

      {eventAnalysis && !loading && (
        <>
          {/* Overview Card */}
          <div className="card analysis-overview">
            <h2>{eventAnalysis.event_name}</h2>
            
            <div className="overview-stats">
              <div className="stat-card">
                <div className="stat-icon" style={{ background: getSentimentColor(eventAnalysis.analysis.overall_sentiment) }}>
                  <span className="emoji">{getSentimentIcon(eventAnalysis.analysis.overall_sentiment)}</span>
                </div>
                <div className="stat-info">
                  <div className="stat-label">Overall Sentiment</div>
                  <div className="stat-value" style={{ color: getSentimentColor(eventAnalysis.analysis.overall_sentiment) }}>
                    {eventAnalysis.analysis.overall_sentiment.toUpperCase()}
                  </div>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-value">{eventAnalysis.analysis.avg_compound_score.toFixed(3)}</div>
                <div className="stat-label">Compound Score</div>
                <div className="stat-subtext">Range: -1 to +1</div>
              </div>

              <div className="stat-card">
                <div className="stat-value">{eventAnalysis.analysis.avg_rating.toFixed(2)}/5</div>
                <div className="stat-label">Avg Rating</div>
              </div>

              <div className="stat-card">
                <div className="stat-value">{eventAnalysis.analysis.recommendation_rate.toFixed(1)}%</div>
                <div className="stat-label">Would Recommend</div>
              </div>

              <div className="stat-card">
                <div className="stat-value">{eventAnalysis.analysis.total_feedback}</div>
                <div className="stat-label">Total Feedback</div>
              </div>
            </div>
          </div>

          {/* Sentiment Breakdown */}
          <div className="card">
            <h2>Sentiment Distribution</h2>
            <div className="sentiment-breakdown">
              <div className="sentiment-bar">
                <div className="bar-header">
                  <span>Positive</span>
                  <span>{eventAnalysis.analysis.sentiment_breakdown.positive}</span>
                </div>
                <div className="bar-container">
                  <div 
                    className="bar-fill positive"
                    style={{ 
                      width: `${(eventAnalysis.analysis.sentiment_breakdown.positive / eventAnalysis.analysis.total_feedback) * 100}%` 
                    }}
                  ></div>
                </div>
              </div>

              <div className="sentiment-bar">
                <div className="bar-header">
                  <span>Neutral</span>
                  <span>{eventAnalysis.analysis.sentiment_breakdown.neutral}</span>
                </div>
                <div className="bar-container">
                  <div 
                    className="bar-fill neutral"
                    style={{ 
                      width: `${(eventAnalysis.analysis.sentiment_breakdown.neutral / eventAnalysis.analysis.total_feedback) * 100}%` 
                    }}
                  ></div>
                </div>
              </div>

              <div className="sentiment-bar">
                <div className="bar-header">
                  <span>Negative</span>
                  <span>{eventAnalysis.analysis.sentiment_breakdown.negative}</span>
                </div>
                <div className="bar-container">
                  <div 
                    className="bar-fill negative"
                    style={{ 
                      width: `${(eventAnalysis.analysis.sentiment_breakdown.negative / eventAnalysis.analysis.total_feedback) * 100}%` 
                    }}
                  ></div>
                </div>
              </div>
            </div>
          </div>

          {/* Themes */}
          <div className="themes-grid">
            {eventAnalysis.analysis.top_positive_themes.length > 0 && (
              <div className="card themes-card positive">
                <h3>✨ Positive Themes</h3>
                <div className="themes-list">
                  {eventAnalysis.analysis.top_positive_themes.map((theme, idx) => (
                    <div key={idx} className="theme-item">
                      <span className="theme-word">{theme.word}</span>
                      <span className="theme-count">{theme.count} mentions</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {eventAnalysis.analysis.top_negative_themes.length > 0 && (
              <div className="card themes-card negative">
                <h3>🔧 Areas for Improvement</h3>
                <div className="themes-list">
                  {eventAnalysis.analysis.top_negative_themes.map((theme, idx) => (
                    <div key={idx} className="theme-item">
                      <span className="theme-word">{theme.word}</span>
                      <span className="theme-count">{theme.count} mentions</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Insights */}
          {eventAnalysis.analysis.insights.length > 0 && (
            <div className="card insights-card">
              <h2>💡 AI-Generated Insights</h2>
              <div className="insights-list">
                {eventAnalysis.analysis.insights.map((insight, idx) => (
                  <div key={idx} className="insight-item">
                    {insight}
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {/* Sentiment Trends */}
      <div className="card">
        <div className="card-header">
          <h2>Sentiment Trends</h2>
          {loadingTrends && <div className="spinner-small"></div>}
        </div>
        
        {avgSentiment !== 0 && (
          <div className="trend-summary">
            <span>Average sentiment across recent events:</span>
            <strong style={{ color: avgSentiment >= 0.05 ? '#10b981' : avgSentiment <= -0.05 ? '#ef4444' : '#6b7280' }}>
              {avgSentiment.toFixed(3)}
            </strong>
          </div>
        )}

        <div className="trends-table">
          <table>
            <thead>
              <tr>
                <th>Event</th>
                <th>Date</th>
                <th>Sentiment Score</th>
                <th>Avg Rating</th>
                <th>Feedback Count</th>
              </tr>
            </thead>
            <tbody>
              {trends
                .filter(t => t.total_feedback > 0)
                .map((trend) => (
                  <tr key={trend.event_id}>
                    <td className="event-name">{trend.event_name}</td>
                    <td>{trend.event_date ? new Date(trend.event_date).toLocaleDateString() : 'N/A'}</td>
                    <td>
                      <span 
                        className="sentiment-score"
                        style={{ 
                          color: trend.sentiment_score >= 0.05 ? '#10b981' : trend.sentiment_score <= -0.05 ? '#ef4444' : '#6b7280',
                          fontWeight: 600
                        }}
                      >
                        {trend.sentiment_score >= 0 ? '+' : ''}{trend.sentiment_score.toFixed(3)}
                      </span>
                    </td>
                    <td>{trend.avg_rating.toFixed(2)}/5</td>
                    <td>{trend.total_feedback}</td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
