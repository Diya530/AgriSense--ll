/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        display: ['Fraunces', 'ui-serif', 'serif'],
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      colors: {
        canvas: '#F6F7F2',
        ink: '#1B2B1E',
        foliage: {
          50: '#EEF3EC', 100: '#D6E3D0', 300: '#9DBE93', 500: '#4C7A44',
          700: '#2E5A2A', 800: '#1F3D2B', 900: '#152A1D',
        },
        wheat: {
          100: '#FBF0D2', 300: '#F0D385', 500: '#D4A017', 700: '#A67C0F',
        },
        soil: {
          300: '#B79574', 500: '#8A6440', 700: '#6B4226',
        },
        sky: {
          100: '#E3F0F7', 300: '#A8D2E6', 500: '#4A93B5',
        },
        clay: {
          400: '#D97757',
        },
      },
      borderRadius: {
        xs: '4px',
      },
      boxShadow: {
        soft: '0 1px 2px rgba(27, 43, 30, 0.06), 0 1px 1px rgba(27, 43, 30, 0.04)',
      },
    },
  },
  plugins: [],
}
