// src/types/vite.d.ts
declare module 'vite' {
  import { Plugin } from 'rollup'
  const defineConfig: (config: { plugins?: Plugin[] }) => void
  export { defineConfig }
}