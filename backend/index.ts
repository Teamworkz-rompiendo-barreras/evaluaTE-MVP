// backend/index.ts
import express, { Request, Response } from 'express';
import path from 'path';
import fs from 'fs';
import puppeteer from 'puppeteer';
import iaReportRoute from './src/routes/iaReportRoute';
import pdfRoute from './src/routes/pdfRoute';
import cors from 'cors';
import cookieParser from 'cookie-parser';

const app = express();

// Configuración CORS global
app.use(cors({
  origin: [
    'http://localhost:3005',
    'http://localhost:5173',
    'https://yellow-mud-0b6281c1e.6.azurestaticapps.net'
  ],
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With', 'Origin', 'Accept'],
  credentials: true,
  optionsSuccessStatus: 200,
  preflightContinue: false
}));

// Responder a preflight OPTIONS para todas las rutas
app.options('*', cors());

app.use(express.json());
app.use(cookieParser());

// Rutas API
app.use('/api/informe-ia', iaReportRoute);
app.use('/api', pdfRoute);

// Servir archivos estáticos si es necesario
app.use(express.static(path.join(__dirname, '../templates')));

// Endpoint PDF legacy (puedes eliminarlo si ya no se usa)
app.post('/api/generate-report', async (req: Request, res: Response) => {
  const { gameData, cvAnalysis } = req.body;
  const templatePath = path.join(__dirname, '../templates/report.html');
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

// Arrancar el servidor solo si este archivo es ejecutado directamente
if (require.main === module) {
  const PORT = process.env.PORT || 8080;
  app.listen(PORT, () => {
    console.log(`EvaluaTE backend server running on port ${PORT}`);
  });
}

export default app;
