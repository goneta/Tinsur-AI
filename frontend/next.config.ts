import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone',
  outputFileTracingRoot: '/var/www/html/Tinsur-AI',
  experimental: {
    devtoolSegmentExplorer: false,
  },
  allowedDevOrigins: ['192.168.100.32'],
};

export default nextConfig;
