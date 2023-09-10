/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.{html,js}"],
  theme: {
    extend: {
      colors: {
      'dark-grayish-navy': '#2b2d42',
      'light-grayish-blue': '#8d99ae',
      'white-ish': '#edf2f4',
      'vivid-red': '#ef233c',
      'dark-vivid-red': '#d90429',
      },
    },
  },
  plugins: [],
}

