import puppeteer from 'puppeteer';

async function run() {
  console.log('🚀 E2E smoke iniciada');
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });
  try {
    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });
    await page.goto('http://127.0.0.1:5173', { waitUntil: 'networkidle0' });
    const homeTitle = await page.title();

    await page.goto('http://127.0.0.1:5173/resultados', { waitUntil: 'networkidle2' });
    await new Promise(r => setTimeout(r, 3000));
    const h1 = await page.$eval('h1', el => el.textContent || '').catch(() => null);
    const hasReport = Boolean(await page.$('.report-content'));
    const hasRadar = Boolean(await page.$('svg, canvas, .nivo'));
    await page.screenshot({ path: 'e2e-snapshot.png', fullPage: true });

    console.log(JSON.stringify({ ok: true, homeTitle, h1, hasReport, hasRadar, screenshot: 'e2e-snapshot.png' }));
  } catch (err) {
    console.error('❌ E2E error:', err);
    process.exitCode = 1;
  } finally {
    await browser.close();
  }
}

run().catch(e => { console.error(e); process.exit(1); });


