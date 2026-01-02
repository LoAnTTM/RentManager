import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#fef7ee',
          100: '#fdedd6',
          200: '#fad7ac',
          300: '#f6ba78',
          400: '#f19342',
          500: '#ed751d',
          600: '#de5a13',
          700: '#b84312',
          800: '#933616',
          900: '#772f15',
          950: '#401509',
        },
        warm: {
          50: '#fdfcfb',
          100: '#faf7f4',
          200: '#f5ede5',
          300: '#ebe0d2',
          400: '#dccbb5',
          500: '#c9b094',
          600: '#b39474',
          700: '#967758',
          800: '#7a6149',
          900: '#64503d',
        }
      },
      fontFamily: {
        sans: ['Be Vietnam Pro', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
export default config

