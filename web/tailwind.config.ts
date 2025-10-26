import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        primary: "#A5D6A7",
        "background-light": "#FFFFFF",
        "background-dark": "#112111",
        "neutral-grey": "#B0BEC5",
        "dark-grey": "#37474F",
        "brand-deep": "#164A41",
        "cta-blue": "#4FC3F7"
      },
      fontFamily: {
        display: ["Manrope", "sans-serif"]
      },
      borderRadius: {
        DEFAULT: "0.25rem",
        lg: "0.5rem",
        xl: "0.75rem",
        full: "9999px"
      }
    }
  },
  darkMode: "class"
};

export default config;
