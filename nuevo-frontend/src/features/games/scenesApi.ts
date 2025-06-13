// src/features/games/scenesApi.ts
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'

// Define el tipo de cada paso de escena
export interface SceneStep {
  text: string
}

// Define el tipo de la escena completa
export interface Scene {
  id: number
  title: string
  steps: SceneStep[]
}

export const scenesApi = createApi({
  reducerPath: 'scenesApi',
  baseQuery: fetchBaseQuery({ baseUrl: '/api' }),  // apunta a /public/api si sirves JSON estático ahí
  endpoints: (builder) => ({
    // 1) Listar todas las escenas (para el dashboard)
    getScenes: builder.query<Scene[], void>({
      query: () => `scenes/index.json`,
    }),
    // 2) Obtener una escena específica por id
    getScene: builder.query<Scene, string>({
      query: (id) => `scenes/${id}.json`,
    }),
  }),
})

// Exporta ambos hooks para usarlos en tus componentes
export const {
  useGetScenesQuery,
  useGetSceneQuery,
} = scenesApi
