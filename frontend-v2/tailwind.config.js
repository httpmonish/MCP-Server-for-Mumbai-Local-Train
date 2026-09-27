/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/*.{js,ts,jsx,tsx}",
    "./src/components/**/*.{js,ts,jsx,tsx}",
    "./src/hooks/**/*.{js,ts,jsx,tsx}",
    "./src/store/**/*.{js,ts,jsx,tsx}",
    "./src/types/**/*.{js,ts,jsx,tsx}",
    "./src/api/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'Inter', 'system-ui', '-apple-system', 'sans-serif'],
        body: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'monospace'],
      },
      colors: {
        obsidian: {
          DEFAULT: '#080c14',
          50: '#f8fafc',
          100: '#f1f5f9',
          800: '#111827',
          900: '#0b1120',
          950: '#070b13',
        },
        transit: {
          cr: '#f43f5e',
          wr: '#0ea5e9',
          hr: '#10b981',
          accent: '#06b6d4',
        },
      },
      keyframes: {
        'train-traverse': {
          '0%': { transform: 'translateX(-110%)' },
          '100%': { transform: 'translateX(110vw)' },
        },
        'spark': {
          '0%, 100%': { opacity: '0.1', transform: 'scale(0.8)' },
          '15%, 85%': { opacity: '0.9', transform: 'scale(1.4)' },
          '50%': { opacity: '0.2', transform: 'scale(0.9)' },
        },
        'moire-drift': {
          '0%': { backgroundPosition: '0% 0%' },
          '50%': { backgroundPosition: '100% 50%' },
          '100%': { backgroundPosition: '0% 0%' },
        },
      },
      animation: {
        'train-traverse': 'train-traverse 18s linear infinite',
        'spark': 'spark 2s ease-in-out infinite',
        'moire-drift': 'moire-drift 24s ease-in-out infinite',
      },
    },
  },
  plugins: [],
}
