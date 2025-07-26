import { ResponsiveRadar } from '@nivo/radar';
import React from 'react';

const SOFT_SKILLS = [
  "Toma de decisiones",
  "Pensamiento analítico",
  "Creatividad",
  "Trabajo en equipo",
  "Curiosidad y aprendizaje",
  "Resiliencia y flexibilidad",
  "Autoconciencia",
  "Empatía",
  "Comunicación",
  "Gestión del tiempo"
];

/**
 * RadarChart
 * @param {Object} props
 * @param {Object} props.userScores - { [softskill]: puntuación } para el usuario
 * @param {Object} [props.averageScores] - (opcional) { [softskill]: puntuación } para referencia
 */
export default function RadarChart({ userScores, averageScores }) {
  // Validar y limpiar los datos de entrada
  const cleanUserScores = userScores || {};
  const cleanAverageScores = averageScores || {};
  
  // Prepara los datos en el orden correcto, asegurándose de que todos los valores sean números válidos
  const radarData = SOFT_SKILLS.map(skill => ({
    softskill: skill,
    usuario: Number(cleanUserScores[skill]) || 0,
    ...(cleanAverageScores && { promedio: Number(cleanAverageScores[skill]) || 0 }),
  }));

  // Determina las keys que se van a graficar
  const keys = averageScores ? ['usuario', 'promedio'] : ['usuario'];

  // Evita renderizar si no hay datos válidos
  const hasScores = radarData.some(item => item.usuario > 0);

  if (!hasScores) {
    return <p>No hay datos suficientes para mostrar el radar chart.</p>;
  }

  return (
    <div style={{ height: 400, width: '100%' }}>
      <ResponsiveRadar
        data={radarData}
        keys={keys}
        indexBy="softskill"
        valueFormat=">-.0f"
        margin={{ top: 40, right: 80, bottom: 40, left: 80 }}
        borderColor={{ from: 'color' }}
        gridLabelOffset={20}
        dotSize={12}
        dotColor={{ theme: 'background' }}
        dotBorderWidth={2}
        dotBorderColor={{ from: 'color' }}
        colors={{ scheme: 'nivo' }}
        fillOpacity={0.25}
        blendMode="multiply"
        animate={true}
        isInteractive={true}
        legends={[
          {
            anchor: 'top-left',
            direction: 'column',
            translateX: -50,
            translateY: -30,
            itemWidth: 80,
            itemHeight: 20,
            itemTextColor: '#999',
            symbolSize: 12,
            symbolShape: 'circle',
          },
        ]}
      />
    </div>
  );
} 