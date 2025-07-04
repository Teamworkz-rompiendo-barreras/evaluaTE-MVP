// backend/src/controllers/pdfController.ts
import express, { Request, Response } from 'express';
import { createPdf } from '../services/pdfService'; // Asegúrate de que la ruta sea correcta

export const generatePDF = async (req: Request, res: Response) => {
  try {
    const pdfBuffer = await createPdf(req.body);
    res.setHeader('Content-Type', 'application/pdf');
    res.setHeader('Content-Disposition', 'attachment; filename=report.pdf');
    res.send(pdfBuffer);
  } catch (error: any) {
    console.error('Error generating PDF:', error);
    if (error.message && error.message.includes('No se pudo cargar la imagen')) {
      res.status(500).json({ error: error.message });
    } else {
      res.status(500).json({ error: 'Error generating PDF' });
    }
  }
};