// src/pages/queries.ts
import { gql } from '@apollo/client';

export const GET_EVALUATION_RESULTS = gql`
  query GetEvaluationResults($userId: String!) {
    evaluationResults(userId: $userId) {
      userId
      softSkillsScores {
        Resolucion_de_Problemas
        Gestion_emocional
        Trabajo_en_equipo
        Curiosidad_y_aprendizaje_continuo
        Resiliencia_y_flexibilidad
        Autoconciencia
        Empatia
        Escucha_activa
        Gestion_del_tiempo
      }
      employabilityScore
      level
      cvScore
      adjustedScore
    }
  }
`;