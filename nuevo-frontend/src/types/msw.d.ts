// src/types/msw.d.ts
import type { RequestHandler, RestContext, RestRequest } from 'msw'
declare module 'msw' {
  export function rest(): any
  export type RestRequest = any
  export type ResponseResolver = any
  export type RestContext = any
  export const rest: {
    get: (path: string, resolver: RequestHandler) => void
    post: (path: string, resolver: RequestHandler) => void
    put: (path: string, resolver: RequestHandler) => void
    delete: (path: string, resolver: RequestHandler) => void
  }

  export function setupServer(...handlers: RequestHandler[]): {
    listen: () => void
    close: () => void
    resetHandlers: () => void
  }
}