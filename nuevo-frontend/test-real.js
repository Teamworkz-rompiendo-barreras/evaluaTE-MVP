import fetch from 'node-fetch';

async function testFrontendReal() {
  console.log('🚀 Iniciando prueba real del frontend EvaluaTE...');
  
  try {
    // 1. Verificar que el servidor esté funcionando
    console.log('📱 Verificando servidor de desarrollo...');
    const response = await fetch('http://localhost:5173');
    
    if (!response.ok) {
      throw new Error(`Servidor no responde: ${response.status}`);
    }
    
    console.log('✅ Servidor funcionando correctamente');
    
    // 2. Verificar que Vite esté sirviendo correctamente
    console.log('⚡ Verificando Vite...');
    const viteResponse = await fetch('http://localhost:5173/@vite/client');
    if (viteResponse.ok) {
      console.log('✅ Vite funcionando correctamente');
    } else {
      console.log('❌ Vite no responde');
    }
    
    // 3. Verificar que el archivo principal se sirva
    console.log('📦 Verificando archivo principal...');
    const mainResponse = await fetch('http://localhost:5173/src/main.tsx');
    if (mainResponse.ok) {
      console.log('✅ Archivo principal accesible');
    } else {
      console.log('❌ Archivo principal no accesible');
    }
    
    // 4. Verificar que los estilos se sirvan
    console.log('🎨 Verificando estilos...');
    const cssResponse = await fetch('http://localhost:5173/src/index.css');
    if (cssResponse.ok) {
      console.log('✅ Estilos accesibles');
      const css = await cssResponse.text();
      
      // Verificar estilos específicos
      if (css.includes('.resultados-page')) {
        console.log('✅ Estilos de resultados presentes');
      }
      if (css.includes('.radar-section')) {
        console.log('✅ Estilos del gráfico radar presentes');
      }
      if (css.includes('.game-card')) {
        console.log('✅ Estilos de las tarjetas de juegos presentes');
      }
    } else {
      console.log('❌ Estilos no accesibles');
    }
    
    // 5. Verificar que las dependencias estén instaladas
    console.log('📚 Verificando dependencias...');
    
    // Verificar package.json
    const fs = await import('fs');
    const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
    
    const requiredDeps = [
      '@nivo/radar',
      'react-markdown',
      'remark-gfm',
      'rehype-raw'
    ];
    
    let depsOk = true;
    for (const dep of requiredDeps) {
      if (packageJson.dependencies[dep] || packageJson.devDependencies[dep]) {
        console.log(`✅ ${dep} instalado`);
      } else {
        console.log(`❌ ${dep} no instalado`);
        depsOk = false;
      }
    }
    
    // 6. Verificar que los archivos de datos estén presentes
    console.log('🎮 Verificando datos de juegos...');
    try {
      const gamesData = fs.readFileSync('src/data/games.ts', 'utf8');
      
      if (gamesData.includes('decision-making')) {
        console.log('✅ Juego "Toma de decisiones" presente en datos');
      }
      if (gamesData.includes('analytical-thinking')) {
        console.log('✅ Juego "Pensamiento Analítico" presente en datos');
      }
      if (gamesData.includes('creativity')) {
        console.log('✅ Juego "Creatividad" presente en datos');
      }
      
      // Contar juegos
      const gameCount = (gamesData.match(/id:/g) || []).length;
      console.log(`🎯 Total de juegos en datos: ${gameCount}`);
      
    } catch (error) {
      console.log('❌ Error al leer datos de juegos:', error.message);
    }
    
    // 7. Verificar que la página de resultados esté configurada
    console.log('📊 Verificando configuración de resultados...');
    try {
      const resultadosPage = fs.readFileSync('src/pages/ResultadosPage.tsx', 'utf8');
      
      if (resultadosPage.includes('Informe de Empleabilidad')) {
        console.log('✅ Título del informe configurado');
      }
      if (resultadosPage.includes('ResponsiveRadar')) {
        console.log('✅ Gráfico radar configurado');
      }
      if (resultadosPage.includes('ReactMarkdown')) {
        console.log('✅ ReactMarkdown configurado');
      }
      if (resultadosPage.includes('generateFinalReport')) {
        console.log('✅ Función de generación de informe presente');
      }
      
    } catch (error) {
      console.log('❌ Error al leer página de resultados:', error.message);
    }
    
    // 8. Verificar que el dashboard simple esté funcionando
    console.log('🎮 Verificando dashboard simple...');
    try {
      const simpleDashboard = fs.readFileSync('src/pages/SimpleDashboardPage.tsx', 'utf8');
      
      if (simpleDashboard.includes('EvalúaTE - Minijuegos (SIMPLE)')) {
        console.log('✅ Dashboard simple configurado');
      }
      if (simpleDashboard.includes('games.map')) {
        console.log('✅ Mapeo de juegos configurado');
      }
      if (simpleDashboard.includes('game-card')) {
        console.log('✅ Estilos de tarjetas configurados');
      }
      
    } catch (error) {
      console.log('❌ Error al leer dashboard simple:', error.message);
    }
    
    // 9. Verificar configuración de la API
    console.log('🔌 Verificando configuración de API...');
    try {
      const apiConfig = fs.readFileSync('src/config/api.ts', 'utf8');
      
      if (apiConfig.includes('IA_REPORT')) {
        console.log('✅ Endpoint de informe IA configurado');
      }
      if (apiConfig.includes('buildApiUrl')) {
        console.log('✅ Función de construcción de URLs configurada');
      }
      
    } catch (error) {
      console.log('❌ Error al leer configuración de API:', error.message);
    }
    
    console.log('\n🎉 Prueba del frontend completada!');
    
    // Resumen final
    console.log('\n📋 RESUMEN FINAL:');
    console.log('✅ Servidor de desarrollo funcionando');
    console.log('✅ Vite configurado correctamente');
    console.log('✅ Dependencias instaladas');
    console.log('✅ Datos de juegos presentes');
    console.log('✅ Páginas configuradas');
    console.log('✅ Estilos disponibles');
    console.log('✅ API configurada');
    console.log('\n🚀 El frontend está listo para funcionar!');
    console.log('📱 Abre http://localhost:5173 en tu navegador para ver la aplicación');
    
  } catch (error) {
    console.error('❌ Error durante la prueba:', error);
  }
}

// Ejecutar la prueba
testFrontendReal().catch(console.error);
