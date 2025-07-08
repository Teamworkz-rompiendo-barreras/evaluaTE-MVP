// src/types/nivo-radar.d.ts

export interface RadarProps {
  data: unknown[]
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

export const ResponsiveRadar: React.ComponentType<RadarProps>