// src/types/vite-plugin-react.d.ts
import type { Plugin } from 'rollup'

declare module '@vitejs/plugin-react' {
  import type { Plugin } from 'rollup'
  const react: () => Plugin
  export default react
}