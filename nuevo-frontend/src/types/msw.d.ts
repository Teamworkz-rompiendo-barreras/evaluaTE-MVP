// src/types/msw.d.ts
declare module 'msw' {
  export const http: {
    get: (path: string, resolver?: any) => any
    post: (path: string, resolver?: any) => any
    put: (path: string, resolver?: any) => any
    delete: (path: string, resolver?: any) => any
  }

  export class HttpResponse {
    static json(data: any): HttpResponse
    constructor(body?: any, init?: any)
  }

  export function setupServer(...handlers: any[]): {
    listen: (options?: any) => void
    close: () => void
    resetHandlers: () => void
  }
}