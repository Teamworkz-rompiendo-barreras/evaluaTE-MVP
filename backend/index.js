"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
// backend/index.ts
const express_1 = __importDefault(require("express"));
const cors_1 = __importDefault(require("cors"));
const path_1 = __importDefault(require("path"));
const fs_1 = __importDefault(require("fs"));
const puppeteer_1 = __importDefault(require("puppeteer"));
const pdfRoute = require('./src/routes/pdfRoute').default;
const app = (0, express_1.default)();

// Configuración CORS para permitir múltiples orígenes
app.use((0, cors_1.default)({
  origin: [
    'http://localhost:3005',
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
app.use(express_1.default.json());
// Sirve los archivos estáticos de templates (si quieres exponer report.html o assets)
app.use(express_1.default.static(path_1.default.join(__dirname, '../templates')));
app.use('/api/pdf', pdfRoute);
app.post('/api/generate-report', (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    const { gameData, cvAnalysis } = req.body;
    const templatePath = path_1.default.join(__dirname, '../templates/report.html');
    let html = fs_1.default.readFileSync(templatePath, 'utf8');
    const injection = `<script>window.__REPORT_DATA__ = ${JSON.stringify({ gameData, cvAnalysis })};</script>`;
    html = html.replace('<!--__DATA_INJECTION__-->', injection);
    const browser = yield puppeteer_1.default.launch({ args: ['--no-sandbox'] });
    const page = yield browser.newPage();
    yield page.setContent(html, { waitUntil: 'networkidle0' });
    const pdfBuffer = yield page.pdf({ format: 'A4', printBackground: true });
    yield browser.close();
    res
        .status(200)
        .set({
        'Content-Type': 'application/pdf',
        'Content-Disposition': 'attachment; filename="informe-resultados.pdf"',
    })
        .send(pdfBuffer);
}));
const PORT = process.env.PORT || 8000;
app.listen(PORT, () => console.log(`