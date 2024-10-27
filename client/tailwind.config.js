/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      colors: {
        // Loss colors (reds) - for negative returns
        "loss-severe": "#770000", // -50% or worse
        "loss-heavy": "#990000", // -35% to -50%
        "loss-medium": "#cc0000", // -20% to -35%
        "loss-light": "#ff1a1a", // -10% to -20%
        "loss-slight": "#ff4d4d", // 0% to -10%

        // Neutral for very small changes
        neutral: "#808080", // Between -1% and +1%

        // Gain colors (greens) - for positive returns
        "gain-slight": "#21ce99", // 0% to +10%
        "gain-light": "#1cb589", // +10% to +20%
        "gain-medium": "#179c79", // +20% to +35%
        "gain-heavy": "#147a5f", // +35% to +50%
        "gain-severe": "#0d503e", // +50% or better
      },
    },
  },
  plugins: [require("@tailwindcss/forms")],
};
