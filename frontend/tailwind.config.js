/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#0a0a0a",
        surface: "#181818",
        surfaceHover: "#212121",
        primary: "#fcfcfc",
        secondary: "#9e9e9e",
        borderDark: "rgba(255,255,255,0.08)",
        grokOrange: "#FF6B35"
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['IBM Plex Mono', 'monospace'],
      }
    },
  },
  plugins: [],
}
