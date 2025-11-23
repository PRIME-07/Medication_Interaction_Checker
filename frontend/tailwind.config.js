/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#f97316', // Orange-500
        secondary: '#fb923c', // Orange-400
        dark: {
          900: '#0f172a', // Slate-900 (Background)
          800: '#1e293b', // Slate-800 (Cards)
          700: '#334155', // Slate-700 (Borders)
          600: '#475569', // Slate-600 (Hover states) 
        }
      }
    },
  },
  plugins: [],
}
