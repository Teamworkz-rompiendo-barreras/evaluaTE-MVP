/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
    './src/**/*.html'
  ],
  theme: {
    extend: {
      colors: {
        primary: '#374BA6',     // Azul principal para botones e interacciones
        secondary: '#F2D680',   // Amarillo suave para fondos destacados
        accent: '#2563EB',     // Azul más oscuro para texto o gráficos
        neutral: {
          light: '#F9F9F9',
          DEFAULT: '#EAEAEA',
          dark: '#454545',
        },
        success: '#4CAF50',
        warning: '#FFA726',
        error: '#EF5350',
        info: '#2196F3',
      },
      fontFamily: {
        sans: ['Inter', 'Atkinson Hyperlegible', 'Arial', 'sans-serif'],
        heading: ['Poppins', 'Inter', 'Arial', 'sans-serif'],
      },
      fontSize: {
        xs: ['0.75rem', { lineHeight: '1rem' }],
        sm: ['0.875rem', { lineHeight: '1.25rem' }],
        base: ['1rem', { lineHeight: '1.5rem' }],
        lg: ['1.125rem', { lineHeight: '1.75rem' }],
        xl: ['1.25rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem', { lineHeight: '2rem' }],
      },
      spacing: {
        '72': '18rem',
        '84': '21rem',
        '96': '24rem',
      },
      borderRadius: {
        '4xl': '2rem',
      }
    },
  },
  plugins: [],
}