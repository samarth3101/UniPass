import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    // Use environment variable for API URL, fallback to localhost for development
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    
    return [
      {
        source: '/api/:path*',
        destination: `${apiUrl}/:path*`,
      },
    ];
  },
  // Enable standalone output for optimal deployment
  output: 'standalone',
};

export default nextConfig;
