import test from 'node:test';
import assert from 'node:assert/strict';
import { convertBackendResponseToNewFormat, generateNewFormatReport, type NewReportSchema, type PersonalData } from './reportConfig';

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
  cv_details: {
    experience: ['Desarrollador en ACME (2020-2023)'],
    education: ['Ingeniería Informática - Universidad Complutense'],
    languages: ['Inglés (C1)'],
    tools: ['React', 'Node.js'],
  },
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
    reordering_suggestions: []
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
  final_message: '¡Éxitos en tu búsqueda laboral!',
  employability_score: 76,
  job_preferences: {
    areas: ['Desarrollo de software'],
    needs: [],
    preferred_platforms: ['LinkedIn'],
    location: 'Madrid, España',
    seniority: 'Senior',
    work_mode: 'híbrido',
    disability_certificate: 'Sí',
    availability: 'completa',
    willing_to_relocate: false,
  },
};

test('convertBackendResponseToNewFormat returns data as-is for new format', () => {
  const result = convertBackendResponseToNewFormat(mockNewFormat);
  assert.deepEqual(result, mockNewFormat);
  assert.equal(result.employability_score, 76);
  assert.deepEqual(result.cv_details, mockNewFormat.cv_details);
});

test('convertBackendResponseToNewFormat keeps contact fields in new format', () => {
  const result = convertBackendResponseToNewFormat(mockNewFormat);
  assert.equal(result.personal_data.location, 'Madrid, España');
  assert.equal(result.personal_data.email, 'jmanuelazana@gmail.com');
  assert.equal(result.personal_data.phone, '+34 600 000 000');
});

test('convertBackendResponseToNewFormat fills defaults when new-format fields are empty', () => {
  const minimalNewFormat: Partial<NewReportSchema> = {
    summary: '',
    profile_summary: '',
    cv_summary: '',
    personal_data: { name: '', location: '', email: '', phone: '', disability_certificate: '' },
    cv_details: { experience: [], education: [], languages: [], tools: [] },
    strengths: [],
    soft_skills: [],
    improvement_areas: [],
    cv_analysis: {
      structure_score: 0,
      coherence_score: 0,
      key_info_score: 0,
      clarity_score: 0,
      style_score: 0,
      evidence: { structure: '', coherence: '', key_info: '', clarity: '', style: '' },
      corrections: [],
      reordering_suggestions: [],
    },
    ideal_work_environment: '',
    suggested_roles: [],
    action_plan: { short_term: [], medium_term: [], long_term: [] },
    job_search_advice: {
      cv_optimization: [],
      letters_portfolio: '',
      recommended_platforms: [],
      networking: '',
      interview_tips: '',
    },
    useful_tools: { productivity: [], job_search: [], learning: [], accessibility: [] },
    employability_score: 0,
    completed_games: [],
    final_message: '',
    job_preferences: {
      areas: [],
      needs: [],
      preferred_platforms: [],
      location: '',
      seniority: '',
      work_mode: '',
      disability_certificate: '',
      availability: '',
      willing_to_relocate: false,
    },
  };

  const result = convertBackendResponseToNewFormat(minimalNewFormat);

  assert.equal(result.summary, 'Perfil profesional en desarrollo.');
  assert.equal(result.profile_summary, 'Perfil profesional en desarrollo.');
  assert.equal(result.cv_summary, 'Perfil profesional en desarrollo.');
  assert.equal(result.personal_data.name, 'Usuario');
  assert.equal(result.personal_data.location, 'No consta');
  assert.equal(result.personal_data.email, 'No consta');
  assert.equal(result.personal_data.phone, 'No especificado');
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
    recommendations: { fortalezas_clave: ['Habilidades de comunicación', 'Capacidad analítica'] },
    employabilityScore: 66
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
  assert.equal(result.employability_score, 66);
  assert.ok(Array.isArray(result.cv_details.experience));
  assert.ok(Array.isArray(result.cv_details.education));
});

test('convertBackendResponseToNewFormat extracts all useful_tools categories', () => {
  const oldFormat = {
    report: {
      tools: {
        productivity: ['Trello'],
        job_search: ['LinkedIn'],
        learning: ['Coursera'],
        accessibility: ['Immersive Reader'],
      },
    },
  };
  const result = convertBackendResponseToNewFormat(oldFormat);
  assert.deepEqual(result.useful_tools, {
    productivity: ['Trello'],
    job_search: ['LinkedIn'],
    learning: ['Coursera'],
    accessibility: ['Immersive Reader'],
  });
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
    '## 2. Preferencias laborales',
    '## 3. Resumen del perfil',
    '## 4. Resumen del CV',
    '### Experiencia destacada',
    '## 5. Fortalezas',
    '# 6. Áreas de mejora y consejos'
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

test('generateNewFormatReport renders CV scores as stars', () => {
  const report = generateNewFormatReport(mockNewFormat);
  assert.ok(report.includes('Estructura: ★★★★☆'));
  assert.ok(report.includes('Coherencia: ★★★★☆'));
  assert.ok(report.includes('Información clave: ★★★★★'));
  assert.ok(report.includes('Claridad: ★★★★☆'));
  assert.ok(report.includes('Estilo: ★★★★★'));
});

test('generateNewFormatReport shows user contact info when backend omits it', () => {
  const backendMissing: NewReportSchema = {
    ...mockNewFormat,
    personal_data: { name: '', location: '', email: '', phone: '', disability_certificate: '' },
    job_preferences: mockNewFormat.job_preferences,
  };
  const normalized = convertBackendResponseToNewFormat(backendMissing);
  const dp: PersonalData = {
    name: 'Ana Ejemplo',
    location: 'Granada',
    email: 'ana@example.com',
    phone: '+34 999 999 999',
    disability_certificate: 'No'
  };
  const isMissing = (val: unknown): boolean => {
    if (val === undefined || val === null) return true;
    if (typeof val === 'string') {
      const trimmed = val.trim();
      return trimmed === '' || trimmed === 'No consta' || trimmed === 'No especificado';
    }
    return false;
  };
  for (const key of Object.keys(dp) as (keyof PersonalData)[]) {
    if (isMissing(normalized.personal_data[key])) {
      normalized.personal_data[key] = dp[key];
    }
  }
  const md = generateNewFormatReport(normalized);
  assert.ok(md.includes('Email: ana@example.com'));
  assert.ok(md.includes('Teléfono: +34 999 999 999'));
  assert.ok(md.includes('Ubicación: Granada'));
});
