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
        // Fuentes principales - ordenadas por accesibilidad cognitiva
        sans: [
          'OpenDyslexic',           // Fuente específica para dislexia
          'Verdana',                // Fuente clara y espaciada
          'Arial',                  // Fallback universal
          'Helvetica',
          'system-ui',
          'sans-serif'
        ],
        // Fuentes para encabezados - más legibles
        heading: [
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
    }  
    },
  },
  plugins: [],
}