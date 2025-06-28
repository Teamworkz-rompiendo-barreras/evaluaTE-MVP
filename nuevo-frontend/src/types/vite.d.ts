// src/types/vite.d.ts
declare module 'vite' {
  import { Plugin } from 'rollup'
  export function defineConfig(config: { plugins?: Plugin[] }): { plugins: Plugin[] }
}