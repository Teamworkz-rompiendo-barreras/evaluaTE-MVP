"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const path_1 = __importDefault(require("path"));
const fs_1 = __importDefault(require("fs"));
const puppeteer_1 = __importDefault(require("puppeteer"));
const iaReportRoute_1 = __importDefault(require("./routes/iaReportRoute"));
const pdfRoute_1 = __importDefault(require("./routes/pdfRoute"));
const cookie_parser_1 = __importDefault(require("cookie-parser"));
const cors_1 = __importDefault(require("cors"));
const app = (0, express_1.default)();
// Middleware CORS: permite peticiones desde cualquier origen (puedes personalizar el origin si lo deseas)
app.use((0, cors_1.default)({
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
app.use(express_1.default.json());
app.use((0, cookie_parser_1.default)());
app.use('/api/informe-ia', iaReportRoute_1.default);
app.use('/api', pdfRoute_1.default);
app.use(express_1.default.static(path_1.default.join(__dirname, '../../templates')));
app.post('/api/generate-report', async (req, res) => {
    const { gameData, cvAnalysis } = req.body;
    const templatePath = path_1.default.join(__dirname, '../../templates/report.html');
    let html = fs_1.default.readFileSync(templatePath, 'utf8');
    const dataScript = `<script>window.__REPORT_DATA__ = ${JSON.stringify({ gameData, cvAnalysis })};</script>`;
    html = html.replace('<!--__DATA_INJECTION__-->', dataScript);
    const browser = await puppeteer_1.default.launch({ args: ['--no-sandbox', '--disable-setuid-sandbox'] });
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
exports.default = app;
