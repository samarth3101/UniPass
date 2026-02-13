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
  }
};

export function getHelpContent(moduleId: string): HelpGuideContent | null {
  return helpGuideConfig[moduleId] || null;
}
