import express, { Request, Response, NextFunction } from 'express';
import path from 'path';
import fs from 'fs';
import puppeteer from 'puppeteer';
import iaReportRoute from './routes/iaReportRoute';
import pdfRoute from './routes/pdfRoute';
import cookieParser from 'cookie-parser';

const app = express();

const allowedOrigins = [
  'http://localhost:3005',
  'http://localhost:5173',
  'https://yellow-mud-0b6281c1e.6.azurestaticapps.net'
];

app.use(function (req: Request, res: Response, next: NextFunction) {
  const origin = req.headers.origin;
  if (origin && allowedOrigins.includes(origin)) {
    res.header('Access-Control-Allow-Origin', origin);
    res.header('Vary', 'Origin');
  }
  res.header('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With, Origin, Accept');
  res.header('Access-Control-Allow-Credentials', 'true');
  if (req.method === 'OPTIONS') {
    res.sendStatus(200);
    return;
  }
  next();
});

app.use(express.json());
app.use(cookieParser());

app.use('/api/informe-ia', iaReportRoute);
app.use('/api', pdfRoute);

app.use(express.static(path.join(__dirname, '../../templates')));

app.post('/api/generate-report', async (req: Request, res: Response) => {
  const { gameData, cvAnalysis } = req.body;
  const templatePath = path.join(__dirname, '../../templates/report.html');
  let html = fs.readFileSync(templatePath, 'utf8');
  const dataScript = `<script>window.__REPORT_DATA__ = ${JSON.stringify({ gameData, cvAnalysis })};</script>`;
  html = html.replace('<!--__DATA_INJECTION__-->', dataScript);
  const browser = await puppeteer.launch({ args: ['--no-sandbox', '--disable-setuid-sandbox'] });
  const page = await browser.newPage();
  await page.setContent(html, { waitUntil: 'networkidle0' });
  const pdfBuffer = await page.pdf({ format: 'A4', printBackground: true });
  await browser.close();
  res
    .status(200)
    .header('Content-Type', 'application/pdf')
    .header('Content-Disposition', 'attachment; filename="informe-resultados.pdf"')
    .send(pdfBuffer);
});

export default app; 