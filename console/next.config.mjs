import createTranslator from 'next-intl/server';

const locales = ['en', 'fa'];

const nextConfig = {
  transpilePackages: ['@aionos/ui-core'],
  experimental: {
    serverActions: true,
  },
  reactStrictMode: true,
  i18n: {
    locales,
    defaultLocale: 'en',
  },
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Strict-Transport-Security',
            value: 'max-age=63072000; includeSubDomains; preload',
          },
        ],
      },
    ];
  },
  webpack: (config) => {
    config.resolve.fallback = {
      ...config.resolve.fallback,
      fs: false,
    };
    return config;
  },
};

export default nextConfig;

export const { getTranslator } = createTranslator({ locale: 'en', messages: {} });
