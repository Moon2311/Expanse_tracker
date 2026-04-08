/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: { DEFAULT: "#1a1f2e", muted: "#5c6578", faint: "#8b93a7" },
        paper: { DEFAULT: "#faf8f5", warm: "#f3efe8" },
        accent: { DEFAULT: "#2d6a4f", light: "#d8f3dc" },
        accent2: { DEFAULT: "#bc6c25", light: "#ffe8d6" },
      },
      fontFamily: {
        display: ['"DM Serif Display"', "Georgia", "serif"],
        sans: ['"DM Sans"', "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
