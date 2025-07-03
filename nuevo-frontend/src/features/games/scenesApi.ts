// src/features/games/scenesApi.ts
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'

// Tipos esperados en cada opción
export interface GameOption {
  text: string
  isCorrect?: boolean // si la opción lleva a buen resultado
  skillImpact?: Record<string, number> // impacto en habilidades blandas, ej: { 'Toma de decisiones': 0.85 }
  feedback?: string // mensaje tras elegir esta opción
}

// Cada paso de escena puede tener texto, imagen, opciones e info para IA
export interface SceneStep {
  text: string
  type?: 'multiple-choice' | 'drag-and-drop' | 'dialogue' | 'reflection'
  image?: string
  options?: GameOption[]
  timeLimit?: number // segundos para responder
  requiresAudio?: boolean
  requiresDragDrop?: boolean
}

// Una escena completa tiene ID, título y pasos
export interface Scene {
  id: number
  title: string
  steps: SceneStep[]
}

// Logs para backend / IA
export interface GameLog {
  gameId: number
  responses: {
    stepIndex: number
    optionIndex: number
    timeSpent: number
    usedHelp: boolean
    retries: number
    emotionalResponse: string
  }[]
}

// API para cargar escenas
export const scenesApi = createApi({
  reducerPath: 'scenesApi',
  baseQuery: fetchBaseQuery({ baseUrl: '/api' }),
  endpoints: (builder) => ({
    getScenes: builder.query<Scene[], void>({
      query: () => 'scenes/index.json',
    }),
    getScene: builder.query<Scene, string>({
      query: (id) => `scenes/${id}.json`,
    }),
    sendGameLog: builder.mutation<void, GameLog>({
      query: (log) => ({
        url: '/analyze/log',
        method: 'POST',
        body: log,
      }),
    }),
  }),
})

// Exportamos hooks
export const {
  useGetScenesQuery,
  useGetSceneQuery,
  useSendGameLogMutation,
} = scenesApi

export const logSceneInteraction = async (
  sceneId: number,
  step: number,
  choice: string
) => {
  await fetch(`/api/logs/step`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ sceneId, step, choice }),
  })
}