// src/pages/queries.ts
import { gql } from '@apollo/client';

export const GET_EVALUATION_RESULTS = gql`
  query GetEvaluationResults($userId: String!) {
    evaluationResults(userId: $userId) {
      userId
      softSkillsScores {
        Resolución_de_Problemas
        Gestión_emocional
        Trabajo_en_equipo
        Curiosidad_y_aprendizaje_continuo
        Resiliencia_y_flexibilidad
        Autoconciencia
        Empatía
        Escucha_activa
        Gestión_del_tiempo
      }
      employabilityScore
      level
      cvScore
      adjustedScore
    }
  }
`;