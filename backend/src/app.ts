import express, { Request, Response, NextFunction } from 'express';
import path from 'path';
import fs from 'fs';
import puppeteer from 'puppeteer';
import iaReportRoute from './routes/iaReportRoute';
import pdfRoute from './routes/pdfRoute';
import cookieParser from 'cookie-parser';
import cors from 'cors';

const app = express();

// Middleware CORS: permite peticiones desde cualquier origen (puedes personalizar el origin si lo deseas)
app.use(cors({
  origin: [
    'http://localhost:3005',
    'http://localhost:3006',
    'http://localhost:5173',
    'https://yellow-mud-0b6281c1e.6.azurestaticapps.net',
    'https://*.azurestaticapps.net',
    'https://*.azurewebsites.net'
  ],
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With', 'Origin', 'Accept'],
  credentials: true,
  optionsSuccessStatus: 200,
  preflightContinue: false
}));

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