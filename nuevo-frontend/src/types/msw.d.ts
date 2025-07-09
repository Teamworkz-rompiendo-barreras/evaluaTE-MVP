// src/types/msw.d.ts
declare const http: {
  get: (path: string, resolver?: any) => any
  post: (path: string, resolver?: any) => any
  put: (path: string, resolver?: any) => any
  delete: (path: string, resolver?: any) => any
}

declare class HttpResponse {
  static json(data: any): HttpResponse
  constructor(body?: any, init?: any)
}

declare function setupServer(...handlers: any[]): {
  listen: (options?: any) => void
  close: () => void
  resetHandlers: () => void
}

export { http, HttpResponse, setupServer };