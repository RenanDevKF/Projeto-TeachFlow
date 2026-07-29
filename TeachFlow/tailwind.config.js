/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './Templates/**/*.html',
    './static/**/*.js',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#4A90E2',
        secondary: '#F5A623',
      },
      fontFamily: {
        sans: ['Poppins', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
