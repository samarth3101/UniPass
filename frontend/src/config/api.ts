/**
 * Central API Configuration
 * All API URLs should go through this to ensure consistent HTTPS usage
 */

/**
 * Get the API base URL
 * - In browser with HTTPS: uses /api proxy to avoid mixed content
 * - Otherwise: uses environment variable or falls back to /api
 */
export const getApiUrl = (): string => {
  // Use environment variable if set
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }

  // In browser, check protocol
  if (typeof window !== 'undefined') {
    const protocol = window.location.protocol;
    
    // Always use proxy when on HTTPS to avoid mixed content errors
    if (protocol === 'https:') {
      return '/api';
    }
    
    // For HTTP (dev only), direct connection
    return 'http://localhost:8000';
  }

  // Server-side or fallback: use proxy
  return '/api';
};

/**
 * Get full API URL (for external links like docs)
 */
export const getFullApiUrl = (): string => {
  const baseUrl = getApiUrl();
  
  // If it's /api, construct full URL
  if (baseUrl === '/api' && typeof window !== 'undefined') {
    return `${window.location.protocol}//localhost:8000`;
  }
  
  return baseUrl;
};

// Export as default for easy import
export default getApiUrl();
