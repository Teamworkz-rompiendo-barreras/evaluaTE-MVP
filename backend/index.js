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
/* File: server/index.ts */
const express_1 = __importDefault(require("express"));
const path_1 = __importDefault(require("path"));
const fs_1 = __importDefault(require("fs"));
const puppeteer_1 = __importDefault(require("puppeteer"));
const app = (0, express_1.default)();
app.use(express_1.default.json());
// Endpoint to generate PDF report
app.post('/api/generate-report', (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    const { gameData, cvAnalysis } = req.body;
    // 1️⃣ Load HTML template
    const templatePath = path_1.default.join(__dirname, '../templates/report.html');
    let html = fs_1.default.readFileSync(templatePath, 'utf8');
    // 2️⃣ Inject data into template
    const dataScript = `<script>window.__REPORT_DATA__ = ${JSON.stringify({ gameData, cvAnalysis })};</script>`;
    html = html.replace('<!--__DATA_INJECTION__-->', dataScript);
    // 3️⃣ Launch headless browser and render PDF
    const browser = yield puppeteer_1.default.launch({ args: ['--no-sandbox', '--disable-setuid-sandbox'] });
    const page = yield browser.newPage();
    yield page.setContent(html, { waitUntil: 'networkidle0' });
    const pdfBuffer = yield page.pdf({ format: 'A4', printBackground: true });
    yield browser.close();
    // 4️⃣ Send PDF to client
    res.set({
        'Content-Type': 'application/pdf',
        'Content-Disposition': 'attachment; filename="informe-resultados.pdf"',
    });
    res.send(pdfBuffer);
}));
// Serve static assets (CSS, JS libs)
app.use(express_1.default.static(path_1.default.join(__dirname, '../templates')));
const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
    console.log(`PDF report server running on port ${PORT}`);
})
    /* File: templates/report.html */
    < !DOCTYPE;
html >
    lang;
"es" >
    charset;
"UTF-8" /  >
    name;
"viewport";
content = "width=device-width, initial-scale=1.0" /  >
    Informe;
de;
Resultados < /title>
    < link;
href = "https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css";
rel = "stylesheet" /  >
    src;
"https://cdn.jsdelivr.net/npm/chart.js" > /script>
    < !--__DATA_INJECTION__;
-- >
    /head>
    < body;
class {
}
"p-8 bg-gray-50" >
    class {
    };
"max-w-2xl mx-auto bg-white p-6 rounded shadow" >
    class {
    };
"text-3xl font-bold mb-4 text-center" > Informe;
de;
Resultados < /h1>
    < section >
    class {
    };
"text-2xl font-semibold mb-2" > Análisis;
de;
tu;
CV < /h2>
    < p > Puntuación;
/strong> <span id="score"></span > /100</p >
    class {
    };
"grid grid-cols-1 md:grid-cols-2 gap-4 mt-4" >
    class {
    };
"font-medium" > Fortalezas < /h3>
    < ul;
id = "strengths";
class {
}
"list-disc ml-6" > /ul>
    < /div>
    < div >
    class {
    };
"font-medium" > Áreas;
a;
mejorar < /h3>
    < ul;
id = "weaknesses";
class {
}
"list-disc ml-6" > /ul>
    < /div>
    < /div>
    < /section>
    < section;
class {
}
"mt-8" >
    class {
    };
"text-2xl font-semibold mb-2" > Minijuegos < /h2>
    < canvas;
id = "radarChart";
width = "400";
height = "400" > /canvas>
    < /section>
    < (/div>);
(function () {
    const { gameData = [], cvAnalysis = {} } = window.__REPORT_DATA__ || {};
    // Populate CV data
    document.getElementById('score').textContent = cvAnalysis.score;
    const strengthsEl = document.getElementById('strengths');
    cvAnalysis.strengths.forEach(s => {
        const li = document.createElement('li');
        li.textContent = s;
        strengthsEl.appendChild(li);
    });
    const weaknessesEl = document.getElementById('weaknesses');
    cvAnalysis.weaknesses.forEach(w => {
        const li = document.createElement('li');
        li.textContent = w;
        weaknessesEl.appendChild(li);
    });
    // Generate Radar Chart
    const labels = gameData.map(d => d.subject);
    const data = gameData.map(d => d.dA);
    new Chart(document.getElementById('radarChart'), {
        type: 'radar',
        data: {
            labels,
            datasets: [{ label: 'Resultados Minijuegos', data }]
        },
        options: {
            scale: { ticks: { beginAtZero: true, max: 100 } }
        }
    });
})()
    < /script>
    < /body>
    < /html>;
