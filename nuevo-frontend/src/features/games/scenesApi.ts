// src/features/games/scenesApi.ts
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'

// 1) Define la forma de los datos que espera tu API
export interface Scene {
  id: string
  title: string
  steps: Array<{
    text: string
    // aquí puedes añadir más campos, p.ej. options, image, etc.
  }>
}

// 2) Crea el API slice con RTK Query
export const scenesApi = createApi({
  reducerPath: 'scenesApi',                            // ruta interna del reducer
  baseQuery: fetchBaseQuery({ baseUrl: '/api' }),      // prefijo de tus endpoints
  endpoints: (builder) => ({
    // Este endpoint GET /api/scenes/:id
    getScene: builder.query<Scene, string>({            // <TipoRespuesta, TipoArgumento>
      query: (id) => `scenes/${id}`,                    // construye la URL
    }),
  }),
})

// 3) Exporta el hook para consumir el endpoint desde componentes
export const { useGetSceneQuery } = scenesApi
