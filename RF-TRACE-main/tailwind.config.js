export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        bg: 'var(--color-bg)',
        panel: 'var(--color-panel)',
        raised: 'var(--color-raised)',
        line: 'var(--color-line)',
        accent: 'var(--color-accent)',
        'accent-hover': 'var(--color-accent-hover)',
        warn: 'var(--color-warn)',
        bad: 'var(--color-bad)',
        main: 'var(--color-text-main)',
        sub: 'var(--color-text-sub)',
        muted: 'var(--color-text-muted)',
        title: 'var(--color-title)',
      },
      fontFamily: {
        sans: ['"IBM Plex Sans"', 'system-ui', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'ui-monospace', 'monospace'],
      },
    },
  },
  plugins: [],
};
