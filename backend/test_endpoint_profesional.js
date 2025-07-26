// test_endpoint_profesional.js
const axios = require('axios');

async function testEndpointProfesional() {
  console.log('🧪 Probando endpoint /api/informe-ia con informe profesional...');
  
  const testData = {
    preferences: {
      fullName: "Ana Martínez Rodríguez",
      userId: "user123",
      areas: ["grabadora de datos"],
      needs: ["Entorno tranquilo", "Instrucciones claras"],
      workMode: "presencial",
      availability: "completa",
      willingToRelocate: false,
      hasDisabilityCert: true
    },
    minigames: [
      {
        skill: "Toma de decisiones",
        score: 35,
        level: "Bajo",
        confidence: 75
      },
      {
        skill: "Pensamiento analítico",
        score: 70,
        level: "Medio",
        confidence: 85
      },
      {
        skill: "Creatividad",
        score: 32,
        level: "Bajo",
        confidence: 60
      },
      {
        skill: "Influencia social",
        score: 22,
        level: "Bajo",
        confidence: 70
      },
      {
        skill: "Curiosidad y aprendizaje",
        score: 83,
        level: "Alto",
        confidence: 90
      },
      {
        skill: "Resiliencia y flexibilidad",
        score: 45,
        level: "Bajo",
        confidence: 65
      }
    ],
    cvAnalysis: {
      structure: "regular",
      coherence: "regular",
      experience: "regular",
      skills: ["Excel", "Grabación de datos", "Trabajo en equipo"],
      strengths: [
        "Experiencia en grabación de datos",
        "Conocimientos básicos de Excel",
        "Capacidad de trabajo en equipo"
      ],
      weaknesses: [
        "Falta de experiencia en roles de liderazgo",
        "Necesita mejorar habilidades de comunicación",
        "CV podría ser más detallado"
      ],
      education: ["Bachillerato", "Curso básico de informática"],
      feedback: "CV funcional pero con oportunidades de mejora"
    }
  };
  
  try {
    console.log('📡 Enviando datos al endpoint...');
    const response = await axios.post('http://localhost:8000/api/informe-ia', testData, {
      headers: {
        'Content-Type': 'application/json'
      },
      timeout: 120000 // 2 minutos de timeout
    });
    
    console.log('✅ Respuesta recibida exitosamente!');
    console.log('📊 Longitud del informe:', response.data.informe?.length || 0, 'caracteres');
    
    // Verificar que el informe contiene las secciones profesionales
    const informe = response.data.informe || '';
    const secciones_esperadas = [
      'RESUMEN EJECUTIVO',
      'ANÁLISIS DE COMPETENCIAS',
      'PREFERENCIAS Y MOTIVACIONES',
      'RECOMENDACIONES',
      'CONCLUSIONES'
    ];
    
    console.log('\n🔍 Verificando secciones del informe:');
    secciones_esperadas.forEach(seccion => {
      if (informe.toUpperCase().includes(seccion)) {
        console.log(`✅ ${seccion} - ENCONTRADA`);
      } else {
        console.log(`❌ ${seccion} - NO ENCONTRADA`);
      }
    });
    
    // Mostrar las primeras líneas del informe
    console.log('\n📋 Primeras líneas del informe:');
    console.log('='.repeat(80));
    console.log(informe.substring(0, 500) + '...');
    console.log('='.repeat(80));
    
    if (informe.length > 1000) {
      console.log('🎉 ¡El informe es sustancialmente más largo y detallado!');
    } else {
      console.log('⚠️ El informe parece ser corto, podría necesitar ajustes');
    }
    
  } catch (error) {
    console.error('❌ Error en la prueba:', error.message);
    if (error.response) {
      console.error('📋 Respuesta del servidor:', error.response.data);
      console.error('📋 Status:', error.response.status);
    }
  }
}

// Ejecutar la prueba
testEndpointProfesional(); 