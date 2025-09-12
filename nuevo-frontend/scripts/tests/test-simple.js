import fetch from 'node-fetch';

async function testFrontendSimple() {
  console.log('🚀 Iniciando prueba simple del frontend EvaluaTE...');
  
  try {
    // 1. Probar que el servidor esté funcionando
    console.log('📱 Verificando que el servidor esté funcionando...');
    const response = await fetch('http://localhost:5173');
    
    if (response.ok) {
      console.log('✅ Servidor funcionando correctamente');
      const html = await response.text();
      
      // Verificar que el título sea correcto
      if (html.includes('EvalúaTE')) {
        console.log('✅ Título de la página correcto');
      } else {
        console.log('❌ Título de la página incorrecto');
      }
      
      // Verificar que se cargue React
      if (html.includes('react') || html.includes('React')) {
        console.log('✅ React detectado en la página');
      } else {
        console.log('❌ React no detectado');
      }
      
    } else {
      console.log(`❌ Error del servidor: ${response.status}`);
    }
    
    // 2. Probar la página de resultados (debería dar error 404 o redirigir)
    console.log('🎯 Probando acceso directo a resultados...');
    try {
      const resultadosResponse = await fetch('http://localhost:5173/resultados');
      console.log(`📊 Respuesta de resultados: ${resultadosResponse.status}`);
      
      if (resultadosResponse.status === 200) {
        console.log('✅ Página de resultados accesible');
      } else if (resultadosResponse.status === 404) {
        console.log('ℹ️ Página de resultados no encontrada (esperado sin autenticación)');
      } else {
        console.log(`ℹ️ Respuesta inesperada: ${resultadosResponse.status}`);
      }
    } catch (error) {
      console.log('ℹ️ Error al acceder a resultados (esperado sin autenticación):', error.message);
    }
    
    // 3. Probar la página de juegos
    console.log('🎮 Probando acceso directo a juegos...');
    try {
      const juegosResponse = await fetch('http://localhost:5173/games');
      console.log(`🎮 Respuesta de juegos: ${juegosResponse.status}`);
      
      if (juegosResponse.status === 200) {
        console.log('✅ Página de juegos accesible');
      } else if (juegosResponse.status === 404) {
        console.log('ℹ️ Página de juegos no encontrada (esperado sin autenticación)');
      } else {
        console.log(`ℹ️ Respuesta inesperada: ${juegosResponse.status}`);
      }
    } catch (error) {
      console.log('ℹ️ Error al acceder a juegos (esperado sin autenticación):', error.message);
    }
    
    // 4. Verificar que los assets estén disponibles
    console.log('📦 Verificando assets...');
    try {
      const mainJsResponse = await fetch('http://localhost:5173/src/main.tsx');
      if (mainJsResponse.ok) {
        console.log('✅ Archivo principal TypeScript accesible');
      } else {
        console.log('❌ Archivo principal TypeScript no accesible');
      }
    } catch (error) {
      console.log('ℹ️ Error al acceder a main.tsx:', error.message);
    }
    
    // 5. Verificar que el CSS esté disponible
    try {
      const cssResponse = await fetch('http://localhost:5173/src/index.css');
      if (cssResponse.ok) {
        console.log('✅ Archivo CSS accesible');
      } else {
        console.log('❌ Archivo CSS no accesible');
      }
    } catch (error) {
      console.log('ℹ️ Error al acceder a CSS:', error.message);
    }
    
    console.log('🎉 Prueba simple del frontend completada!');
    
  } catch (error) {
    console.error('❌ Error durante la prueba:', error);
  }
}

// Ejecutar la prueba
testFrontendSimple().catch(console.error);
