// backend/src/routes/pdfRoute.ts
import express from 'express';
import { generatePDF, analyzeCV } from '../controllers/pdfController'; // Importar el nuevo controlador

const router = express.Router();

// Ruta para generar el informe en PDF
router.post('/generate-report', generatePDF);
// Ruta para analizar el CV (PDF)
router.post('/analyze-cv', analyzeCV);

export default router;