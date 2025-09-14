import test from 'node:test';
import assert from 'node:assert/strict';
import { convertBackendResponseToNewFormat, generateNewFormatReport, type NewReportSchema } from './reportConfig.ts';

const mockNewFormat: NewReportSchema = {
  summary: 'Resumen ejecutivo del candidato',
  personal_data: {
    name: 'José Manuel Azaña',
    location: 'Madrid, España',
    email: 'jmanuelazana@gmail.com',
    phone: '+34 600 000 000',
    disability_certificate: 'Sí'
  },
  profile_summary: 'Perfil profesional con experiencia en desarrollo de software y habilidades de liderazgo.',
  cv_summary: 'CV bien estructurado con experiencia en tecnologías modernas.',
  strengths: ['Liderazgo de equipos técnicos'],
  soft_skills: [
    { skill: 'Liderazgo', score: 90 },
    { skill: 'Comunicación', score: 85 }
  ],
  improvement_areas: [
    {
      area: 'Gestión de proyectos',
      reason: 'Necesita más experiencia en metodologías ágiles',
      suggested_action: 'Completar certificación Scrum Master'
    }
  ],
  cv_analysis: {
    structure_score: 4,
    coherence_score: 4,
    key_info_score: 5,
    clarity_score: 4,
    style_score: 5,
    evidence: {
      structure: 'CV bien organizado',
      coherence: 'Información coherente',
      key_info: 'Incluye datos relevantes',
      clarity: 'Lenguaje claro',
      style: 'Presentación profesional'
    },
    corrections: [],
    reordering_suggestions: [],
    observations: ['Observación 1', 'Observación 2'],
    actions: ['Acción 1', 'Acción 2']
  },
  ideal_work_environment: 'Entorno dinámico',
  suggested_roles: [
    {
      role: 'Senior Full-Stack Developer',
      reason: 'Experiencia técnica sólida',
      seniority: 'Senior',
      remote_viable: true
    }
  ],
  action_plan: {
    short_term: ['Actualizar CV'],
    medium_term: ['Completar certificación AWS'],
    long_term: ['Desarrollar especialización en arquitectura cloud']
  },
  job_search_advice: {
    cv_optimization: ['Usar palabras clave específicas del sector'],
    letters_portfolio: 'Preparar carta de presentación personalizada',
    recommended_platforms: ['LinkedIn'],
    networking: 'Participar en meetups',
    interview_tips: 'Practicar presentación de proyectos técnicos'
  },
  useful_tools: {
    productivity: ['Trello'],
    job_search: ['LinkedIn'],
    learning: ['Coursera'],
    accessibility: ['Ninguna']
  },
  completed_games: ['Juego de lógica'],
  final_message: '¡Éxitos en tu búsqueda laboral!'
};

test('convertBackendResponseToNewFormat returns data as-is for new format', () => {
  const result = convertBackendResponseToNewFormat(mockNewFormat);
  assert.deepEqual(result, mockNewFormat);
});

test('convertBackendResponseToNewFormat keeps contact fields in new format', () => {
  const result = convertBackendResponseToNewFormat(mockNewFormat);
  assert.equal(result.personal_data.location, 'Madrid, España');
  assert.equal(result.personal_data.email, 'jmanuelazana@gmail.com');
  assert.equal(result.personal_data.phone, '+34 600 000 000');
});

test('convertBackendResponseToNewFormat transforms old format', () => {
  const oldFormat = {
    report: {
      fullName: 'María García',
      personal_data: {
        name: 'María García',
        location: 'Sevilla, España',
        email: 'maria@example.com',
        phone: '+34 123 456 789'
      },
      resumen_ejecutivo: 'Candidata con experiencia en marketing digital',
      soft_skills: [
        { skill: 'Comunicación', score: 80 },
        { name: 'Trabajo en equipo', score: 75 }
      ],
      cvAnalysis: {
        structure: 'good',
        feedback: 'CV bien estructurado con información relevante'
      }
    },
    recommendations: { fortalezas_clave: ['Habilidades de comunicación', 'Capacidad analítica'] }
  };
  const result = convertBackendResponseToNewFormat(oldFormat);
  assert.equal(result.personal_data.name, 'María García');
  assert.equal(result.personal_data.location, 'Sevilla, España');
  assert.equal(result.personal_data.email, 'maria@example.com');
  assert.equal(result.personal_data.phone, '+34 123 456 789');
  assert.deepEqual(result.strengths, ['Habilidades de comunicación', 'Capacidad analítica']);
  assert.deepEqual(result.soft_skills, [
    { skill: 'Comunicación', score: 80 },
    { skill: 'Trabajo en equipo', score: 75 }
  ]);
  assert.deepEqual(result.cv_analysis.observations, []);
  assert.deepEqual(result.cv_analysis.actions, []);
});

test('convertBackendResponseToNewFormat uses report fields when personal_data is missing', () => {
  const oldFormat = {
    report: {
      fullName: 'Carlos López',
      location: 'Valencia, España',
      email: 'carlos@example.com',
      phone: '+34 111 222 333',
      disability_certificate: 'No'
    }
  };
  const result = convertBackendResponseToNewFormat(oldFormat);
  assert.deepEqual(result.personal_data, {
    name: 'Carlos López',
    location: 'Valencia, España',
    email: 'carlos@example.com',
    phone: '+34 111 222 333',
    disability_certificate: 'No'
  });
});

test('generateNewFormatReport includes required sections', () => {
  const report = generateNewFormatReport(mockNewFormat);
  const sections = [
    '## 1. Datos personales básicos',
    '## 2. Resumen del perfil',
    '## 3. Resumen del CV',
    '## 4. Fortalezas',
    '# 5. Áreas de mejora y consejos',
    'Observaciones del análisis:',
    'Correcciones/Acciones:'
  ];
  sections.forEach(section => {
    assert.ok(report.includes(section));
  });
});

test('generateNewFormatReport includes radarData block', () => {
  const report = generateNewFormatReport(mockNewFormat);
  const match = report.match(/```json\n([\s\S]*?)\n```/);
  assert.ok(match?.[1], 'radarData block not found');
  const parsed = JSON.parse(match![1]!);
  assert.deepEqual(parsed, {
    radarData: mockNewFormat.soft_skills.map(s => ({ softskill: s.skill, score: s.score }))
  });
});
