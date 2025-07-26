"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
// backend/src/routes/pdfRoute.ts
const express_1 = __importDefault(require("express"));
const pdfController_1 = require("../controllers/pdfController"); // Importar el nuevo controlador
const router = express_1.default.Router();
// Ruta para generar el informe en PDF
router.post('/generate-report', pdfController_1.generatePDF);
// Ruta para analizar el CV (PDF)
router.post('/analyze-cv', pdfController_1.analyzeCV);
exports.default = router;
