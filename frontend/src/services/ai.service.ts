/**
 * AI Service - Handles all AI-related API calls
 * Supports OpenAI and other AI providers
 */

import { AI_CONFIG, isAIFeatureEnabled } from '@/config/ai.config';

// Types
export interface AIGenerateOptions {
  prompt: string;
  maxTokens?: number;
  temperature?: number;
  systemMessage?: string;
}

export interface AIResponse {
  success: boolean;
  content: string;
  usage?: {
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
  };
  error?: string;
}

// Rate limiting tracking
let requestCount = 0;
let lastResetTime = Date.now();

/**
 * Check and enforce rate limiting
 */
function checkRateLimit(): boolean {
  const now = Date.now();
  const oneMinute = 60 * 1000;

  // Reset counter if a minute has passed
  if (now - lastResetTime > oneMinute) {
    requestCount = 0;
    lastResetTime = now;
  }

  // Check if we've exceeded the limit
  if (requestCount >= AI_CONFIG.rateLimit.maxRequestsPerMinute) {
    return false;
  }

  requestCount++;
  return true;
}

/**
 * Generate text using AI
 */
export async function generateAIText(options: AIGenerateOptions): Promise<AIResponse> {
  try {
    // Check rate limit
    if (!checkRateLimit()) {
      return {
        success: false,
        content: '',
        error: 'Rate limit exceeded. Please try again in a moment.',
      };
    }

    // Check if API key is configured
    if (!AI_CONFIG.openai.apiKey) {
      return {
        success: false,
        content: '',
        error: 'AI service not configured. Please add your API key.',
      };
    }

    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${AI_CONFIG.openai.apiKey}`,
      },
      body: JSON.stringify({
        model: AI_CONFIG.openai.model,
        messages: [
          {
            role: 'system',
            content: options.systemMessage || 'You are a helpful assistant.',
          },
          {
            role: 'user',
            content: options.prompt,
          },
        ],
        max_tokens: options.maxTokens || AI_CONFIG.openai.maxTokens,
        temperature: options.temperature || AI_CONFIG.openai.temperature,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error?.message || 'AI request failed');
    }

    const data = await response.json();

    return {
      success: true,
      content: data.choices[0]?.message?.content || '',
      usage: {
        promptTokens: data.usage?.prompt_tokens || 0,
        completionTokens: data.usage?.completion_tokens || 0,
        totalTokens: data.usage?.total_tokens || 0,
      },
    };
  } catch (error: any) {
    console.error('AI generation error:', error);
    return {
      success: false,
      content: '',
      error: error.message || 'Failed to generate AI content',
    };
  }
}

/**
 * Generate event description
 */
export async function generateEventDescription(params: {
  title: string;
  location: string;
  date: string;
  targetAudience?: string;
  eventType?: string;
}): Promise<AIResponse> {
  if (!isAIFeatureEnabled('eventDescriptionGenerator')) {
    return {
      success: false,
      content: '',
      error: 'Event description generator is not enabled',
    };
  }

  const prompt = `Generate a compelling and professional event description for:
Event Title: ${params.title}
Location: ${params.location}
Date: ${params.date}
${params.targetAudience ? `Target Audience: ${params.targetAudience}` : ''}
${params.eventType ? `Event Type: ${params.eventType}` : ''}

The description should be engaging, informative, and suitable for promoting the event to potential attendees.
Keep it between 150-300 words.`;

  return generateAIText({
    prompt,
    systemMessage: AI_CONFIG.prompts.eventDescription.system,
    maxTokens: AI_CONFIG.prompts.eventDescription.maxLength,
  });
}

/**
 * Generate email content for event notifications
 */
export async function generateEmailContent(params: {
  eventTitle: string;
  eventDate: string;
  recipientType: 'registered' | 'attended' | 'reminder';
  additionalInfo?: string;
}): Promise<AIResponse> {
  if (!isAIFeatureEnabled('emailContentGenerator')) {
    return {
      success: false,
      content: '',
      error: 'Email content generator is not enabled',
    };
  }

  let prompt = '';
  switch (params.recipientType) {
    case 'registered':
      prompt = `Generate a professional confirmation email for someone who just registered for:
Event: ${params.eventTitle}
Date: ${params.eventDate}
${params.additionalInfo ? `Additional Info: ${params.additionalInfo}` : ''}

Include: Welcome message, event details, what to bring, and next steps.`;
      break;
    case 'attended':
      prompt = `Generate a thank you email for someone who attended:
Event: ${params.eventTitle}
Date: ${params.eventDate}

Include: Gratitude, event recap, feedback request, and information about upcoming events.`;
      break;
    case 'reminder':
      prompt = `Generate a reminder email for an upcoming event:
Event: ${params.eventTitle}
Date: ${params.eventDate}

Include: Friendly reminder, event details, what to expect, and contact information.`;
      break;
  }

  return generateAIText({
    prompt,
    systemMessage: AI_CONFIG.prompts.emailContent.system,
    maxTokens: AI_CONFIG.prompts.emailContent.maxLength,
  });
}

/**
 * Generate attendance insights and recommendations
 */
export async function generateAttendanceInsights(params: {
  totalRegistrations: number;
  totalAttended: number;
  attendanceRate: number;
  eventTitle: string;
  historicalData?: any;
}): Promise<AIResponse> {
  if (!isAIFeatureEnabled('attendanceInsights')) {
    return {
      success: false,
      content: '',
      error: 'Attendance insights feature is not enabled',
    };
  }

  const prompt = `Analyze this event attendance data and provide insights:
Event: ${params.eventTitle}
Total Registrations: ${params.totalRegistrations}
Total Attended: ${params.totalAttended}
Attendance Rate: ${params.attendanceRate}%

Provide:
1. Performance assessment (is this good/average/needs improvement?)
2. Possible reasons for the attendance rate
3. 3-5 actionable recommendations to improve attendance in future events
4. Any patterns or trends you notice

Keep the insights practical and specific.`;

  return generateAIText({
    prompt,
    systemMessage: AI_CONFIG.prompts.attendanceInsights.system,
    maxTokens: AI_CONFIG.prompts.attendanceInsights.maxLength,
  });
}

/**
 * Smart event recommendations based on user behavior
 */
export async function generateEventRecommendations(params: {
  userHistory: string[];
  upcomingEvents: string[];
}): Promise<AIResponse> {
  if (!isAIFeatureEnabled('smartRecommendations')) {
    return {
      success: false,
      content: '',
      error: 'Smart recommendations feature is not enabled',
    };
  }

  const prompt = `Based on user's event attendance history: ${params.userHistory.join(', ')}
And these upcoming events: ${params.upcomingEvents.join(', ')}

Recommend 3 events that would best match their interests. For each recommendation, explain why.`;

  return generateAIText({
    prompt,
    systemMessage: 'You are an event recommendation expert.',
    maxTokens: 500,
  });
}
