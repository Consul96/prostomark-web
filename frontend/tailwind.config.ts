import type { Config } from 'tailwindcss';

/**
 * Semantic, theme-aware design tokens.
 *
 * All platform surfaces reference these tokens instead of hard-coded
 * slate/white classes. The concrete color values live as CSS custom
 * properties in `src/styles/index.css` and are swapped between the
 * `light` and `dark` (class-based) themes. This is the single source of
 * truth for the ProstoMark visual system.
 */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f3f8f7',
          100: '#dcefeb',
          200: '#b9dfd8',
          300: '#8cc7bc',
          400: '#59ab9c',
          500: '#2f8c7f',
          600: '#216f65',
          700: '#1f5952',
          800: '#1d4641',
          900: '#1a3b37',
        },
        // Secondary accent used for charts / highlights.
        violet: {
          400: '#a78bfa',
          500: '#8b5cf6',
          600: '#7c3aed',
        },
        // --- Semantic surface & content tokens (CSS-variable driven) ---
        surface: {
          DEFAULT: 'rgb(var(--surface) / <alpha-value>)',
          raised: 'rgb(var(--surface-raised) / <alpha-value>)',
          overlay: 'rgb(var(--surface-overlay) / <alpha-value>)',
          inset: 'rgb(var(--surface-inset) / <alpha-value>)',
        },
        content: {
          DEFAULT: 'rgb(var(--content) / <alpha-value>)',
          muted: 'rgb(var(--content-muted) / <alpha-value>)',
          subtle: 'rgb(var(--content-subtle) / <alpha-value>)',
          inverted: 'rgb(var(--content-inverted) / <alpha-value>)',
        },
        line: {
          DEFAULT: 'rgb(var(--line) / <alpha-value>)',
          strong: 'rgb(var(--line-strong) / <alpha-value>)',
        },
        accent: {
          DEFAULT: 'rgb(var(--accent) / <alpha-value>)',
          soft: 'rgb(var(--accent-soft) / <alpha-value>)',
          contrast: 'rgb(var(--accent-contrast) / <alpha-value>)',
        },
      },
      fontFamily: {
        heading: ['"Space Grotesk"', 'sans-serif'],
        body: ['"Manrope"', 'sans-serif'],
      },
      boxShadow: {
        card: '0 1px 2px rgb(var(--shadow) / 0.06), 0 12px 30px -18px rgb(var(--shadow) / 0.35)',
        'card-raised': '0 1px 2px rgb(var(--shadow) / 0.08), 0 20px 45px -22px rgb(var(--shadow) / 0.5)',
      },
    },
  },
  plugins: [],
} satisfies Config;
