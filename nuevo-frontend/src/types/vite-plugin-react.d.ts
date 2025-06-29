// src/types/vite-plugin-react.d.ts
import type { Plugin } from 'rollup'

declare module '@vitejs/plugin-react' {
  const react: () => Plugin
  export default react
}