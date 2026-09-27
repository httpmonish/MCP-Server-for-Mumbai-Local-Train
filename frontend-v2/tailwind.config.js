/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/*.{js,ts,jsx,tsx}",
    "./src/components/*.{js,ts,jsx,tsx}",
    "./src/hooks/*.{js,ts,jsx,tsx}",
    "./src/store/*.{js,ts,jsx,tsx}",
    "./src/types/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        headline: ['"EB Garamond"', 'serif'],
        'headline-italic': ['"EB Garamond"', 'serif'],
        body: ['"Plus Jakarta Sans"', 'Inter', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
        telemetry: ['"JetBrains Mono"', 'monospace'],
      },
      colors: {
        'surface-obsidian': '#090A0C',
        'surface-glow': '#14171F',
        'surface-container-lowest': '#0d0e10',
        'surface-container-low': '#1b1c1e',
        'surface-container': '#1f2022',
        'surface-container-high': '#292a2c',
        'surface-container-highest': '#343537',
        'text-primary': '#F5F4F0',
        'text-secondary': 'rgba(255, 255, 255, 0.65)',
        'text-muted': 'rgba(255, 255, 255, 0.40)',
        primary: {
          DEFAULT: '#4edea3',
          container: '#10b981',
          fixed: '#6ffbbe',
        },
        secondary: {
          DEFAULT: '#ffb95f',
          container: '#ee9800',
        },
        tertiary: {
          DEFAULT: '#ffb2b7',
          container: '#ff7886',
        },
        'signal-rose': '#f43f5e',
        'signal-rose-glow': 'rgba(244, 63, 94, 0.15)',
        'lumen-green-glow': 'rgba(16, 185, 129, 0.15)',
        'transit-amber-glow': 'rgba(245, 158, 11, 0.15)',
        'glass-surface': 'rgba(255, 255, 255, 0.03)',
        'glass-border': 'rgba(255, 255, 255, 0.08)',
        'glass-border-hover': 'rgba(255, 255, 255, 0.18)',
      },
    },
  },
  plugins: [],
}
