/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // OPTCG color scheme
        optcg: {
          red: '#E53935',
          blue: '#1E88E5',
          green: '#43A047',
          purple: '#8E24AA',
          yellow: '#FDD835',
          black: '#212121',
        },
        // Tier colors
        tier: {
          s: '#FFD700',
          a: '#C0C0C0',
          b: '#CD7F32',
          c: '#4A90D9',
          d: '#808080',
        }
      },
      fontFamily: {
        display: ['Outfit', 'system-ui', 'sans-serif'],
        body: ['DM Sans', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}

