import type { Config } from 'tailwindcss';

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
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
          900: '#1a3b37'
        },
      },
      fontFamily: {
        heading: ['"Space Grotesk"', 'sans-serif'],
        body: ['"Manrope"', 'sans-serif'],
      },
      boxShadow: {
        card: '0 10px 25px -15px rgba(17, 24, 39, 0.25)',
      },
    },
  },
  plugins: [],
} satisfies Config;
