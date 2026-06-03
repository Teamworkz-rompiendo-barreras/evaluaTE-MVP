import { ResponsiveRadar } from '@nivo/radar';
import React from 'react';

const SOFT_SKILLS = [
  "Toma de decisiones",
  "Pensamiento analítico",
  "Creatividad",
  "Influencia social",
  "Curiosidad y aprendizaje",
  "Resiliencia y flexibilidad",
  "Autoconciencia",
  "Empatía",
  "Pensamiento Crítico",
  "Liderazgo"
];

// Función para dividir etiquetas largas en múltiples líneas
const renderTick = (tick) => {
  const { x, y, value } = tick;
  
  // Dividir el texto en palabras
  const words = value.split(' ');
  
  // Si tiene exactamente 2 palabras, dividir en dos líneas
  if (words.length === 2) {
    return (
      <g>
        <text
          x={x}
          y={y - 7}
          textAnchor="middle"
          dominantBaseline="middle"
          style={{
            fontSize: '11px',
            fontWeight: 500,
            fill: '#666'
          }}
        >
          {words[0]}
        </text>
        <text
          x={x}
          y={y + 7}
          textAnchor="middle"
          dominantBaseline="middle"
          style={{
            fontSize: '11px',
            fontWeight: 500,
            fill: '#666'
          }}
        >
          {words[1]}
        </text>
      </g>
    );
  }
  
  // Si tiene más de 2 palabras, dividir en líneas
  if (words.length > 2) {
    const lines = [];
    let currentLine = '';
    
    words.forEach((word, index) => {
      if (currentLine.length + word.length > 12) {
        if (currentLine) lines.push(currentLine.trim());
        currentLine = word;
      } else {
        currentLine += (currentLine ? ' ' : '') + word;
      }
      
      if (index === words.length - 1 && currentLine) {
        lines.push(currentLine.trim());
      }
    });
    
    // Renderizar múltiples líneas
    return (
      <g>
        {lines.map((line, index) => (
          <text
            key={index}
            x={x}
            y={y + (index * 14) - (lines.length - 1) * 7}
            textAnchor="middle"
            dominantBaseline="middle"
            style={{
              fontSize: '11px',
              fontWeight: 500,
              fill: '#666'
            }}
          >
            {line}
          </text>
        ))}
      </g>
    );
  }
  
  // Para etiquetas cortas, renderizar normalmente
  return (
    <text
      x={x}
      y={y}
      textAnchor="middle"
      dominantBaseline="middle"
      style={{
        fontSize: '12px',
        fontWeight: 500,
        fill: '#666'
      }}
    >
      {value}
    </text>
  );
};

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
    <div style={{ height: 500, width: '100%' }}>
      <ResponsiveRadar
        data={radarData}
        keys={keys}
        indexBy="softskill"
        valueFormat=">-.0f"
        margin={{ top: 60, right: 120, bottom: 60, left: 120 }}
        borderColor={{ from: 'color' }}
        gridLabelOffset={50}
        dotSize={12}
        dotColor={{ theme: 'background' }}
        dotBorderWidth={2}
        dotBorderColor={{ from: 'color' }}
        colors={[isDark ? '#F2D680' : '#374BA6 ']}
        fillOpacity={0.25}
        blendMode="multiply"
        animate={true}
        isInteractive={true}
        renderTick={renderTick}
        theme={{
          text: {
            fontSize: 12,
            fontWeight: 500,
          },
          grid: {
            line: {
              stroke: '#ddd',
              strokeWidth: 1,
            },
          },
        }}
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
