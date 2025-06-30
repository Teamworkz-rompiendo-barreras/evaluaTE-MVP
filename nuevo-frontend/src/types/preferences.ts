// src/types/preferences.ts

/**
 * Preferencias laborales del candidato
 */
export interface JobPreference {
  /**
   * Sectores o áreas de interés del candidato
   * Ejemplos: "Logística", "Atención al cliente", "Tecnología"
   */
  areas: string[]

  /**
   * Necesidades específicas o apoyos requeridos
   * Ejemplo: "Trabajo en entorno tranquilo", "Acceso a luz natural"
   */
  needs: string[]

  /**
   * Modo de trabajo preferido
   * remoto, presencial o híbrido
   */
  workMode?: 'remoto' | 'presencial' | 'híbrido'

  /**
   * Disponibilidad horaria
   * mañana, tarde o completa
   */
  availability?: 'mañana' | 'tarde' | 'completa'

  /**
   * ¿Está dispuesto a mudarse si es necesario?
   */
  willingToRelocate: boolean

  /**
   * ¿Tiene certificado de discapacidad?
   */
  hasDisabilityCert: boolean

  /**
   * Idiomas dominados (opcional)
   */
  languages?: string[]

  /**
   * Tipo de jornada deseada (opcional)
   */
  scheduleType?: 'media' | 'completa' | 'adaptativa'

  /**
   * Adaptaciones activadas durante la gamificación
   */
  accessibilitySettings?: AccessibilitySettings
}

/**
 * Configuración de accesibilidad según elecciones del usuario
 */
export interface AccessibilitySettings {
  /**
   * Si usa modo lectura fácil
   */
  easyReadingMode: boolean

  /**
   * Si ha activado ayuda auditiva
   */
  audioAssistiveMode: boolean

  /**
   * Si muestra pictogramas
   */
  showPictograms: boolean

  /**
   * Nivel de contraste activo
   */
  contrastLevel: 'normal' | 'alto' | 'muy-alto'
}