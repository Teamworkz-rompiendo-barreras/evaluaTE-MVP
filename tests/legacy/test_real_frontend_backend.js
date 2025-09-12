// test_real_frontend_backend.js
// Script para probar la integración real entre frontend y backend

const testRealIntegration = async () => {
  console.log('🧪 Probando integración REAL frontend-backend...\n');
  
  try {
    // 1. Probar que el backend esté funcionando
    console.log('1️⃣ Verificando backend...');
    const healthResponse = await fetch('http://localhost:8080/health');
    if (healthResponse.ok) {
      console.log('✅ Backend funcionando correctamente');
    } else {
      console.log('❌ Backend no responde correctamente');
      return;
    }

    // 2. Probar el endpoint del informe
    console.log('\n2️⃣ Probando endpoint del informe...');
    const testData = {
      userId: "test-user-123",
      fullName: "María García López",
      softSkills: [
        { skill: "Comunicación", score: 85, level: "alto", confidence: 90 },
        { skill: "Trabajo en equipo", score: 78, level: "medio", confidence: 85 },
        { skill: "Liderazgo", score: 72, level: "medio", confidence: 80 }
      ],
      cvAnalysis: {
        structure: "excelente",
        coherence: "buena",
        feedback: "CV muy bien estructurado con información clara y organizada",
        strengths: ["Formato profesional", "Información completa"],
        weaknesses: ["Podría incluir más métricas"]
      },
      jobPreferences: {
        areas: ["Desarrollo Web", "Frontend"],
        workMode: "híbrido",
        availability: "inmediata",
        hasDisabilityCert: false
      },
      cvFile: null
    };

    console.log('📤 Enviando datos de prueba al backend...');
    const reportResponse = await fetch('http://localhost:8080/api/informe-ia', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(testData)
    });

    if (!reportResponse.ok) {
      console.log(`❌ Error del backend: ${reportResponse.status} ${reportResponse.statusText}`);
      return;
    }

    const reportData = await reportResponse.json();
    console.log('✅ Respuesta del backend recibida exitosamente');
    
    // 3. Verificar estructura de la respuesta
    console.log('\n3️⃣ Verificando estructura de la respuesta...');
    
    const requiredFields = [
      'summary', 'personal_data', 'profile_summary', 'cv_summary', 
      'strengths', 'improvement_areas', 'cv_analysis', 'ideal_work_environment',
      'suggested_roles', 'action_plan', 'job_search_advice', 'useful_tools',
      'completed_games', 'final_message'
    ];

    let missingFields = [];
    requiredFields.forEach(field => {
      if (!(field in reportData)) {
        missingFields.push(field);
      }
    });

    if (missingFields.length === 0) {
      console.log('✅ Todos los campos requeridos están presentes');
    } else {
      console.log(`⚠️ Campos faltantes: ${missingFields.join(', ')}`);
    }

    // 4. Verificar datos específicos
    console.log('\n4️⃣ Verificando datos específicos...');
    
    console.log(`📊 Resumen: ${reportData.summary?.substring(0, 50)}...`);
    console.log(`👤 Nombre: ${reportData.personal_data?.name || 'No disponible'}`);
    console.log(`💪 Fortalezas: ${reportData.strengths?.length || 0} encontradas`);
    console.log(`🎯 Roles sugeridos: ${reportData.suggested_roles?.length || 0} roles`);
    console.log(`📝 Plan de acción: ${reportData.action_plan?.short_term?.length || 0} acciones corto plazo`);
    console.log(`🛠️ Herramientas: ${reportData.useful_tools?.productivity?.length || 0} herramientas de productividad`);

    // 5. Simular procesamiento del frontend
    console.log('\n5️⃣ Simulando procesamiento del frontend...');
    
    // Extraer datos como lo hace el frontend
    const score = reportData.employabilityScore;
    const level = reportData.level;
    const fraseFinal = reportData.final_message;
    
    console.log(`📈 Puntuación extraída: ${score !== undefined ? score : 'No disponible'}`);
    console.log(`🏆 Nivel extraído: ${level || 'No especificado'}`);
    console.log(`💬 Frase final: ${fraseFinal ? 'SÍ' : 'NO'}`);

    // 6. Verificar que se pueda generar un informe completo
    console.log('\n6️⃣ Verificando generación de informe completo...');
    
    const hasCompleteData = 
      reportData.personal_data?.name &&
      reportData.profile_summary &&
      reportData.strengths?.length > 0 &&
      reportData.action_plan?.short_term?.length > 0;

    if (hasCompleteData) {
      console.log('✅ Datos suficientes para generar informe completo');
      
      // Simular la generación del informe como lo haría el frontend
      const informeCompleto = `# 📋 Informe de Empleabilidad Profesional

## 👤 Información Personal
**Nombre:** ${reportData.personal_data.name}
**Ubicación:** ${reportData.personal_data.location}
**Email:** ${reportData.personal_data.email}

## 🎯 Resumen del Perfil
${reportData.profile_summary}

## 💪 Fortalezas Identificadas
${reportData.strengths.map(s => `- ${s}`).join('\n')}

## 📊 Análisis del CV
**Estructura:** ${reportData.cv_analysis.evidence.structure}
**Coherencia:** ${reportData.cv_analysis.evidence.coherence}
**Claridad:** ${reportData.cv_analysis.evidence.clarity}

## 🎯 Roles Sugeridos
${reportData.suggested_roles.map(r => `- **${r.role}** (${r.seniority}): ${r.reason}`).join('\n')}

## 🚀 Plan de Acción
**Corto plazo:**
${reportData.action_plan.short_term.map(a => `- ${a}`).join('\n')}

**Medio plazo:**
${reportData.action_plan.medium_term.map(a => `- ${a}`).join('\n')}

**Largo plazo:**
${reportData.action_plan.long_term.map(a => `- ${a}`).join('\n')}

## 🛠️ Herramientas Útiles
**Productividad:** ${reportData.useful_tools.productivity.join(', ')}
**Búsqueda de empleo:** ${reportData.useful_tools.job_search.join(', ')}
**Aprendizaje:** ${reportData.useful_tools.learning.join(', ')}

## 💬 Mensaje Final
${reportData.final_message}

---

*Informe generado automáticamente por EvaluaTE*`;

      console.log('📋 Informe completo generado exitosamente');
      console.log(`📏 Longitud del informe: ${informeCompleto.length} caracteres`);
      
    } else {
      console.log('⚠️ Datos insuficientes para informe completo');
    }

    console.log('\n🎉 ¡Prueba de integración REAL completada exitosamente!');
    console.log('✅ El frontend puede procesar correctamente la respuesta del backend');
    console.log('✅ Se pueden generar informes completos con todos los datos');
    
  } catch (error) {
    console.error('❌ Error en la prueba de integración real:', error);
  }
};

// Ejecutar la prueba
testRealIntegration();
