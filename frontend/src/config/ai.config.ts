/**
 * AI Integration Configuration
 * Central configuration for all AI-related services
 */

export const AI_CONFIG = {
  // OpenAI Configuration
  openai: {
    apiKey: process.env.NEXT_PUBLIC_OPENAI_API_KEY || '',
    model: process.env.NEXT_PUBLIC_OPENAI_MODEL || 'gpt-4-turbo-preview',
    maxTokens: parseInt(process.env.NEXT_PUBLIC_OPENAI_MAX_TOKENS || '2000'),
    temperature: parseFloat(process.env.NEXT_PUBLIC_OPENAI_TEMPERATURE || '0.7'),
  },

  // AI Features Toggle
  features: {
    eventDescriptionGenerator: process.env.NEXT_PUBLIC_AI_EVENT_DESCRIPTION === 'true',
    emailContentGenerator: process.env.NEXT_PUBLIC_AI_EMAIL_GENERATOR === 'true',
    certificateCustomizer: process.env.NEXT_PUBLIC_AI_CERTIFICATE_DESIGNER === 'true',
    attendanceInsights: process.env.NEXT_PUBLIC_AI_ATTENDANCE_INSIGHTS === 'true',
    smartRecommendations: process.env.NEXT_PUBLIC_AI_RECOMMENDATIONS === 'true',
  },

  // Rate Limiting
  rateLimit: {
    maxRequestsPerMinute: parseInt(process.env.NEXT_PUBLIC_AI_RATE_LIMIT || '10'),
    retryAttempts: 3,
    retryDelay: 1000, // ms
  },

  // Caching
  cache: {
    enabled: process.env.NEXT_PUBLIC_AI_CACHE_ENABLED === 'true',
    ttl: parseInt(process.env.NEXT_PUBLIC_AI_CACHE_TTL || '3600'), // seconds
  },

  // Prompts Configuration
  prompts: {
    eventDescription: {
      system: 'You are a professional event organizer helping to create engaging event descriptions.',
      maxLength: 500,
    },
    emailContent: {
      system: 'You are a professional email copywriter creating engaging emails for event management.',
      maxLength: 1000,
    },
    attendanceInsights: {
      system: 'You are a data analyst providing insights on event attendance patterns.',
      maxLength: 800,
    },
  },
};

export type AIFeature = keyof typeof AI_CONFIG.features;

/**
 * Check if an AI feature is enabled
 */
export function isAIFeatureEnabled(feature: AIFeature): boolean {
  return AI_CONFIG.features[feature] || false;
}

/**
 * Get AI configuration with validation
 */
export function getAIConfig() {
  if (!AI_CONFIG.openai.apiKey) {
    console.warn('⚠️ OpenAI API key not configured. AI features will be disabled.');
  }
  return AI_CONFIG;
}
