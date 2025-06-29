// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    open: true
  },
  build: {
    outDir: 'dist',
    sourcemap: false // Reduce tamaño del build
  },
  resolve: {
    alias: {
      '@': '/src',
      '@/components': './src/components',
      '@/features': './src/features',
      '@/types': './src/types'
    }
  }
})