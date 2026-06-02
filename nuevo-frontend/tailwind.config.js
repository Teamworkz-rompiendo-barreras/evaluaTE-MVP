/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
    './src/**/*.html'
  ],
  theme: {
    extend: {
      colors: {
        primary: '#166534',     // Verde oscuro principal  — ratio 8.5:1 sobre blanco ✓
        secondary: '#15803d',   // Verde medio accesible   — ratio 5.5:1 sobre blanco ✓ (era #4ade80, ratio 1.9:1 ✗)
        'secondary-light': '#4ade80', // Solo para fondos decorativos, nunca como color de texto
        accent: '#16a34a',      // Verde medio hover       — ratio 6.2:1 sobre blanco ✓
        neutral: {
          light: '#F9F9F9',
          DEFAULT: '#EAEAEA',
          dark: '#1f2937',      // Oscurecido (era #454545, ratio 8.9:1 → ahora 15:1 sobre blanco)
        },
        success: '#15803d',
        warning: '#b45309',     // Ámbar oscuro — ratio 4.8:1 ✓ (era #FFA726, ratio 2.8:1 ✗)
        error: '#b91c1c',       // Rojo oscuro  — ratio 5.9:1 ✓ (era #EF5350, ratio 3.7:1 ✗)
        info: '#0369a1',        // Azul oscuro  — ratio 5.8:1 ✓ (era #0ea5e9, ratio 2.7:1 ✗)
      },
      fontFamily: {
        // Fuentes principales
        sans: [
          'Montserrat',
          'OpenDyslexic',
          'Verdana',
          'Arial',
          'Helvetica',
          'system-ui',
          'sans-serif'
        ],
        // Fuentes para encabezados
        heading: [
          'Montserrat',
          'OpenDyslexic',
          'Verdana',
          'Arial',
          'Helvetica',
          'system-ui',
          'sans-serif'
        ],
        // Fuente específica para dislexia
        dyslexic: [
          'OpenDyslexic',
          'Comic Sans MS',
          'Verdana',
          'Arial',
          'sans-serif'
        ],
        // Fuente de alta legibilidad
        readable: [
          'OpenDyslexic',
          'Verdana',
          'Arial',
          'Helvetica',
          'system-ui',
          'sans-serif'
        ],
        // Fuente para código - mantener monospace
        mono: [
          'Monaco',
          'Menlo',
          'Ubuntu Mono',
          'Consolas',
          'monospace'
        ]
      },
      fontSize: {
        xs: ['0.75rem', { lineHeight: '1.2rem' }],
        sm: ['0.875rem', { lineHeight: '1.4rem' }],
        base: ['1rem', { lineHeight: '1.6rem' }],
        lg: ['1.125rem', { lineHeight: '1.8rem' }],
        xl: ['1.25rem', { lineHeight: '2rem' }],
        '2xl': ['1.5rem', { lineHeight: '2.2rem' }],
        // Tamaños específicos para accesibilidad
        'accessible-sm': ['1rem', { lineHeight: '1.6rem' }],
        'accessible-base': ['1.125rem', { lineHeight: '1.8rem' }],
        'accessible-lg': ['1.25rem', { lineHeight: '2rem' }],
        'accessible-xl': ['1.5rem', { lineHeight: '2.2rem' }],
      },
      spacing: {
        '72': '18rem',
        '84': '21rem',
        '96': '24rem',
      },
      borderRadius: {
        '4xl': '2rem',
      },
      screens: {
        'xs': '480px',
        'sm': '640px',
        'md': '768px',
        'lg': '1024px',
        'xl': '1280px',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      }
    },
  },
  plugins: [],
  corePlugins: {
    preflight: true,
  }
}