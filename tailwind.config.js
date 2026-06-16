/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Cyber-noir / pro-audio palette
        canvas: "#0f172a", // slate base
        accent: {
          blue: "#38bdf8", // electric blue — primary waveform
          violet: "#8b5cf6", // violet — stems / secondary
          amber: "#f59e0b", // amber — sliders / active controls
        },
      },
      fontFamily: {
        mono: ["JetBrains Mono", "ui-monospace", "monospace"],
      },
      boxShadow: {
        neon: "0 0 12px rgba(56, 189, 248, 0.35)",
      },
    },
  },
  plugins: [],
};
