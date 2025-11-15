import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: process.env.BUILD_STANDALONE === 'true' ? 'standalone' : 'export',
  basePath: process.env.NEXT_PUBLIC_BASE_PATH || '',
  images: {
    unoptimized: true, // Required for static export
  },
  // Disable features not supported in static export
  ...(process.env.BUILD_STANDALONE !== 'true' && {
    trailingSlash: true,
  }),
};

export default nextConfig;
