import type { Config } from 'tailwindcss';
const config: Config = {
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}', './providers/**/*.{ts,tsx}'],
  darkMode: ['class'],
  theme: {
    extend: {
      colors: {
        glass: {
          base: 'rgba(17, 25, 40, 0.85)',
          highlight: 'rgba(255, 255, 255, 0.15)',
        },
      },
      backdropBlur: {
        xs: '2px',
      },
      boxShadow: {
        glass: '0 1px 20px rgba(15, 23, 42, 0.25)',
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
};
export default config;
