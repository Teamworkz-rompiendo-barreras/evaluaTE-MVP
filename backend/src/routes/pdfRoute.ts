// backend/src/routes/pdfRoute.ts
import express from 'express';
import { generatePDF } from '../controllers/pdfController'; // Asegúrate de que la ruta sea correcta

const router = express.Router();

// Ruta para generar el informe en PDF
router.post('/generate-report', generatePDF);

export default router;