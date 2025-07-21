// backend/src/controllers/pdfController.ts
import express from 'express';
import { createPdf } from '../services/pdfService'; // Asegúrate de que la ruta sea correcta
import pdfParse from 'pdf-parse';
import multer from 'multer';
import { Request, Response } from 'express';

// Eliminar la declaración inline y crear un archivo pdf-parse.d.ts en la raíz del backend.

// Middleware de multer para recibir archivos
const upload = multer({ storage: multer.memoryStorage() });

export const generatePDF = async (req: Request, res: Response) => {
  try {
    const pdfBuffer = await createPdf(req.body);
    res.setHeader('Content-Type', 'application/pdf');
    res.setHeader('Content-Disposition', 'attachment; filename=report.pdf');
    res.send(pdfBuffer);
  } catch (error: any) {
    console.error('Error generating PDF:', error);
    
    // Manejar errores de validación de datos
    if (error.message && error.message.includes('Datos inválidos')) {
      res.status(400).json({ error: error.message });
    }
    // Manejar errores de carga de imágenes
    else if (error.message && error.message.includes('No se pudo cargar la imagen')) {
      res.status(500).json({ error: error.message });
    }
    // Otros errores
    else {
      res.status(500).json({ error: 'Error generating PDF' });
    }
  }
};

export const analyzeCV = [
  upload.single('cv'),
  async (req: Request & { file?: Express.Multer.File }, res: Response) => {
    try {
      if (!req.file) {
        console.error('No se envió ningún archivo PDF.');
        return res.status(400).json({ error: 'No se envió ningún archivo PDF.' });
      }
      console.log(`Archivo recibido: ${req.file.originalname}, tamaño: ${req.file.size} bytes`);
      // Extraer texto del PDF
      let data;
      try {
        data = await pdfParse(req.file.buffer);
      } catch (err) {
        console.error('Error al leer el PDF:', err);
        return res.status(400).json({ error: 'No se pudo leer el archivo PDF. Asegúrate de que el archivo es un PDF válido.' });
      }
      const text = data.text || '';
      console.log('Texto extraído del PDF (primeros 500 caracteres):', text.slice(0, 500));
      if (text.length < 100) {
        console.error('El texto extraído del PDF es demasiado corto o vacío.');
        return res.status(400).json({ error: 'El archivo PDF no contiene suficiente texto para analizar el CV. Por favor, revisa el archivo.' });
      }

      // Lógica simple de análisis (puedes mejorarla con IA/NLP)
      const structure = text.includes('Experiencia') && text.includes('Educación') ? 'bueno' : 'regular';
      const coherence = text.includes('Responsable') && text.includes('Logros') ? 'bueno' : 'regular';
      const years = text.match(/\d{4}/g);
      const experience = years && years.length > 2 ? 'bueno' : 'regular';
      const skills = Array.from(new Set((text.match(/JavaScript|React|TypeScript|HTML|CSS|Python|SQL/gi) || [])));
      const education = (text.match(/(Grado|Licenciatura|Máster|Ingeniería|Doctorado)[^\n]*/gi) || []);
      const alerts = [];
      if (!text.toLowerCase().includes('proyecto')) alerts.push('Faltan proyectos personales');
      if (skills.length < 3) alerts.push('Pocas habilidades técnicas detectadas');

      const cvAnalysis = {
        structure,
        coherence,
        experience,
        skills,
        education,
        alerts
      };
      console.log('Resultado del análisis de CV:', JSON.stringify(cvAnalysis, null, 2));
      return res.json(cvAnalysis);
    } catch (error) {
      console.error('Error analizando el CV:', error);
      return res.status(500).json({ error: 'Error analizando el CV.' });
    }
  }
];