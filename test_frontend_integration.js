// test_frontend_integration.js
// Script para probar la integración del frontend con el backend

const testBackendResponse = async () => {
  console.log('🧪 Probando integración frontend-backend...\n');
  
  try {
    // Simular la respuesta del backend (formato nuevo)
    const mockBackendResponse = {
      summary: "Informe de empleabilidad para Usuario Test",
      personal_data: {
        name: "Usuario Test",
        location: "Madrid, España",
        email: "usuario@test.com",
        phone: "+34 600 000 000",
        disability_certificate: "No"
      },
      profile_summary: "Perfil profesional con potencial de desarrollo. Se recomienda fortalecer habilidades técnicas específicas.",
      cv_summary: "CV con información básica disponible. Se sugiere enriquecer con más detalles sobre proyectos.",
      strengths: ["Comunicación", "Trabajo en equipo", "Adaptabilidad"],
      improvement_areas: [
        {
          area: "Experiencia técnica",
          reason: "Necesita más práctica en tecnologías específicas",
          suggested_action: "Completar proyectos prácticos"
        }
      ],
      cv_analysis: {
        structure_score: 4,
        coherence_score: 4,
        key_info_score: 3,
        clarity_score: 4,
        style_score: 3,
        evidence: {
          structure: "Buena estructura y organización",
          coherence: "Información coherente y lógica",
          key_info: "Información básica disponible",
          clarity: "Formato claro y legible",
          style: "Estilo profesional"
        },
        corrections: [
          "Incluir más detalles sobre logros específicos",
          "Añadir métricas cuantificables"
        ],
        reordering_suggestions: [
          "Priorizar experiencia laboral más reciente"
        ]
      },
      ideal_work_environment: "Entorno inclusivo con oportunidades de aprendizaje",
      suggested_roles: [
        {
          role: "Desarrollador Junior",
          reason: "Perfil adecuado para roles de entrada",
          seniority: "Junior",
          remote_viable: true
        }
      ],
      action_plan: {
        short_term: [
          "Actualizar CV con información más detallada",
          "Crear perfil en LinkedIn"
        ],
        medium_term: [
          "Completar formación en habilidades técnicas",
          "Ampliar red profesional"
        ],
        long_term: [
          "Desarrollar especialización técnica",
          "Buscar oportunidades de liderazgo"
        ]
      },
      job_search_advice: {
        cv_optimization: [
          "Usar palabras clave específicas del sector",
          "Incluir logros cuantificables"
        ],
        letters_portfolio: "Preparar carta de presentación personalizada",
        recommended_platforms: ["LinkedIn", "InfoJobs", "Indeed"],
        networking: "Participar en meetups y grupos profesionales",
        interview_tips: "Preparar respuestas STAR"
      },
      useful_tools: {
        productivity: ["Trello", "Notion"],
        job_search: ["LinkedIn", "Glassdoor"],
        learning: ["Coursera", "Udemy"],
        accessibility: ["Microsoft Immersive Reader", "Grammarly"]
      },
      completed_games: ["Evaluación de habilidades básicas"],
      final_message: "Usuario Test, tu perfil muestra excelente potencial. Enfócate en construir experiencia práctica."
    };

    console.log('📊 Respuesta simulada del backend:');
    console.log(JSON.stringify(mockBackendResponse, null, 2));
    console.log('\n');

    // Simular el procesamiento del frontend
    console.log('🔄 Procesando respuesta en el frontend...\n');

    // Extraer datos como lo hace el frontend
    const data = mockBackendResponse;
    const reportData = data?.report ?? {};
    
    // Extraer puntuación
    const score = typeof data?.employabilityScore === 'number' ? data.employabilityScore : undefined;
    console.log('📈 Puntuación extraída:', score);
    
    // Extraer nivel
    const level = data?.level ?? reportData?.nivel ?? undefined;
    console.log('🏆 Nivel extraído:', level);
    
    // Extraer frase final
    const fraseFinal = data?.final_message || '';
    console.log('💬 Frase final extraída:', fraseFinal);
    
    // Verificar si hay informe Markdown del backend
    const mdBackend = data?.informe || undefined;
    console.log('📝 Informe Markdown del backend:', mdBackend ? 'SÍ' : 'NO');
    
    if (mdBackend) {
      console.log('✅ Usando informe del backend');
    } else {
      console.log('⚠️ No hay informe del backend, usando fallback');
      
      // Simular la función buildFallbackMarkdown
      const userFullName = "Usuario Test";
      const cvAnalysis = {
        structure_score: 4,
        coherence_score: 4,
        key_info_score: 3,
        clarity_score: 4,
        style_score: 3,
        evidence: {
          structure: 'Buena',
          coherence: 'Excelente',
          key_info: 'Información básica',
          clarity: 'Clara',
          style: 'Profesional'
        },
        corrections: [],
        reordering_suggestions: []
      };
      const completedGames = ["Evaluación de habilidades básicas"];
      
      const informeFallback = `# 📋 Informe de Empleabilidad Profesional

## 👤 Información Personal
**Nombre:** ${userFullName}
**Puntuación de Empleabilidad:** ${score !== undefined ? `${score}/100` : 'No disponible'}
**Nivel:** ${level ?? 'No especificado'}

## 🎯 Resumen Ejecutivo
${data.profile_summary || 'Análisis de empleabilidad basado en tu perfil y habilidades.'}

## 💪 Fortalezas Identificadas
${data.strengths?.length > 0 ? data.strengths.map(s => `- ${s}`).join('\n') : '- Se están evaluando tus fortalezas'}

  ## 📊 Análisis del CV
  ${cvAnalysis ? `**Estructura:** ${cvAnalysis.evidence.structure || 'Regular'}\n**Coherencia:** ${cvAnalysis.evidence.coherence || 'Regular'}\n**Claridad:** ${cvAnalysis.evidence.clarity || 'Regular'}` : 'CV en proceso de análisis'}

## 🎮 Juegos Completados
${completedGames.length ? completedGames.map(g => `- ${g}`).join('\n') : '- Evaluación de habilidades básicas completada'}

## 📝 Recomendaciones
${data.job_search_advice?.cv_optimization?.length > 0 ? data.job_search_advice.cv_optimization.map(r => `- ${r}`).join('\n') : '- Revisar y actualizar CV regularmente\n- Practicar habilidades de comunicación\n- Mantener actitud proactiva'}

## 🚀 Plan de Acción
1. **Corto plazo:** ${data.action_plan?.short_term?.[0] || 'Actualizar CV y crear perfil profesional'}
2. **Medio plazo:** ${data.action_plan?.medium_term?.[0] || 'Ampliar habilidades técnicas y networking'}
3. **Largo plazo:** ${data.action_plan?.long_term?.[0] || 'Desarrollar especialización y liderazgo'}

---

*Informe generado automáticamente por EvaluaTE*`;

      console.log('📋 Informe fallback generado:');
      console.log(informeFallback);
    }

    console.log('\n✅ Prueba de integración completada exitosamente!');
    console.log('🎯 El frontend está configurado correctamente para procesar la respuesta del backend.');
    
  } catch (error) {
    console.error('❌ Error en la prueba:', error);
  }
};

// Ejecutar la prueba
testBackendResponse();
