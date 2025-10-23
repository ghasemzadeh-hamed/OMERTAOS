/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  experimental: {
    appDir: true
  },
  i18n: {
    locales: ['en', 'fa'],
    defaultLocale: 'en',
    localeDetection: true
  }
};

export default nextConfig;
