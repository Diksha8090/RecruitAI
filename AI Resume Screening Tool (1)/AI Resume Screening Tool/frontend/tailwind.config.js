/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        dark: {
          900: '#0D1117',
          800: '#161B22',
          700: '#1C2333',
          600: '#21262D',
          500: '#30363D',
        },
        teal: {
          400: '#2DD4BF',
          500: '#14B8A6',
          DEFAULT: '#00D4AA',
        },
        brand: {
          teal: '#00D4AA',
          orange: '#F59E0B',
          purple: '#8B5CF6',
          pink: '#EC4899',
          blue: '#3B82F6',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float': 'float 6s ease-in-out infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        }
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
      },
      boxShadow: {
        'glow-teal': '0 0 20px rgba(0, 212, 170, 0.3)',
        'glow-orange': '0 0 20px rgba(245, 158, 11, 0.3)',
      }
    },
  },
  plugins: [],
};
