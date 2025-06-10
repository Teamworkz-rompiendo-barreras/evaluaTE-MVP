import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  // Opcional: si más adelante quieres customizar rutas o alias,
  // lo harás aquí.
});
