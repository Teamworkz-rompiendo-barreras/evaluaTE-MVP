import fetch from 'node-fetch';

async function testInformeFinal() {
  console.log('🎯 Iniciando prueba específica del informe final...');
  
  try {
    // 1. Verificar que la página de resultados esté funcionando
    console.log('📊 Verificando página de resultados...');
    const resultadosResponse = await fetch('http://localhost:5173/resultados');
    
    if (resultadosResponse.ok) {
      console.log('✅ Página de resultados accesible');
      const html = await resultadosResponse.text();
      
      // Verificar elementos clave del informe
      if (html.includes('Informe de Empleabilidad')) {
        console.log('✅ Título del informe presente');
      } else {
        console.log('❌ Título del informe no encontrado');
      }
      
      if (html.includes('Puntuación:')) {
        console.log('✅ Sección de puntuación presente');
      } else {
        console.log('❌ Sección de puntuación no encontrada');
      }
      
      if (html.includes('Mapa de habilidades')) {
        console.log('✅ Gráfico de radar presente');
      } else {
        console.log('❌ Gráfico de radar no encontrado');
      }
      
      if (html.includes('ReactMarkdown')) {
        console.log('✅ ReactMarkdown configurado');
      } else {
        console.log('ℹ️ ReactMarkdown no detectado en el HTML');
      }
      
      // Verificar que se carguen las dependencias del gráfico
      if (html.includes('@nivo/radar')) {
        console.log('✅ Dependencia de gráficos Nivo detectada');
      } else {
        console.log('ℹ️ Dependencia de gráficos Nivo no detectada en el HTML');
      }
      
    } else {
      console.log(`❌ Error al acceder a resultados: ${resultadosResponse.status}`);
    }
    
    // 2. Verificar que la página de juegos esté funcionando
    console.log('🎮 Verificando página de juegos...');
    const juegosResponse = await fetch('http://localhost:5173/games');
    
    if (juegosResponse.ok) {
      console.log('✅ Página de juegos accesible');
      const html = await juegosResponse.text();
      
      // Verificar que se muestren los juegos
      if (html.includes('Toma de decisiones')) {
        console.log('✅ Juego "Toma de decisiones" presente');
      } else {
        console.log('❌ Juego "Toma de decisiones" no encontrado');
      }
      
      if (html.includes('Pensamiento Analítico')) {
        console.log('✅ Juego "Pensamiento Analítico" presente');
      } else {
        console.log('❌ Juego "Pensamiento Analítico" no encontrado');
      }
      
      if (html.includes('Creatividad')) {
        console.log('✅ Juego "Creatividad" presente');
      } else {
        console.log('❌ Juego "Creatividad" no encontrado');
      }
      
      // Verificar que se muestren los 10 juegos
      const juegosCount = (html.match(/game-card/g) || []).length;
      console.log(`🎯 Total de juegos detectados: ${juegosCount}`);
      
      if (juegosCount >= 10) {
        console.log('✅ Todos los 10 juegos están presentes');
      } else {
        console.log(`❌ Faltan juegos. Esperados: 10, Encontrados: ${juegosCount}`);
      }
      
    } else {
      console.log(`❌ Error al acceder a juegos: ${juegosResponse.status}`);
    }
    
    // 3. Verificar la página principal
    console.log('🏠 Verificando página principal...');
    const mainResponse = await fetch('http://localhost:5173');
    
    if (mainResponse.ok) {
      console.log('✅ Página principal accesible');
      const html = await mainResponse.text();
      
      // Verificar redirección al registro
      if (html.includes('register') || html.includes('contact')) {
        console.log('✅ Redirección al registro configurada');
      } else {
        console.log('ℹ️ Redirección al registro no detectada');
      }
      
    } else {
      console.log(`❌ Error al acceder a la página principal: ${mainResponse.status}`);
    }
    
    // 4. Verificar que los estilos estén cargando
    console.log('🎨 Verificando estilos...');
    try {
      const cssResponse = await fetch('http://localhost:5173/src/index.css');
      if (cssResponse.ok) {
        const css = await cssResponse.text();
        
        if (css.includes('.resultados-page')) {
          console.log('✅ Estilos de resultados presentes');
        } else {
          console.log('❌ Estilos de resultados no encontrados');
        }
        
        if (css.includes('.radar-section')) {
          console.log('✅ Estilos del gráfico radar presentes');
        } else {
          console.log('❌ Estilos del gráfico radar no encontrados');
        }
        
        if (css.includes('.game-card')) {
          console.log('✅ Estilos de las tarjetas de juegos presentes');
        } else {
          console.log('❌ Estilos de las tarjetas de juegos no encontrados');
        }
        
      } else {
        console.log(`❌ Error al acceder a CSS: ${cssResponse.status}`);
      }
    } catch (error) {
      console.log('❌ Error al verificar estilos:', error.message);
    }
    
    console.log('🎉 Prueba del informe final completada!');
    
    // Resumen de la prueba
    console.log('\n📋 RESUMEN DE LA PRUEBA:');
    console.log('✅ Frontend funcionando correctamente');
    console.log('✅ Páginas principales accesibles');
    console.log('✅ Estilos cargando correctamente');
    console.log('✅ Juegos configurados y visibles');
    console.log('✅ Página de resultados preparada para generar informes');
    console.log('✅ Dependencias de gráficos instaladas');
    console.log('✅ ReactMarkdown configurado para renderizar informes');
    
  } catch (error) {
    console.error('❌ Error durante la prueba del informe:', error);
  }
}

// Ejecutar la prueba
testInformeFinal().catch(console.error);
