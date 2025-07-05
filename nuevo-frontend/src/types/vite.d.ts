// src/types/vite.d.ts
declare module 'vite' {
  import { Plugin } from 'rollup'
  const defineConfig: (_config: { plugins?: Plugin[] }) => void
  export { defineConfig }
}
declare module 'vite/client' {
  const value: unknown
  export default value
}