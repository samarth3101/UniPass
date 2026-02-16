// Help Guide Configuration for Cortex AI Modules

export interface HelpSection {
  title: string;
  content: string | string[];
  type?: 'paragraph' | 'list' | 'ordered-list';
}

export interface HelpGuideContent {
  moduleId: string;
  moduleName: string;
  displayName: string;
  sections: HelpSection[];
}

export const helpGuideConfig: Record<string, HelpGuideContent> = {
  'descriptive-analytics': {
    moduleId: 'descriptive-analytics',
    moduleName: 'Descriptive Analytics',
    displayName: 'Cortex Descriptive Analytics Dashboard',
    sections: [
      {
        title: 'What is This?',
        content: 'Advanced analytics platform that provides comprehensive insights into attendance patterns, student engagement, and event participation across your institution.',
        type: 'paragraph'
      },
      {
        title: 'How It Works',
        content: [
          'Aggregates data from all attendance records and student participation',
          'Analyzes temporal patterns (hourly, daily, weekly trends)',
          'Segments insights by department, branch, and student cohorts',
          'Calculates engagement rates and participation metrics'
        ],
        type: 'list'
      },
      {
        title: 'Getting Started',
        content: [
          'Select Date Range: Choose preset periods (7/30 days) or custom dates',
          'Review Summary: Check high-level metrics like total events and engagement',
          'Analyze Departments: Compare participation rates across branches',
          'Study Time Patterns: Identify peak attendance hours and days',
          'Download Reports: Export data for further analysis'
        ],
        type: 'ordered-list'
      },
      {
        title: 'Key Metrics',
        content: [
          'Participation Rate: Percentage of active students attending events',
          'Engagement Rate: Overall student involvement in the system',
          'Avg Events Per Student: Mean number of events attended',
          'Peak Times: Hours and days with highest attendance',
          'Department Performance: Branch-wise comparative analysis'
        ],
        type: 'list'
      },
      {
        title: 'Best Practices',
        content: [
          'Review analytics weekly to track trends',
          'Compare metrics across different time periods',
          'Use department insights for targeted engagement',
          'Identify low-performing branches for intervention',
          'Export reports before semester reviews'
        ],
        type: 'list'
      }
    ]
  },
  
  'anomaly-detection': {
    moduleId: 'anomaly-detection',
    moduleName: 'Anomaly Detection',
    displayName: 'Cortex Anomaly Detection Dashboard',
    sections: [
      {
        title: 'What is This?',
        content: 'AI-powered system that automatically detects suspicious attendance patterns using machine learning algorithms to identify potential fraud or irregularities.',
        type: 'paragraph'
      },
      {
        title: 'How It Works',
        content: [
          'Isolation Forest Algorithm analyzes 8 different behavioral features',
          'Scans timing, frequency, and attendance patterns to identify outliers',
          'Assigns severity scores (HIGH/MEDIUM) based on anomaly strength',
          'Flags unusual patterns such as late scans, irregular timing, or suspicious frequency'
        ],
        type: 'list'
      },
      {
        title: 'Getting Started',
        content: [
          'Train the Model: Click "Train Model" to analyze existing attendance data',
          'Review Detections: Check the alerts list for flagged suspicious patterns',
          'Filter by Event: Use event ID filter for targeted anomaly analysis',
          'Investigate Anomalies: Click on alerts to view detailed feature breakdowns',
          'Retrain Regularly: Update the model with new data weekly or bi-weekly'
        ],
        type: 'ordered-list'
      },
      {
        title: 'Key Features Analyzed',
        content: [
          'Time After Start: How long after the event began was attendance recorded',
          'Scan Frequency: How often a student scans across different events',
          'Attendance Rate: Percentage of events attended by the student',
          'Admin Override: Patterns in manual scans vs. self-scan behavior',
          'Time Since Last Scan: Interval between consecutive attendance records',
          'Event Duration: Total length of the event when scan occurred',
          'Days Since Last Event: Gap between student attendance at events',
          'Late Scan Flag: Binary indicator for scans occurring unusually late'
        ],
        type: 'list'
      },
      {
        title: 'When to Retrain',
        content: [
          'New semester starts with different attendance patterns',
          '500+ new attendance records have been added to the system',
          'Detection accuracy seems off or producing false positives',
          'Major event policy changes or format modifications',
          'Weekly maintenance (recommended best practice)',
          'After bulk import of historical data'
        ],
        type: 'list'
      },
      {
        title: 'Understanding Severity',
        content: [
          'HIGH Severity: Strong anomaly signals requiring immediate review and investigation',
          'MEDIUM Severity: Moderate anomaly patterns worth monitoring and verification',
          'Anomaly Score: Ranges from -1 to 1, with values closer to -1 indicating stronger anomalies',
          'Review Threshold: Focus on HIGH severity first, then address MEDIUM cases'
        ],
        type: 'list'
      }
    ]
  },

  'prediction-model': {
    moduleId: 'prediction-model',
    moduleName: 'Prediction Model',
    displayName: 'Cortex Prediction Model Dashboard',
    sections: [
      {
        title: 'What is This?',
        content: 'Predictive analytics engine that forecasts future attendance patterns, student engagement trends, and event participation likelihood using machine learning.',
        type: 'paragraph'
      },
      {
        title: 'How It Works',
        content: [
          'Trained on historical attendance and engagement data',
          'Uses regression and classification models for forecasting',
          'Analyzes seasonal patterns and student behavior trends',
          'Provides confidence intervals for predictions'
        ],
        type: 'list'
      },
      {
        title: 'Getting Started',
        content: [
          'Train Prediction Model: Initialize with historical data',
          'Select Prediction Type: Choose attendance forecast or engagement prediction',
          'Set Parameters: Define time range and confidence level',
          'Review Predictions: Analyze forecast results and trends',
          'Export Forecasts: Download predictions for planning'
        ],
        type: 'ordered-list'
      },
      {
        title: 'Prediction Types',
        content: [
          'Attendance Forecasting: Predict expected turnout for upcoming events',
          'Engagement Trends: Forecast student participation over time',
          'Risk Assessment: Identify students at risk of low engagement',
          'Capacity Planning: Estimate resource needs based on predictions'
        ],
        type: 'list'
      },
      {
        title: 'Best Practices',
        content: [
          'Retrain monthly or when significant data changes occur',
          'Validate predictions against actual outcomes regularly',
          'Use predictions for event planning and resource allocation',
          'Combine with descriptive analytics for comprehensive insights',
          'Monitor prediction accuracy and adjust parameters as needed'
        ],
        type: 'list'
      }
    ]
  },

  'cortex-core': {
    moduleId: 'cortex-core',
    moduleName: 'Cortex CORE',
    displayName: 'Cortex CORE - Campus Organization & Record Engine',
    sections: [
      {
        title: 'What is Cortex CORE?',
        content: 'Cortex CORE (Campus Organization & Record Engine) is your Advanced Intelligence System for comprehensive participation management, featuring conflict detection, certificate verification, audit trails, and fraud detection.',
        type: 'paragraph'
      },
      {
        title: 'Core Features',
        content: [
          'Conflict Detection: Reconciles participation data with trust scoring',
          'Student Snapshots: Historical profile tracking with temporal queries',
          'Certificate System: SHA-256 verification with fraud detection',
          'Audit Trail: Complete change history, revocations, and invalidations',
          'Multi-Role Engine: Track multiple roles per student per event',
          'Transcript Generator: JSON and PDF participation transcripts'
        ],
        type: 'list'
      },
      {
        title: 'Cortex Exclusives',
        content: [
          'Attendance Invalidation: Mark fraudulent attendance while preserving records',
          'Data Correction: Apply retroactive corrections with full audit trail',
          'Fraud Detection: AI-powered pattern detection for suspicious activity',
          'Public Verification: Certificate validation available to everyone',
          'Complete API Reference: 21 comprehensive PS1 endpoints'
        ],
        type: 'list'
      },
      {
        title: 'How to Use Features',
        content: [
          'Conflict Detection: Click "Open Dashboard" to view reconciliation results',
          'Student Snapshots: Enter PRN and click "View History" to see timeline',
          'Certificate Verification: Enter Certificate ID and click "Verify" for validation',
          'Audit Trail: Provide Event ID and Student PRN, then click "View Audit"',
          'Transcript Generator: Enter Student PRN and choose "View JSON" or "Download PDF"',
          'Invalidation: Enter Attendance Record ID with reason to invalidate',
          'Fraud Detection: Enter Event ID and click "Run Fraud Detection"'
        ],
        type: 'ordered-list'
      },
      {
        title: 'Multi-Role System',
        content: [
          'PARTICIPANT: Regular event attendee',
          'VOLUNTEER: Helps organize and manage the event',
          'SPEAKER: Presents or delivers content at the event',
          'ORGANIZER: Plans and coordinates the event',
          'JUDGE: Evaluates competitions or judging panels',
          'MENTOR: Provides guidance and mentorship to participants'
        ],
        type: 'list'
      },
      {
        title: 'Understanding Trust Scores',
        content: 'Trust scores (0-100) indicate data quality and consistency. High scores (80+) mean clean records, medium scores (50-79) suggest minor conflicts, and low scores (below 50) indicate significant inconsistencies requiring review.',
        type: 'paragraph'
      },
      {
        title: 'Certificate Verification',
        content: [
          'Every certificate has a unique SHA-256 hash for verification',
          'Publicly accessible verification ensures authenticity',
          'Revoked certificates are clearly marked with warnings',
          'Fraud detection automatically flags suspicious certificates',
          'Complete audit trail shows all certificate lifecycle events'
        ],
        type: 'list'
      },
      {
        title: 'Fraud Detection Capabilities',
        content: [
          'Duplicate Certificates: Finds multiple certificates for same student/event',
          'Orphan Certificates: Identifies certificates without participation records',
          'Suspicious Timing: Detects rapid-fire scans and unusual patterns',
          'Premature Certificates: Flags certificates issued before events',
          'Revoked Certificate Usage: Tracks usage of revoked certificates',
          'Override Abuse: Detects excessive manual override patterns',
          'Bulk Anomalies: Identifies suspicious batch operations'
        ],
        type: 'list'
      },
      {
        title: 'Best Practices',
        content: [
          'Review conflict dashboard weekly to maintain data quality',
          'Run fraud detection after major events to catch anomalies early',
          'Use snapshots to track student progression over time',
          'Always provide detailed reasons when invalidating or correcting data',
          'Verify certificates periodically to ensure system integrity',
          'Export transcripts before semester reviews or student requests',
          'Check audit trails when investigating data discrepancies'
        ],
        type: 'list'
      },
      {
        title: 'API Access',
        content: 'All Cortex CORE features are available via REST API at /ps1/* endpoints. Visit localhost:8000/docs for complete API documentation with 21 comprehensive endpoints covering all functionality.',
        type: 'paragraph'
      }
    ]
  },

  'lecture-intelligence': {
    moduleId: 'lecture-intelligence',
    moduleName: 'Lecture Intelligence',
    displayName: 'Cortex LIE - Lecture Intelligence Engine',
    sections: [
      {
        title: 'What is Cortex LIE?',
        content: 'Cortex LIE (Lecture Intelligence Engine) automatically transcribes lecture audio recordings, extracts key insights, generates summaries, identifies important topics, and provides actionable recommendations using advanced AI.',
        type: 'paragraph'
      },
      {
        title: 'How It Works',
        content: [
          'Upload audio recordings from lectures or guest speaker sessions',
          'AI transcribes the complete audio to text with high accuracy',
          'Natural Language Processing identifies keywords and important topics',
          'Generates comprehensive summaries with key discussion points',
          'Extracts memorable quotes and technical highlights',
          'Provides follow-up action recommendations based on content'
        ],
        type: 'list'
      },
      {
        title: 'Getting Started',
        content: [
          'Enter Event ID: Specify which event the lecture recording belongs to',
          'Upload Audio: Select MP3, WAV, or M4A file (max 100MB)',
          'Wait for Processing: AI analyzes and transcribes the audio',
          'Review Report: Check transcript, keywords, summary, and insights',
          'Export or Share: Download reports for documentation or sharing'
        ],
        type: 'ordered-list'
      },
      {
        title: 'Supported Audio Formats',
        content: [
          'MP3: Standard compressed audio format',
          'WAV: Uncompressed high-quality audio',
          'M4A: Apple audio format (AAC codec)',
          'Maximum file size: 100MB per upload',
          'Recommended: Clear audio with minimal background noise'
        ],
        type: 'list'
      },
      {
        title: 'What You Get',
        content: [
          'Complete Transcript: Full text version of the lecture',
          'Keywords: Most important terms and concepts discussed',
          'Event Overview: High-level summary of the lecture content',
          'Key Topics: Main discussion points and subjects covered',
          'Important Quotes: Memorable statements from speakers',
          'Technical Highlights: Key technical or academic insights',
          'Engagement Summary: Analysis of audience interaction patterns',
          'Follow-up Actions: Recommended next steps based on content'
        ],
        type: 'list'
      },
      {
        title: 'Best Practices',
        content: [
          'Use quality recording equipment for better transcription accuracy',
          'Minimize background noise during recording',
          'Record closer to the speaker for clearer audio',
          'Upload within 24 hours for timely insights',
          'Review transcripts to catch any AI misinterpretations',
          'Share summaries with students who missed the lecture',
          'Archive reports for future reference and accreditation'
        ],
        type: 'list'
      },
      {
        title: 'Tips for Better Results',
        content: [
          'Single speaker recordings work better than multi-person discussions',
          'Clear enunciation improves transcription accuracy',
          'Technical jargon may require manual review',
          'Longer recordings (30+ minutes) provide richer insights',
          'Include Q&A sessions for engagement analysis'
        ],
        type: 'list'
      },
      {
        title: 'Processing Time',
        content: 'Processing time depends on audio length and server load. Typically, a 1-hour lecture takes 5-10 minutes to process. You\'ll see real-time status updates (processing, completed, or failed).',
        type: 'paragraph'
      }
    ]
  },

  'sentiment-analysis': {
    moduleId: 'sentiment-analysis',
    moduleName: 'Sentiment Analysis',
    displayName: 'Cortex Sentiment Analysis Dashboard',
    sections: [
      {
        title: 'What is This?',
        content: 'AI-powered sentiment analysis system that processes student feedback to understand emotional tone, identify trends, extract themes, and provide actionable insights for improving events and student satisfaction.',
        type: 'paragraph'
      },
      {
        title: 'How It Works',
        content: [
          'Collects feedback from students after events',
          'Uses Natural Language Processing to analyze text sentiment',
          'Classifies feedback as Positive, Neutral, or Negative',
          'Calculates compound sentiment scores (-1 to +1)',
          'Extracts common themes and keywords from feedback',
          'Generates trend analysis across multiple events'
        ],
        type: 'list'
      },
      {
        title: 'Getting Started',
        content: [
          'Select an Event: Choose from the dropdown to analyze specific event feedback',
          'Review Overall Sentiment: Check the summary metrics and ratings',
          'Examine Breakdown: See distribution of positive, neutral, and negative feedback',
          'Explore Themes: Identify common positive and negative topics',
          'Study Trends: Compare sentiment across recent events',
          'Take Action: Use insights to improve future events'
        ],
        type: 'ordered-list'
      },
      {
        title: 'Key Metrics Explained',
        content: [
          'Overall Sentiment: General emotional tone (Positive/Neutral/Negative)',
          'Compound Score: Numerical sentiment (-1 to +1, higher is better)',
          'Average Rating: Mean star rating from student feedback',
          'Recommendation Rate: Percentage of students who would recommend',
          'Sentiment Breakdown: Distribution across positive, neutral, negative',
          'Theme Analysis: Most frequently mentioned topics'
        ],
        type: 'list'
      },
      {
        title: 'Understanding Sentiment Scores',
        content: [
          'Positive (+0.05 to +1.0): Students enjoyed the event',
          'Neutral (-0.05 to +0.05): Mixed or balanced feedback',
          'Negative (-1.0 to -0.05): Areas needing improvement',
          'Compound Score > +0.5: Excellent reception',
          'Compound Score 0 to +0.5: Good with room for improvement',
          'Compound Score < 0: Significant concerns to address'
        ],
        type: 'list'
      },
      {
        title: 'Positive Themes',
        content: 'Highlight what students loved about the event. Use these themes to replicate success in future events, recognize what works well, and promote strengths in event planning.',
        type: 'paragraph'
      },
      {
        title: 'Negative Themes',
        content: 'Identify areas for improvement. Common issues might include timing, content delivery, venue problems, or organizational challenges. Address these systematically to enhance student satisfaction.',
        type: 'paragraph'
      },
      {
        title: 'Trend Analysis',
        content: [
          'Track sentiment evolution: See how feedback changes over time',
          'Compare events: Identify which events perform better',
          'Seasonal patterns: Understand timing impact on satisfaction',
          'Long-term improvement: Monitor whether changes are working',
          'Benchmark performance: Set standards based on historical data'
        ],
        type: 'list'
      },
      {
        title: 'Best Practices',
        content: [
          'Encourage students to provide detailed feedback',
          'Review sentiment within 48 hours of event completion',
          'Address negative themes promptly and visibly',
          'Share positive feedback with organizers and speakers',
          'Use trends to inform future event planning decisions',
          'Respond to student concerns to show you\'re listening',
          'Compare similar events to identify best practices'
        ],
        type: 'list'
      },
      {
        title: 'Taking Action',
        content: [
          'High Negative Sentiment: Conduct follow-up surveys, address specific concerns',
          'Mixed Feedback: Identify divisive aspects and gather more context',
          'Consistently Low Ratings: Consider major format or content changes',
          'Positive Trends: Document and replicate successful strategies',
          'Emerging Themes: Watch for new patterns requiring attention'
        ],
        type: 'list'
      }
    ]
  }
};

export function getHelpContent(moduleId: string): HelpGuideContent | null {
  return helpGuideConfig[moduleId] || null;
}
