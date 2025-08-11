// src/features/games/scenesApi.ts
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'
import { API_CONFIG, buildApiUrl } from '../../config/api'
import { games } from '../../data/games'

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

// Función para convertir escenas de games.ts al formato esperado
const convertGameToScene = (gameId: string): Scene | null => {
  const game = games.find(g => g.id === gameId)
  if (!game || !game.scenes) return null

  // Convertir la primera escena del juego
  const firstScene = game.scenes[0]
  if (!firstScene) return null

  return {
    id: 0, // ID temporal
    title: firstScene.title,
    steps: [
      {
        text: firstScene.description,
        type: 'multiple-choice',
        options: (Array.isArray(firstScene.options) ? firstScene.options : []).map(opt => ({
          text: opt.text,
          skillImpact: { [game.softSkill]: opt.score / 100 },
          feedback: opt.feedback || ''
        }))
      }
    ]
  }
}

// API para cargar escenas
export const scenesApi = createApi({
  reducerPath: 'scenesApi',
  // Forzar base absoluta del backend para producción (SWA) y dev
  baseQuery: fetchBaseQuery({ baseUrl: API_CONFIG.BASE_URL }),
  endpoints: (builder) => ({
    getScenes: builder.query<Scene[], void>({
      queryFn: () => {
        // Retornar escenas convertidas de los juegos
        const scenes = (Array.isArray(games) ? games.slice(0, 10) : []).map((game, index) => ({
          id: index,
          title: game.title,
          steps: [{
            text: game.description,
            type: 'multiple-choice' as const,
            options: []
          }]
        }))
        return { data: scenes }
      },
    }),
    getScene: builder.query<Scene, string>({
      queryFn: (gameId) => {
        const scene = convertGameToScene(gameId)
        if (!scene) {
          return { error: { status: 404, data: 'Game not found' } }
        }
        return { data: scene }
      },
    }),
    sendGameLog: builder.mutation<void, GameLog>({
      query: (log) => ({
        // Mapear al endpoint existente del backend
        url: buildApiUrl('/api/logs/scene'),
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
  await fetch(buildApiUrl('/api/logs/scene'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ sceneId, step, choice }),
  })
}