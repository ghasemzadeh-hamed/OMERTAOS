import type { Config } from 'tailwindcss';
import plugin from 'tailwindcss/plugin';

export default {
  darkMode: ['class'],
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}', './pages/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        glass: {
          surface: 'rgba(255, 255, 255, 0.1)',
          surfaceDark: 'rgba(15, 23, 42, 0.6)',
          border: 'rgba(255, 255, 255, 0.3)',
          accent: '#60a5fa'
        }
      },
      backdropBlur: {
        xl: '24px'
      },
      boxShadow: {
        glass: '0 10px 40px rgba(15, 23, 42, 0.25)'
      }
    }
  },
  plugins: [
    plugin(({ addUtilities }) => {
      addUtilities({
        '.glass-card': {
          '@apply bg-glass-surface/80 dark:bg-glass-surfaceDark/80 backdrop-blur-xl border border-glass-border/40 shadow-glass rounded-3xl': {}
        }
      });
    })
  ]
} satisfies Config;
