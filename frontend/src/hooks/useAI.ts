/**
 * React Hook for AI Features
 * Provides easy-to-use AI functionality in React components
 */

import { useState } from 'react';
import {
  generateEventDescription,
  generateEmailContent,
  generateAttendanceInsights,
  generateEventRecommendations,
  AIResponse,
} from '@/services/ai.service';
import { isAIFeatureEnabled, AIFeature } from '@/config/ai.config';

export interface UseAIState {
  loading: boolean;
  error: string | null;
  result: string | null;
  usage?: {
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
  };
}

/**
 * Hook for generating event descriptions
 */
export function useEventDescriptionAI() {
  const [state, setState] = useState<UseAIState>({
    loading: false,
    error: null,
    result: null,
  });

  const generate = async (params: {
    title: string;
    location: string;
    date: string;
    targetAudience?: string;
    eventType?: string;
  }) => {
    setState({ loading: true, error: null, result: null });

    try {
      const response = await generateEventDescription(params);

      setState({
        loading: false,
        error: response.success ? null : response.error || 'Generation failed',
        result: response.success ? response.content : null,
        usage: response.usage,
      });

      return response;
    } catch (err: any) {
      setState({
        loading: false,
        error: err.message || 'An error occurred',
        result: null,
      });
      return { success: false, content: '', error: err.message };
    }
  };

  const reset = () => {
    setState({ loading: false, error: null, result: null });
  };

  return {
    ...state,
    generate,
    reset,
    isEnabled: isAIFeatureEnabled('eventDescriptionGenerator'),
  };
}

/**
 * Hook for generating email content
 */
export function useEmailAI() {
  const [state, setState] = useState<UseAIState>({
    loading: false,
    error: null,
    result: null,
  });

  const generate = async (params: {
    eventTitle: string;
    eventDate: string;
    recipientType: 'registered' | 'attended' | 'reminder';
    additionalInfo?: string;
  }) => {
    setState({ loading: true, error: null, result: null });

    try {
      const response = await generateEmailContent(params);

      setState({
        loading: false,
        error: response.success ? null : response.error || 'Generation failed',
        result: response.success ? response.content : null,
        usage: response.usage,
      });

      return response;
    } catch (err: any) {
      setState({
        loading: false,
        error: err.message || 'An error occurred',
        result: null,
      });
      return { success: false, content: '', error: err.message };
    }
  };

  const reset = () => {
    setState({ loading: false, error: null, result: null });
  };

  return {
    ...state,
    generate,
    reset,
    isEnabled: isAIFeatureEnabled('emailContentGenerator'),
  };
}

/**
 * Hook for attendance insights
 */
export function useAttendanceInsightsAI() {
  const [state, setState] = useState<UseAIState>({
    loading: false,
    error: null,
    result: null,
  });

  const generate = async (params: {
    totalRegistrations: number;
    totalAttended: number;
    attendanceRate: number;
    eventTitle: string;
    historicalData?: any;
  }) => {
    setState({ loading: true, error: null, result: null });

    try {
      const response = await generateAttendanceInsights(params);

      setState({
        loading: false,
        error: response.success ? null : response.error || 'Generation failed',
        result: response.success ? response.content : null,
        usage: response.usage,
      });

      return response;
    } catch (err: any) {
      setState({
        loading: false,
        error: err.message || 'An error occurred',
        result: null,
      });
      return { success: false, content: '', error: err.message };
    }
  };

  const reset = () => {
    setState({ loading: false, error: null, result: null });
  };

  return {
    ...state,
    generate,
    reset,
    isEnabled: isAIFeatureEnabled('attendanceInsights'),
  };
}

/**
 * Hook for smart recommendations
 */
export function useRecommendationsAI() {
  const [state, setState] = useState<UseAIState>({
    loading: false,
    error: null,
    result: null,
  });

  const generate = async (params: {
    userHistory: string[];
    upcomingEvents: string[];
  }) => {
    setState({ loading: true, error: null, result: null });

    try {
      const response = await generateEventRecommendations(params);

      setState({
        loading: false,
        error: response.success ? null : response.error || 'Generation failed',
        result: response.success ? response.content : null,
        usage: response.usage,
      });

      return response;
    } catch (err: any) {
      setState({
        loading: false,
        error: err.message || 'An error occurred',
        result: null,
      });
      return { success: false, content: '', error: err.message };
    }
  };

  const reset = () => {
    setState({ loading: false, error: null, result: null });
  };

  return {
    ...state,
    generate,
    reset,
    isEnabled: isAIFeatureEnabled('smartRecommendations'),
  };
}

/**
 * Generic AI hook for custom prompts
 */
export function useAI() {
  const [state, setState] = useState<UseAIState>({
    loading: false,
    error: null,
    result: null,
  });

  const checkFeature = (feature: AIFeature): boolean => {
    return isAIFeatureEnabled(feature);
  };

  const reset = () => {
    setState({ loading: false, error: null, result: null });
  };

  return {
    ...state,
    checkFeature,
    reset,
  };
}
