/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'cream': '#FFF9F8',
        'lavender': '#C9B6E4',
        'pink-blush': '#EAD8EB',
        'charcoal': '#333333',
      },
      fontFamily: {
        'heading': ['Playfair Display', 'serif'],
        'body': ['Poppins', 'sans-serif'],
      },
      boxShadow: {
        'soft': '0 4px 6px -1px rgba(201, 182, 228, 0.1), 0 2px 4px -1px rgba(201, 182, 228, 0.06)',
        'soft-lg': '0 10px 15px -3px rgba(201, 182, 228, 0.1), 0 4px 6px -2px rgba(201, 182, 228, 0.05)',
      },
    },
  },
  plugins: [],
}

