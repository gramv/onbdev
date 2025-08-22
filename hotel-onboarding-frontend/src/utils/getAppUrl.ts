/**
 * Get the current application URL dynamically
 * In production, uses the actual domain from window.location
 * Falls back to environment variable or default production URL
 */
export const getAppUrl = (): string => {
  // In browser environment, use the actual domain
  if (typeof window !== 'undefined') {
    return window.location.origin;
  }
  
  // Fallback for SSR or build time
  return import.meta.env.VITE_APP_URL || 'https://hotel-onboarding-frontend.vercel.app';
};

/**
 * Get the application URL for a specific path
 * @param path - The path to append (should start with /)
 */
export const getAppUrlWithPath = (path: string): string => {
  const baseUrl = getAppUrl();
  // Ensure path starts with /
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${baseUrl}${normalizedPath}`;
};