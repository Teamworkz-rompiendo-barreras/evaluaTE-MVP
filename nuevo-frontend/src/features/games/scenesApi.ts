// src/features/games/scenesApi.ts
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'

// Interfaz de cada paso de escena
export interface SceneStep {
  text: string
  image?: string
  options?: Array<{ text: string }>
}

// Interfaz de una escena completa
export interface Scene {
  id: number
  title: string
  steps: SceneStep[]
}

export const scenesApi = createApi({
  reducerPath: 'scenesApi',
  baseQuery: fetchBaseQuery({ baseUrl: '/api' }),
  endpoints: (builder) => ({
    getScenes: builder.query<Scene[], void>({
      query: () => `scenes/index.json`,
    }),
    getScene: builder.query<Scene, string>({
      query: (id) => `scenes/${id}.json`,
    }),
  }),
})

export const {
  useGetScenesQuery,
  useGetSceneQuery,
} = scenesApi