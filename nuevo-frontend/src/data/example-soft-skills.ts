// src/data/example-soft-skills.ts
// Datos de ejemplo para probar el radar chart con 10 habilidades blandas

export interface ExampleSoftSkill {
  skill: string;
  score: number;
  level: 'bajo' | 'medio' | 'alto';
  confidence: number;
}

export const exampleSoftSkills: ExampleSoftSkill[] = [
  {
    skill: "Comunicación",
    score: 85,
    level: "alto",
    confidence: 0.9
  },
  {
    skill: "Trabajo en equipo",
    score: 78,
    level: "medio",
    confidence: 0.8
  },
  {
    skill: "Liderazgo",
    score: 72,
    level: "medio",
    confidence: 0.7
  },
  {
    skill: "Resolución de problemas",
    score: 88,
    level: "alto",
    confidence: 0.9
  },
  {
    skill: "Adaptabilidad",
    score: 65,
    level: "medio",
    confidence: 0.6
  },
  {
    skill: "Gestión del tiempo",
    score: 82,
    level: "alto",
    confidence: 0.8
  },
  {
    skill: "Creatividad",
    score: 75,
    level: "medio",
    confidence: 0.7
  },
  {
    skill: "Pensamiento crítico",
    score: 90,
    level: "alto",
    confidence: 0.9
  },
  {
    skill: "Inteligencia emocional",
    score: 68,
    level: "medio",
    confidence: 0.6
  },
  {
    skill: "Negociación",
    score: 70,
    level: "medio",
    confidence: 0.7
  }
];

// Datos en formato compatible con el radar chart
export const radarChartData = exampleSoftSkills.map(skill => ({
  softskill: skill.skill,
  score: skill.score
}));
