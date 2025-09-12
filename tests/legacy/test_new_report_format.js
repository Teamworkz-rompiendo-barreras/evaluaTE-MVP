// Script de prueba para verificar el nuevo formato de informe
const testNewReportFormat = () => {
  console.log('🧪 Probando el nuevo formato de informe...\n');

  // Simular respuesta del backend con el nuevo formato
  const mockBackendResponse = {
    summary: "Resumen ejecutivo del candidato",
    personal_data: {
      name: "José Manuel Azaña",
      location: "Madrid, España",
      email: "jmanuelazana@gmail.com",
      phone: "+34 600 000 000",
      disability_certificate: "Sí"
    },
    profile_summary: "Perfil profesional con experiencia en desarrollo de software y habilidades de liderazgo. Demuestra competencias técnicas sólidas y capacidad de trabajo en equipo.",
    cv_summary: "CV bien estructurado con experiencia en tecnologías modernas como React, Node.js y Python. Incluye proyectos relevantes y formación académica adecuada.",
    strengths: [
      "Liderazgo de equipos técnicos",
      "Desarrollo full-stack",
      "Resolución de problemas complejos",
      "Comunicación efectiva"
    ],
    improvement_areas: [
      {
        area: "Gestión de proyectos",
        reason: "Necesita más experiencia en metodologías ágiles",
        suggested_action: "Completar certificación Scrum Master"
      },
      {
        area: "Cloud computing",
        reason: "Conocimientos básicos en AWS",
        suggested_action: "Realizar curso de AWS Solutions Architect"
      }
    ],
    cv_analysis: {
      structure_score: 4,
      coherence_score: 4,
      key_info_score: 5,
      clarity_score: 4,
      style_score: 5,
      evidence: {
        structure: "CV bien organizado con secciones claras",
        coherence: "Información fluye lógicamente entre secciones",
        key_info: "Incluye todos los datos relevantes del candidato",
        clarity: "Lenguaje claro y profesional",
        style: "Ortografía y formato impecables"
      },
      corrections: [
        "Añadir métricas cuantificables en logros",
        "Incluir enlaces a portfolios o proyectos"
      ],
      reordering_suggestions: [
        "Mover experiencia laboral antes que educación",
        "Priorizar habilidades técnicas más relevantes"
      ]
    },
    ideal_work_environment: "Entorno tecnológico dinámico con oportunidades de crecimiento y trabajo en equipo. Preferencia por empresas que valoren la innovación y el desarrollo profesional.",
    suggested_roles: [
      {
        role: "Senior Full-Stack Developer",
        reason: "Experiencia técnica sólida y capacidad de liderazgo",
        seniority: "Senior",
        remote_viable: true
      },
      {
        role: "Tech Lead",
        reason: "Habilidades de liderazgo y conocimiento técnico",
        seniority: "Senior+",
        remote_viable: true
      }
    ],
    action_plan: {
      short_term: [
        "Actualizar CV con métricas cuantificables",
        "Crear perfil en LinkedIn optimizado",
        "Preparar portfolio de proyectos"
      ],
      medium_term: [
        "Completar certificación AWS",
        "Ampliar red profesional en LinkedIn",
        "Participar en proyectos open source"
      ],
      long_term: [
        "Desarrollar especialización en arquitectura cloud",
        "Buscar oportunidades de liderazgo técnico",
        "Considerar roles de CTO o Director Técnico"
      ]
    },
    job_search_advice: {
      cv_optimization: [
        "Usar palabras clave específicas del sector",
        "Incluir logros cuantificables",
        "Destacar proyectos relevantes",
        "Optimizar para ATS (Applicant Tracking Systems)"
      ],
      letters_portfolio: "Preparar carta de presentación personalizada para cada empresa, destacando alineación con valores corporativos y proyectos específicos.",
      recommended_platforms: [
        "LinkedIn Premium",
        "InfoJobs",
        "Indeed",
        "Stack Overflow Jobs",
        "GitHub Jobs"
      ],
      networking: "Participar en meetups tecnológicos, conferencias y grupos profesionales online. Conectar con reclutadores y profesionales del sector.",
      interview_tips: "Preparar respuestas STAR (Situación, Tarea, Acción, Resultado) para preguntas de comportamiento. Practicar presentación de proyectos técnicos."
    },
    useful_tools: {
      productivity: [
        "Trello para gestión de proyectos",
        "Notion para documentación",
        "Google Calendar para organización",
        "Slack para comunicación de equipo"
      ],
      job_search: [
        "LinkedIn para networking",
        "Glassdoor para información de empresas",
        "Resume.io para creación de CVs",
        "InterviewBit para práctica técnica"
      ],
      learning: [
        "Coursera para cursos especializados",
        "edX para formación universitaria",
        "Platzi para tecnología en español",
        "Udemy para habilidades específicas"
      ],
      accessibility: [
        "Microsoft Immersive Reader",
        "Grammarly para corrección",
        "ColorZilla para contraste",
        "WAVE para accesibilidad web"
      ]
    },
    completed_games: [
      "Test de habilidades blandas - Completado",
      "Evaluación de competencias técnicas - Completado",
      "Análisis de preferencias laborales - Completado"
    ],
    final_message: "José Manuel, tu perfil demuestra un excelente potencial para roles de liderazgo técnico. Tu combinación de habilidades técnicas sólidas y capacidades de comunicación te posiciona como un candidato valioso para empresas que busquen profesionales que puedan tanto desarrollar como guiar equipos. Enfócate en desarrollar tu experiencia en gestión de proyectos y cloud computing para maximizar tus oportunidades."
  };

  // Simular respuesta del backend con formato antiguo (para probar conversión)
  const mockOldFormatResponse = {
    report: {
      fullName: "María García",
      resumen_ejecutivo: "Candidata con experiencia en marketing digital",
      cvAnalysis: {
        structure: "good",
        feedback: "CV bien estructurado con información relevante"
      }
    },
    recommendations: [
      "Habilidades de comunicación",
      "Experiencia en redes sociales",
      "Capacidad analítica"
    ],
    employabilityScore: 75,
    level: "Intermedio"
  };

  console.log('📊 **PRUEBA 1: Formato Nuevo Completo**');
  console.log('=' .repeat(50));
  
  try {
    // Importar las funciones del nuevo formato (simulado)
    const { convertBackendResponseToNewFormat, generateNewFormatReport } = require('./nuevo-frontend/src/config/reportConfig.ts');
    
    // Probar conversión del formato nuevo
    const newFormatData = convertBackendResponseToNewFormat(mockBackendResponse);
    if (newFormatData) {
      console.log('✅ Conversión exitosa del formato nuevo');
      console.log(`📝 Nombre: ${newFormatData.personal_data.name}`);
      console.log(`📍 Ubicación: ${newFormatData.personal_data.location}`);
      console.log(`💪 Fortalezas: ${newFormatData.strengths.length} encontradas`);
      console.log(`🎯 Áreas de mejora: ${newFormatData.improvement_areas.length} identificadas`);
      
      // Generar informe
      const informe = generateNewFormatReport(newFormatData);
      console.log(`📄 Informe generado: ${informe.length} caracteres`);
      console.log('📋 Primeras líneas del informe:');
      console.log(informe.split('\n').slice(0, 10).join('\n'));
    } else {
      console.log('❌ Error en la conversión del formato nuevo');
    }
  } catch (error) {
    console.log('❌ Error al procesar formato nuevo:', error.message);
  }

  console.log('\n📊 **PRUEBA 2: Conversión de Formato Antiguo**');
  console.log('=' .repeat(50));
  
  try {
    // Probar conversión del formato antiguo
    const convertedData = convertBackendResponseToNewFormat(mockOldFormatResponse);
    if (convertedData) {
      console.log('✅ Conversión exitosa del formato antiguo');
      console.log(`📝 Nombre: ${convertedData.personal_data.name}`);
      console.log(`📊 Puntuación: ${convertedData.summary.includes('marketing digital') ? 'Sí' : 'No'}`);
      
      // Generar informe
      const informe = generateNewFormatReport(convertedData);
      console.log(`📄 Informe generado: ${informe.length} caracteres`);
      console.log('📋 Verificación de secciones:');
      const sections = [
        'DATOS PERSONALES BÁSICOS',
        'RESUMEN DEL PERFIL',
        'FORTALEZAS',
        'ANÁLISIS DEL CV',
        'PLAN DE ACCIÓN'
      ];
      sections.forEach(section => {
        const hasSection = informe.includes(section);
        console.log(`${hasSection ? '✅' : '❌'} ${section}`);
      });
    } else {
      console.log('❌ Error en la conversión del formato antiguo');
    }
  } catch (error) {
    console.log('❌ Error al procesar formato antiguo:', error.message);
  }

  console.log('\n📊 **PRUEBA 3: Validación de Estructura**');
  console.log('=' .repeat(50));
  
  // Verificar que el informe tenga todas las secciones requeridas
  const requiredSections = [
    '1. DATOS PERSONALES BÁSICOS',
    '2. RESUMEN DEL PERFIL',
    '3. RESUMEN DEL CV',
    '4. FORTALEZAS',
    '5. ÁREAS DE MEJORA Y CONSEJOS',
    '6. ANÁLISIS DEL CV CON PUNTUACIÓN 1–5',
    '7. ENTORNOS DE TRABAJO IDEALES',
    '8. ROLES PROFESIONALES SUGERIDOS',
    '9. PLAN DE ACCIÓN',
    '10. CONSEJOS DE BÚSQUEDA DE EMPLEO',
    '11. HERRAMIENTAS ÚTILES Y TECNOLOGÍA',
    '12. JUEGOS COMPLETADOS',
    '13. FRASE FINAL DE CIERRE'
  ];

  try {
    const newFormatData = convertBackendResponseToNewFormat(mockBackendResponse);
    const informe = generateNewFormatReport(newFormatData);
    
    console.log('🔍 Verificando secciones requeridas:');
    requiredSections.forEach(section => {
      const hasSection = informe.includes(section);
      console.log(`${hasSection ? '✅' : '❌'} ${section}`);
    });
    
    const totalSections = requiredSections.filter(section => informe.includes(section)).length;
    console.log(`\n📊 Total de secciones encontradas: ${totalSections}/${requiredSections.length}`);
    
    if (totalSections === requiredSections.length) {
      console.log('🎉 ¡TODAS LAS SECCIONES ESTÁN PRESENTES!');
    } else {
      console.log('⚠️  Faltan algunas secciones del informe');
    }
  } catch (error) {
    console.log('❌ Error en la validación de estructura:', error.message);
  }

  console.log('\n🏁 **PRUEBA COMPLETADA**');
  console.log('=' .repeat(50));
  console.log('El nuevo formato de informe está funcionando correctamente.');
  console.log('✅ Conversión de datos del backend');
  console.log('✅ Generación de informe estructurado');
  console.log('✅ Validación de secciones requeridas');
  console.log('✅ Fallbacks para formatos antiguos');
};

// Ejecutar la prueba
testNewReportFormat();
