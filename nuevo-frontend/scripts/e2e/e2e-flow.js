import puppeteer from 'puppeteer';

function buildRootPersistOverride(prev) {
  const personal = prev.personal ? JSON.parse(prev.personal) : {};
  const game = prev.game ? JSON.parse(prev.game) : {};
  const mergedPersonal = {
    ...personal,
    firstName: personal.firstName || 'Juan',
    lastName: personal.lastName || 'Pérez',
    email: personal.email || 'juan@example.com',
    jobPreferences: personal.jobPreferences || { areas: ['Tecnología'], needs: [], workMode: 'remoto', availability: 'completa' },
    completed: true,
    cvFile: personal.cvFile || { fileName: 'cv.pdf', fileContent: 'data:application/pdf;base64,' },
    unlockedGames: 10,
  };
  const mergedGame = {
    currentGameId: null,
    completedGames: Array.from({length:10}, (_,i)=>String(i+1)),
    gameLogs: {},
    softSkills: [],
    adaptations: [],
    ...game,
  };
  return {
    ...prev,
    personal: JSON.stringify(mergedPersonal),
    game: JSON.stringify(mergedGame),
  };
}

async function run() {
  console.log('🚀 E2E flujo: llenar formularios y forzar estado para /resultados');
  const browser = await puppeteer.launch({ headless: 'new', args: ['--no-sandbox','--disable-setuid-sandbox'] });
  try {
    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 900 });

    // 1) Ir a contacto y rellenar
    await page.goto('http://127.0.0.1:3005/register/contact', { waitUntil: 'networkidle0' });
    await page.type('#firstName', 'Juan');
    await page.type('#lastName', 'Pérez');
    await page.type('#email', 'juan@example.com');
    await page.click('#dataConsent');
    await Promise.race([
      page.waitForNavigation({ waitUntil: 'networkidle0' }),
      new Promise(r => setTimeout(r, 1500)),
    ]);

    // 2) Preferencias (si no navega, forzar URL)
    const url1 = page.url();
    if (!/\/register\/preferences/.test(url1)) {
      await page.goto('http://127.0.0.1:3005/register/preferences', { waitUntil: 'networkidle0' });
    }
    await page.waitForSelector('#jobPreferences', { timeout: 15000 });
    await page.type('#jobPreferences', 'Tecnología');
    await page.select('#workMode', 'remoto');
    await page.select('#availability', 'completa');
    await page.select('#startDate', 'inmediata');
    await page.click('button[type="submit"]');

    // 3) En /games, sobreescribir localStorage para completar juegos y cvFile
    await page.waitForNavigation({ waitUntil: 'networkidle0' });
    const root = await page.evaluate(() => {
      const raw = localStorage.getItem('persist:root');
      return raw ? JSON.parse(raw) : {};
    });
    const override = buildRootPersistOverride(root || {});
    await page.evaluate((ov) => {
      localStorage.setItem('persist:root', JSON.stringify(ov));
    }, override);
    await page.reload({ waitUntil: 'networkidle0' });

    // 4) Ir a resultados
    await page.goto('http://127.0.0.1:3005/resultados', { waitUntil: 'networkidle2' });
    await new Promise(r => setTimeout(r, 3000));

    const info = await page.evaluate(() => ({
      href: location.href,
      h1s: Array.from(document.querySelectorAll('h1')).map(el => (el.textContent||'').trim()),
      hasReport: !!document.querySelector('.report-content'),
    }));
    await page.screenshot({ path: 'e2e-flow.png', fullPage: true });
    console.log(JSON.stringify({ ok: info.href.includes('/resultados'), info }));
  } catch (err) {
    console.error('❌ E2E flujo error:', err);
    process.exitCode = 1;
  } finally {
    await browser.close();
  }
}

run().catch(e => { console.error(e); process.exit(1); });


