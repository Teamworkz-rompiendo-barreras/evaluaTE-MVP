import puppeteer from 'puppeteer';

function buildPersistedState() {
  const personal = {
    firstName: 'Juan',
    lastName: 'Pérez',
    email: 'juan@example.com',
    whatsapp: '',
    jobPreferences: { areas: ['Tecnología'], needs: [], workMode: 'remoto', availability: 'completa' },
    workMode: 'remoto',
    availability: 'completa',
    startDate: 'inmediata',
    willingToRelocate: false,
    hasDisabilityCert: false,
    cvFile: { fileName: 'cv.pdf', fileContent: 'data:application/pdf;base64,' },
    cvAnalysis: undefined,
    softSkills: [
      { skill: 'Liderazgo', score: 80, level: 'alto', confidence: 90 },
      { skill: 'Creatividad', score: 75, level: 'alto', confidence: 85 },
      { skill: 'Pensamiento Analítico', score: 70, level: 'medio', confidence: 80 },
      { skill: 'Empatía', score: 65, level: 'medio', confidence: 70 },
      { skill: 'Resiliencia', score: 60, level: 'medio', confidence: 70 },
    ],
    unlockedGames: 10,
    report: undefined,
    logs: [],
    accessibilitySettings: {
      easyReadingMode: false,
      audioAssistiveMode: false,
      showPictograms: false,
      contrastLevel: 'normal',
      fontScale: 120,
    },
    completed: true,
  };

  const game = {
    currentGameId: null,
    completedGames: ['1','2','3','4','5','6','7','8','9','10'],
    gameLogs: {},
    softSkills: [],
    adaptations: [],
  };

  const progress = {};
  const accessibility = {};

  return {
    personal: JSON.stringify(personal),
    progress: JSON.stringify(progress),
    accessibility: JSON.stringify(accessibility),
    game: JSON.stringify(game),
    _persist: { version: 1, rehydrated: true },
  };
}

async function run() {
  console.log('🚀 E2E reporte: preparando estado y navegando a /resultados');
  const browser = await puppeteer.launch({ headless: 'new', args: ['--no-sandbox','--disable-setuid-sandbox'] });
  try {
    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 900 });

    // Inyectar estado ANTES de cargar la app (rehidratación temprana)
    const state = buildPersistedState();
    const wrapped = {
      personal: state.personal,
      progress: state.progress,
      accessibility: state.accessibility,
      game: state.game,
      _persist: { version: 1, rehydrated: true }
    };
    await page.evaluateOnNewDocument((st) => {
      try { localStorage.setItem('persist:root', JSON.stringify(st)); } catch {}
    }, wrapped);

    await page.goto('http://127.0.0.1:3005/resultados', { waitUntil: 'domcontentloaded' });
    // Esperar a que Redux Persist rehidrate
    await new Promise(r => setTimeout(r, 1500));
    // Forzar evaluación de ruta actual
    await page.evaluate(() => history.pushState({}, '', '/resultados'));
    await new Promise(r => setTimeout(r, 400));

    // Esperar al menos a que aparezca el título de portada del informe
    const titleFound = await page.evaluate(() => {
      const h1s = Array.from(document.querySelectorAll('h1')).map(el => (el.textContent || '').trim());
      return h1s.some(t => t.includes('Informe de Empleabilidad'));
    });

    const hasReport = Boolean(await page.$('.report-content'));
    const hasRadar = Boolean(await page.$('svg, canvas, .nivo'));
    const routeInfo = await page.evaluate(() => ({ href: location.href, h1s: Array.from(document.querySelectorAll('h1')).map(el => (el.textContent||'').trim()), hasPrintDisabled: !!document.querySelector('button[disabled]') }));
    await page.screenshot({ path: 'e2e-report.png', fullPage: true });

    console.log(JSON.stringify({ ok: titleFound, hasReport, hasRadar, routeInfo, screenshot: 'e2e-report.png' }));
  } catch (err) {
    console.error('❌ E2E reporte error:', err);
    process.exitCode = 1;
  } finally {
    await browser.close();
  }
}

run().catch(e => { console.error(e); process.exit(1); });


