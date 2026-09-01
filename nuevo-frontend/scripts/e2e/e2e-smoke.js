import puppeteer from 'puppeteer';
import { AxePuppeteer } from '@axe-core/puppeteer';

// Estandarizamos el puerto a 3005 para no colisionar con otras pruebas
const BASE_URL = 'http://127.0.0.1:3005';

async function run() {
  console.log('🚀 E2E Smoke y Accesibilidad iniciada');
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });
  
  try {
    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });
    
    // 1. Prueba de carga y título
    await page.goto(BASE_URL, { waitUntil: 'networkidle0' });
    const homeTitle = await page.title();
    
    // 2. Navegación a Resultados
    await page.goto(`${BASE_URL}/resultados`, { waitUntil: 'networkidle2' });
    await new Promise(r => setTimeout(r, 3000));
    
    const h1 = await page.$eval('h1', el => el.textContent || '').catch(() => null);
    const hasReport = Boolean(await page.$('.report-content'));
    
    // 3. AUDITORÍA CRÍTICA DE ACCESIBILIDAD (WCAG 2.2 AA)
    console.log('⚖️ Ejecutando auditoría WCAG 2.2 AA...');
    const results = await new AxePuppeteer(page)
      .withTags(['wcag2a', 'wcag2aa', 'wcag22aa'])
      .analyze();

    if (results.violations.length > 0) {
      console.error(`❌ FALLO DE ACCESIBILIDAD DETECTADO (${results.violations.length} violaciones):`);
      results.violations.forEach(v => {
        console.error(`- [${v.impact}] ${v.help} (${v.id})`);
        v.nodes.forEach(node => console.error(`   DOM: ${node.html}`));
      });
      throw new Error('La interfaz no cumple con la normativa de Accesibilidad Europea.');
    } else {
      console.log('✅ Certificación de accesibilidad superada sin violaciones críticas.');
    }

    await page.screenshot({ path: 'e2e-snapshot.png', fullPage: true });
    console.log(JSON.stringify({ ok: true, homeTitle, h1, hasReport, wcagPassed: true }));
    
  } catch (err) {
    console.error('❌ E2E/WCAG error:', err.message);
    process.exitCode = 1; // Aborta el script deploy.sh
  } finally {
    await browser.close();
  }
}

run().catch(e => { console.error(e); process.exit(1); });