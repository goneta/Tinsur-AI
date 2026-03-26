/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    // Workaround for Next.js 15.5.x devtools RSC manifest/runtime crash on some setups.
    devtoolSegmentExplorer: false,
  },
  // Allow opening dev server from LAN URL while testing on same network.
  allowedDevOrigins: ['192.168.100.32'],
};

module.exports = nextConfig;

// Forced update to clear Vercel build cache: 2026-01-30 04:10
