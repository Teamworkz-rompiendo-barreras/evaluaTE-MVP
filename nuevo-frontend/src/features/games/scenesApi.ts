// src/features/games/scenesApi.ts
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'

// Define el tipo de la escena según tu backend / mock
export interface SceneStep {
  text: string
}
export interface Scene {
  id: number
  title: string
  steps: SceneStep[]
}

export const scenesApi = createApi({
  reducerPath: 'scenesApi',
  baseQuery: fetchBaseQuery({ baseUrl: '/api' }),
  endpoints: (builder) => ({
    getScene: builder.query<Scene, string>({
      query: (id) => `scenes/${id}.json`,
    }),
    // en el futuro puedes añadir listScenes, postResults, etc.
  }),
})

// Exporta el hook
export const { useGetSceneQuery } = scenesApi
