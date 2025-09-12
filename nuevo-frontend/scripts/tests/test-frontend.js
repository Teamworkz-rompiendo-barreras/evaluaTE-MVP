import puppeteer from 'puppeteer';

async function testFrontend() {
  console.log('🚀 Iniciando prueba del frontend EvaluaTE...');
  
  const browser = await puppeteer.launch({ 
    headless: false, 
    slowMo: 1000,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  try {
    const page = await browser.newPage();
    
    // Configurar viewport
    await page.setViewport({ width: 1280, height: 720 });
    
    console.log('📱 Navegando al frontend...');
    await page.goto('http://localhost:5173', { waitUntil: 'networkidle0' });
    
    // Esperar a que cargue la página de registro
    await page.waitForSelector('h1', { timeout: 10000 });
    
    console.log('✅ Página cargada correctamente');
    
    // Verificar que estamos en la página de registro
    const title = await page.$eval('h1', el => el.textContent);
    console.log(`📋 Título de la página: ${title}`);
    
    // Simular llenado de datos personales
    console.log('👤 Llenando datos personales...');
    
    // Buscar campos de formulario
    const nameInput = await page.$('input[name="firstName"], input[placeholder*="nombre"], input[placeholder*="Nombre"]');
    const lastNameInput = await page.$('input[name="lastName"], input[placeholder*="apellido"], input[placeholder*="Apellido"]');
    const emailInput = await page.$('input[name="email"], input[type="email"], input[placeholder*="email"]');
    
    if (nameInput) {
      await nameInput.type('Juan');
      console.log('✅ Nombre ingresado');
    }
    
    if (lastNameInput) {
      await lastNameInput.type('Pérez');
      console.log('✅ Apellido ingresado');
    }
    
    if (emailInput) {
      await emailInput.type('juan.perez@test.com');
      console.log('✅ Email ingresado');
    }
    
    // Buscar botón de continuar
    const continueButton = await page.$('button[type="submit"], button:contains("Continuar"), button:contains("Siguiente")');
    if (continueButton) {
      console.log('🔄 Haciendo clic en continuar...');
      await continueButton.click();
      await page.waitForTimeout(2000);
    }
    
    // Intentar navegar directamente a la página de resultados para probar el informe
    console.log('🎯 Navegando directamente a resultados para probar el informe...');
    await page.goto('http://localhost:5173/resultados', { waitUntil: 'networkidle0' });
    
    // Verificar si hay algún mensaje de error o carga
    const loadingElement = await page.$('.loading-section, .loading-spinner, [class*="loading"]');
    if (loadingElement) {
      console.log('⏳ Informe en proceso de generación...');
      await page.waitForTimeout(5000); // Esperar 5 segundos
    }
    
    // Verificar si se generó el informe
    const reportElement = await page.$('.report-section, .report-content, [class*="report"]');
    if (reportElement) {
      console.log('✅ Informe generado correctamente');
      
      // Extraer contenido del informe
      const reportContent = await page.$eval('.report-content, .markdown-content', el => el.textContent);
      console.log('📄 Contenido del informe:');
      console.log(reportContent.substring(0, 200) + '...');
      
      // Verificar si hay gráfico de radar
      const radarElement = await page.$('.radar-section, .radar-chart');
      if (radarElement) {
        console.log('📊 Gráfico de radar presente');
      }
      
      // Verificar puntuación
      const scoreElement = await page.$('.score-value, [class*="score"]');
      if (scoreElement) {
        const score = await page.$eval('.score-value, [class*="score"]', el => el.textContent);
        console.log(`🎯 Puntuación: ${score}`);
      }
      
    } else {
      console.log('❌ No se pudo generar el informe');
      
      // Verificar si hay mensaje de error
      const errorElement = await page.$('.error-section, .error-message, [class*="error"]');
      if (errorElement) {
        const errorMessage = await page.$eval('.error-section, .error-message, [class*="error"]', el => el.textContent);
        console.log(`❌ Error: ${errorMessage}`);
      }
    }
    
    // Navegar al dashboard de juegos
    console.log('🎮 Navegando al dashboard de juegos...');
    await page.goto('http://localhost:5173/games', { waitUntil: 'networkidle0' });
    
    // Verificar que se muestren los juegos
    const gamesGrid = await page.$('.grid, [class*="grid"]');
    if (gamesGrid) {
      console.log('✅ Dashboard de juegos cargado');
      
      // Contar juegos disponibles
      const gameCards = await page.$$('.game-card, [class*="game-card"]');
      console.log(`🎯 Juegos disponibles: ${gameCards.length}`);
      
      // Hacer clic en el primer juego
      if (gameCards.length > 0) {
        console.log('🎮 Abriendo primer juego...');
        await gameCards[0].click();
        await page.waitForTimeout(2000);
        
        // Verificar si se abrió la escena del juego
        const gameScene = await page.$('.game-scene, [class*="scene"], .scene-content');
        if (gameScene) {
          console.log('✅ Escena del juego cargada');
        }
      }
    }
    
    // Tomar screenshot final
    console.log('📸 Tomando screenshot final...');
    await page.screenshot({ path: 'frontend-test-result.png', fullPage: true });
    console.log('📸 Screenshot guardado como frontend-test-result.png');
    
    console.log('🎉 Prueba del frontend completada exitosamente!');
    
  } catch (error) {
    console.error('❌ Error durante la prueba:', error);
    
    // Tomar screenshot en caso de error
    try {
      await page.screenshot({ path: 'frontend-test-error.png', fullPage: true });
      console.log('📸 Screenshot de error guardado como frontend-test-error.png');
    } catch (screenshotError) {
      console.error('❌ Error al tomar screenshot:', screenshotError);
    }
  } finally {
    await browser.close();
  }
}

// Ejecutar la prueba
testFrontend().catch(console.error);
