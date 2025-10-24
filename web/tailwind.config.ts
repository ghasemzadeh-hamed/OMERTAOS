import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: ['class'],
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        background: 'var(--background)',
        foreground: 'var(--foreground)'
      },
      backdropBlur: {
        xs: '2px'
      },
      boxShadow: {
        glass: '0 20px 45px rgba(0,0,0,0.25)'
      },
      borderRadius: {
        glass: '24px'
      },
      animation: {
        'pulse-glow': 'pulseGlow 4s ease-in-out infinite'
      },
      keyframes: {
        pulseGlow: {
          '0%, 100%': { boxShadow: '0 0 10px rgba(99,102,241,0.4)' },
          '50%': { boxShadow: '0 0 20px rgba(129,140,248,0.7)' }
        }
      }
    }
  },
  plugins: [require('tailwindcss-animate')]
}

export default config
