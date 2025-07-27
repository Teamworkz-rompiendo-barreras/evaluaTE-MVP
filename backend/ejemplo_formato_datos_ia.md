# Formato de Datos de Entrada a la IA

Este documento muestra exactamente cómo se formatean y proporcionan los datos de entrada a la IA para generar el informe final.

## 📋 Estructura de Datos de Entrada

Los datos se proporcionan a la IA en formato de texto estructurado, organizado en secciones claras y legibles.

### 🔄 Flujo de Datos

1. **Frontend** → Envía datos estructurados (JSON)
2. **Backend** → Convierte a formato de texto legible
3. **IA** → Recibe texto estructurado y genera informe

## 📝 Formato Completo de Entrada a la IA

```text
PERFIL COMPLETO DEL CANDIDATO:

DATOS PERSONALES:
- Nombre: Ester Pérez Ribada
- ID: user-ester-2025

HABILIDADES SOFT EVALUADAS:
- comunicación: 85% (Nivel: alto, Confianza: 90%)
- trabajo en equipo: 75% (Nivel: medio, Confianza: 85%)
- liderazgo: 60% (Nivel: medio, Confianza: 70%)
- resolución de problemas: 80% (Nivel: alto, Confianza: 85%)
- adaptabilidad: 70% (Nivel: medio, Confianza: 75%)

ANÁLISIS DETALLADO DEL CV:
PUNTOS FUERTES:
  • Formación académica presente
  • Perfil equilibrado con habilidades blandas
  • Perfil internacional con múltiples idiomas

ÁREAS DE MEJORA:
  • Falta de verbos de acción en las descripciones

FEEDBACK GENERAL: Tu CV tiene una estructura muy profesional y completa. Intenta usar verbos de acción y cuantificar tus logros. Has mencionado 5 tecnologías.

ESTRUCTURA: excelente
COHERENCIA: regular
EXPERIENCIA: mejorable

HABILIDADES TÉCNICAS DETECTADAS:
  • photoshop
  • office
  • microsoft
  • go
  • ant

FORMACIÓN DETECTADA:
  • ['EDUCACIÓN AUTÓNOMA']

ALERTAS O PUNTOS CRÍTICOS:
  ⚠️ Usa verbos de acción en tus descripciones

PREFERENCIAS LABORALES:
ÁREAS DE INTERÉS:
  • desarrollo web
  • frontend
  • UX/UI

NECESIDADES ESPECÍFICAS:
  • flexibilidad horaria
  • trabajo remoto
  • proyectos desafiantes

MODO DE TRABAJO: remoto
DISPONIBILIDAD: completa
DISPONIBILIDAD DE REUBICACIÓN: No
CERTIFICADO DE DISCAPACIDAD: No

JUEGOS COMPLETADOS:
juego1, juego2, juego3

LOGS DE JUEGOS:
[
  {
    "sceneId": 1,
    "decisions": [
      {
        "question": "¿Cómo te sientes en situaciones de presión?",
        "answer": "Mantengo la calma",
        "confidence": 85
      }
    ],
    "totalSteps": 5,
    "totalTime": 120,
    "averageConfidence": 85.0,
    "emotionalTrend": ["confiado", "tranquilo"],
    "accessibilityUsed": false
  }
]
```

## 🏗️ Estructura de Datos Original (JSON)

### 1. **Soft Skills (Habilidades Blandas)**
```json
{
  "softSkills": [
    {
      "skill": "comunicación",
      "score": 85,
      "level": "alto",
      "confidence": 90
    },
    {
      "skill": "trabajo en equipo",
      "score": 75,
      "level": "medio",
      "confidence": 85
    }
  ]
}
```

### 2. **Análisis de CV**
```json
{
  "cvAnalysis": {
    "strengths": ["Formación académica presente", "Perfil equilibrado con habilidades blandas"],
    "weaknesses": ["Falta de verbos de acción en las descripciones"],
    "feedback": "Tu CV tiene una estructura muy profesional y completa...",
    "structure": "excelente",
    "coherence": "regular",
    "experience": "mejorable",
    "skills": ["photoshop", "office", "microsoft", "go", "ant"],
    "education": ["EDUCACIÓN AUTÓNOMA"],
    "alerts": ["Usa verbos de acción en tus descripciones"]
  }
}
```

### 3. **Preferencias Laborales**
```json
{
  "jobPreferences": {
    "areas": ["desarrollo web", "frontend", "UX/UI"],
    "needs": ["flexibilidad horaria", "trabajo remoto", "proyectos desafiantes"],
    "workMode": "remoto",
    "availability": "completa",
    "willingToRelocate": false,
    "hasDisabilityCert": false
  }
}
```

### 4. **Juegos Completados**
```json
{
  "completedGames": ["juego1", "juego2", "juego3"],
  "logs": [
    {
      "sceneId": 1,
      "decisions": [
        {
          "question": "¿Cómo te sientes en situaciones de presión?",
          "answer": "Mantengo la calma",
          "confidence": 85
        }
      ],
      "totalSteps": 5,
      "totalTime": 120,
      "averageConfidence": 85.0,
      "emotionalTrend": ["confiado", "tranquilo"],
      "accessibilityUsed": false
    }
  ]
}
```

## 🔧 Funciones de Formateo

### `format_cv_analysis(cv_data: dict)`
Convierte el análisis del CV en texto estructurado:
- Puntos fuertes
- Áreas de mejora
- Feedback general
- Estructura y coherencia
- Habilidades técnicas
- Formación detectada
- Alertas

### `format_job_preferences(preferences: dict)`
Convierte las preferencias laborales en texto estructurado:
- Áreas de interés
- Necesidades específicas
- Modo de trabajo
- Disponibilidad
- Factores adicionales

## 📊 Datos que Recibe la IA

La IA recibe **TODOS** estos datos integrados:

1. ** Datos Personales**: Nombre e ID del usuario
2. **🎯 Soft Skills**: Habilidades evaluadas con puntuaciones, niveles y confianza
3. **📄 Análisis de CV**: Fortalezas, debilidades, habilidades técnicas, formación
4. **💼 Preferencias Laborales**: Áreas de interés, necesidades, modo de trabajo
5. **🎮 Juegos Completados**: Lista de juegos terminados
6. **📝 Logs de Juegos**: Decisiones detalladas, tiempos, tendencias emocionales

## 🎯 Ventajas del Formato

- **Legible**: Texto estructurado fácil de procesar por la IA
- **Completo**: Incluye todos los datos del sistema
- **Organizado**: Secciones claras y bien definidas
- **Contextual**: Cada dato tiene contexto y significado
- **Flexible**: Maneja datos faltantes de forma elegante

## 🔄 Proceso de Conversión

1. **JSON → Texto**: Los datos JSON se convierten a texto legible
2. **Formateo**: Se aplican funciones de formateo específicas
3. **Integración**: Se combinan todos los datos en un solo texto
4. **Envío a IA**: El texto completo se envía al prompt de la IA

Este formato permite que la IA tenga acceso completo a todos los datos del candidato para generar un informe personalizado y detallado. 