// backend/src/controllers/pdfController.ts
import express, { Request, Response } from 'express';
import { createPdf } from '../services/pdfService'; // Asegúrate de que la ruta sea correcta

export const generatePDF = async (req: Request, res: Response) => {
  try {
    const pdfBuffer = await createPdf(req.body);
    res.setHeader('Content-Type', 'application/pdf');
    res.setHeader('Content-Disposition', 'attachment; filename=report.pdf');
    res.send(pdfBuffer);
  } catch (error) {
    console.error('Error generating PDF:', error);
    res.status(500).send('Error generating PDF');
  }
};