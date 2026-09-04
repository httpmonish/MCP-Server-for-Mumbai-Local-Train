/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
        hand: ['"Caveat"', 'cursive'],
        blueprint: ['"Architects Daughter"', 'cursive'],
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
