// src/types/nivo-radar.d.ts
import { ComponentType } from 'react'

interface RadarProps {
  data: any[]
  keys: string[]
  indexBy: string
  maxValue?: number
  margin?: { top: number; right: number; bottom: number; left: number }
  borderColor?: string
  gridShape?: 'linear' | 'circular'
  dotSize?: number
  dotColor?: string
  dotBorderWidth?: number
  enableDots?: boolean
  animate?: boolean
}

declare module '@nivo/radar' {
  export const ResponsiveRadar: ComponentType<RadarProps>
}