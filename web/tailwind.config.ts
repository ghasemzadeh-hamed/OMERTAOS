import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}'],
  darkMode: ['class'],
  theme: {
    extend: {
      colors: {
        glass: 'rgba(255, 255, 255, 0.08)',
        'glass-dark': 'rgba(15, 23, 42, 0.7)',
        accent: '#7f5af0',
        primary: '#1d4ed8',
      },
      backdropBlur: {
        xl: '24px',
      },
      borderRadius: {
        'glass-lg': '24px',
      },
      boxShadow: {
        glass: '0 30px 60px -30px rgba(15, 23, 42, 0.6)',
      },
      fontFamily: {
        display: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
};

export default config;
