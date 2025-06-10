/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        primary: "#374BA6",
        secondary: "#F2D680",
        text: "#454545",
      },
      fontFamily: {
        sans: ["Inter", "Atkinson Hyperlegible", "Arial", "sans-serif"],
      },
    },
  },
  plugins: [],
};
