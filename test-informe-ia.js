const fetch = require('node-fetch');

async function testInformeIA() {
    console.log('🧪 Probando generación de informe IA...\n');
    
    const requestBody = {
        userId: 'test-user-123',
        fullName: 'Usuario de Prueba',
        softSkills: [
            {
                skill: 'Comunicación',
                score: 85,
                level: 'Alto',
                confidence: 90
            },
            {
                skill: 'Trabajo en equipo',
                score: 78,
                level: 'Medio',
                confidence: 85
            },
            {
                skill: 'Resolución de problemas',
                score: 92,
                level: 'Alto',
                confidence: 88
            }
        ],
        cvAnalysis: {
            strengths: ['Experiencia en desarrollo web', 'Conocimientos de JavaScript'],
            weaknesses: ['Falta de experiencia en gestión de proyectos'],
            feedback: 'CV bien estructurado con buenas habilidades técnicas',
            structure: 'buena',
            coherence: 'excelente',
            experience: 'regular',
            skills: ['JavaScript', 'React', 'Node.js'],
            education: ['Ingeniería Informática'],
            alerts: []
        },
        jobPreferences: {
            areas: ['Desarrollo web', 'Frontend'],
            needs: ['Trabajo remoto', 'Flexibilidad horaria'],
            workMode: 'remoto',
            availability: 'completa',
            willingToRelocate: true,
            hasDisabilityCert: false
        },
        completedGames: ['decision-making', 'analytical-thinking', 'creativity'],
        logs: []
    };

    try {
        console.log('📤 Enviando solicitud al backend...');
        console.log('URL: http://localhost:8000/api/informe-ia');
        console.log('Datos enviados:', JSON.stringify(requestBody, null, 2));
        
        const response = await fetch('http://localhost:8000/api/informe-ia', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });

        console.log('\n📥 Respuesta del servidor:');
        console.log('Status:', response.status);
        console.log('Status Text:', response.statusText);
        console.log('Headers:', Object.fromEntries(response.headers.entries()));

        if (!response.ok) {
            const errorText = await response.text();
            console.log('\n❌ Error en la respuesta:');
            console.log(errorText);
            return;
        }

        const data = await response.json();
        console.log('\n✅ Respuesta exitosa:');
        console.log('Estructura de la respuesta:', Object.keys(data));
        console.log('\n📋 Contenido completo:');
        console.log(JSON.stringify(data, null, 2));

        // Verificar si hay problemas con las propiedades
        console.log('\n🔍 Verificación de propiedades:');
        console.log('• data.report:', data.report ? '✅ Existe' : '❌ No existe');
        if (data.report) {
            console.log('• data.report.jobPreferences:', data.report.jobPreferences ? '✅ Existe' : '❌ No existe');
            if (data.report.jobPreferences) {
                console.log('• data.report.jobPreferences.areas:', data.report.jobPreferences.areas ? '✅ Existe' : '❌ No existe');
                if (data.report.jobPreferences.areas) {
                    console.log('• Es array:', Array.isArray(data.report.jobPreferences.areas) ? '✅ Sí' : '❌ No');
                }
            }
        }
        console.log('• data.recommendations:', data.recommendations ? '✅ Existe' : '❌ No existe');
        console.log('• data.summary:', data.summary ? '✅ Existe' : '❌ No existe');

    } catch (error) {
        console.log('\n💥 Error en la petición:');
        console.log('Error:', error.message);
        console.log('Stack:', error.stack);
    }
}

// Ejecutar la prueba
testInformeIA();
