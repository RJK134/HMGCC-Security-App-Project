/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // Confidence levels
        confidence: {
          high: "#22c55e",
          medium: "#f59e0b",
          low: "#ef4444",
        },
        // Source tiers
        tier: {
          1: "#3b82f6", // blue - manufacturer
          2: "#22c55e", // green - academic
          3: "#eab308", // yellow - trusted forum
          4: "#9ca3af", // gray - unverified
        },
        // App-specific
        sra: {
          bg: "var(--sra-bg)",
          sidebar: "var(--sra-sidebar)",
          card: "var(--sra-card)",
          border: "var(--sra-border)",
          text: "var(--sra-text)",
          muted: "var(--sra-muted)",
          accent: "#3b82f6",
        },
      },
    },
  },
  plugins: [require("@tailwindcss/typography")],
};
