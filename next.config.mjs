import { createTranslator } from 'next-intl/server';
import createNextIntlPlugin from 'next-intl/plugin';
import withSuperjson from 'next-superjson-plugin';

const withNextIntl = createNextIntlPlugin('./i18n.ts');

const config = {
  reactStrictMode: true,
  experimental: {
    serverActions: true,
    typedRoutes: true
  },
  i18n: {
    locales: ['en', 'fa'],
    defaultLocale: 'en'
  },
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**'
      }
    ]
  }
};

export default withSuperjson()(withNextIntl(config));
