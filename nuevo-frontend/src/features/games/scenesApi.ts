// src/features/games/scenesApi.ts
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'

// 1) Define cómo es tu objeto "Scene" que viene del backend
export interface Scene {
  id: string
  title: string
  steps: Array<{
    text: string
    // aquí puedes añadir más campos, p.ej. options, image, etc.
  }>
}

// 2) Crea el API slice
export const scenesApi = createApi({
  reducerPath: 'scenesApi',                            // nombre interno
  baseQuery: fetchBaseQuery({ baseUrl: '/api' }),      // prefijo de tus endpoints
  endpoints: (builder) => ({
    getScene: builder.query<Scene, string>({            // <TipoRespuesta, TipoArgumento>
      query: (id) => `scenes/${id}`,                    // GET /api/scenes/:id
    }),
  }),
})

// 3) Exporta el hook que usarás en tu componente
export const { useGetSceneQuery } = scenesApi
