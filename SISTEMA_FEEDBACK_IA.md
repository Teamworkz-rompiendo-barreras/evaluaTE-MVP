# Sistema de Feedback para IA - EvaluaTE

## ¿Cómo funciona el feedback?

### 1. Recopilación de Feedback
Cuando los usuarios completan su evaluación y reciben el informe de empleabilidad, pueden proporcionar feedback sobre la utilidad del informe:

- **Rating**: "Útil" o "No útil"
- **Comentarios**: Texto libre con sugerencias o críticas
- **Datos del usuario**: Contexto sobre sus habilidades evaluadas y preferencias

### 2. Almacenamiento
El feedback se guarda en el archivo `feedback_ia.json` en el directorio del backend con la siguiente estructura:

```json
{
  "informe": "Texto completo del informe generado",
  "rating": "Útil",
  "comment": "El informe fue muy útil para entender mis fortalezas",
  "userData": {
    "preferences": {...},
    "minigames": [...],
    "cvAnalysis": {...}
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

### 3. Aprendizaje de la IA
La IA aprende del feedback de la siguiente manera:

#### Carga de Feedback Previo
- Se cargan automáticamente los últimos 5 feedbacks marcados como "Útil"
- Solo se consideran feedbacks positivos para evitar sesgos negativos
- El feedback se incluye en el prompt de la IA para informes futuros

#### Mejora Continua
- La IA recibe contexto sobre qué aspectos fueron útiles para usuarios anteriores
- Los comentarios ayudan a identificar áreas de mejora específicas
- El sistema se adapta gradualmente a las preferencias de los usuarios

### 4. Endpoints Disponibles

#### POST `/api/informe-ia/feedback`
Recibe y almacena el feedback de los usuarios.

**Body:**
```json
{
  "informe": "texto del informe",
  "rating": "Útil" | "No útil",
  "comment": "comentario del usuario",
  "userData": {
    "preferences": {...},
    "minigames": [...],
    "cvAnalysis": {...}
  }
}
```

#### GET `/api/informe-ia/feedback/stats`
Obtiene estadísticas del feedback para análisis.

**Response:**
```json
{
  "total_feedback": 25,
  "useful_feedback": 20,
  "not_useful_feedback": 5,
  "useful_percentage": 80.0,
  "recent_feedback": [...],
  "common_comments": [...]
}
```

### 5. Beneficios del Sistema

#### Para Usuarios
- Los informes mejoran con el tiempo
- Feedback directo sobre la utilidad
- Personalización basada en experiencias previas

#### Para Desarrolladores
- Métricas de satisfacción del usuario
- Identificación de áreas de mejora
- Datos para optimización continua

#### Para la IA
- Aprendizaje de patrones exitosos
- Adaptación a preferencias de usuarios
- Mejora en la calidad de recomendaciones

### 6. Privacidad y Seguridad

- Los datos personales se anonimizan en el feedback
- Solo se almacenan comentarios y ratings
- No se comparten datos sensibles
- Cumplimiento con GDPR y normativas de privacidad

### 7. Monitoreo y Mantenimiento

#### Archivo de Feedback
- Ubicación: `backend/feedback_ia.json`
- Formato: JSON estructurado
- Backup automático recomendado

#### Limpieza Periódica
- Revisar feedbacks antiguos (>6 meses)
- Eliminar feedbacks duplicados o spam
- Mantener solo feedbacks relevantes

### 8. Próximas Mejoras

- [ ] Dashboard de administración para ver feedback
- [ ] Análisis de sentimientos automático
- [ ] Categorización automática de comentarios
- [ ] Alertas para feedback negativo
- [ ] Exportación de estadísticas
- [ ] Integración con herramientas de análisis

---

**Nota**: Este sistema permite que la IA mejore continuamente basándose en el feedback real de los usuarios, creando un ciclo de mejora constante para la calidad de los informes de empleabilidad.