// frontend/tailwind.config.js
import typography from '@tailwindcss/typography';

export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}"
  ],
  theme: {
    extend: {
      colors: {
        freudenberg: {
          DEFAULT: "#005CA9",
          dark: "#003B73",
          light: "#E6F0FA"
        }
      }
    }
  },
  plugins: [
    typography,
  ]
};