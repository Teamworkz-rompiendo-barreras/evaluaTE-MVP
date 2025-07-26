// backend/src/controllers/pdfController.ts
import express from 'express';
import { createPdf } from '../services/pdfService'; // Asegúrate de que la ruta sea correcta
import pdfParse from 'pdf-parse';
import multer from 'multer';
import { Request, Response } from 'express';
import { spawn } from 'child_process';
import path from 'path';

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
      
      // Usar Python para analizar el CV
      const pythonResult = await analyzeCVWithPython(req.file.buffer);
      
      if (pythonResult.error) {
        console.error('Error en análisis Python:', pythonResult.error);
        return res.status(500).json({ error: pythonResult.error });
      }
      
      // Extraer el análisis del resultado de Python
      const analysis = pythonResult.analysis;
      
      console.log('=== ANÁLISIS DE CV CON PYTHON ===');
      console.log('Estructura:', analysis.structure);
      console.log('Coherencia:', analysis.coherence);
      console.log('Experiencia:', analysis.experience);
      console.log('Habilidades técnicas encontradas:', analysis.technologies_count);
      console.log('Experiencias encontradas:', analysis.experience_count);
      console.log('Educación encontrada:', analysis.education_count);
      console.log('Años totales de experiencia:', analysis.total_years_experience);
      
      // Convertir el resultado de Python al formato esperado por el frontend
      const cvAnalysis = {
        structure: analysis.structure,
        coherence: analysis.coherence,
        experience: analysis.experience,
        skills: analysis.skills || [],
        softSkills: analysis.softSkills || [],
        education: analysis.education || [],
        strengths: analysis.strengths || [],
        weaknesses: analysis.weaknesses || [],
        feedback: analysis.feedback || '',
        alerts: analysis.alerts || []
      };
      
      console.log('Resultado final:', JSON.stringify(cvAnalysis, null, 2));
      
      return res.json(cvAnalysis);
      
    } catch (error) {
      console.error('Error analizando el CV:', error);
      return res.status(500).json({ error: 'Error analizando el CV.' });
    }
  }
];

async function analyzeCVWithPython(pdfBuffer: Buffer): Promise<any> {
  return new Promise((resolve, reject) => {
    try {
      // Crear un script Python temporal que reciba el buffer
      const pythonScript = `
import sys
import json
import base64
from cv_analyzer import extract_pdf_info

# Recibir el PDF como base64 desde stdin
pdf_base64 = sys.stdin.read().strip()
pdf_buffer = base64.b64decode(pdf_base64)

# Analizar el CV
result = extract_pdf_info(pdf_buffer)

# Enviar resultado como JSON
print(json.dumps(result, ensure_ascii=False))
`;

      // Convertir el buffer a base64
      const pdfBase64 = pdfBuffer.toString('base64');
      
      // Ejecutar Python con el entorno virtual
      const pythonProcess = spawn(path.join(__dirname, '../../venv/bin/python'), ['-c', pythonScript], {
        cwd: path.join(__dirname, '../../'), // Ir al directorio backend
        env: {
          ...process.env,
          PYTHONPATH: path.join(__dirname, '../../')
        }
      });
      
      let stdout = '';
      let stderr = '';
      
      pythonProcess.stdout.on('data', (data) => {
        stdout += data.toString();
      });
      
      pythonProcess.stderr.on('data', (data) => {
        stderr += data.toString();
      });
      
      pythonProcess.on('close', (code) => {
        if (code !== 0) {
          console.error('Error en Python:', stderr);
          reject(new Error(`Python process exited with code ${code}: ${stderr}`));
          return;
        }
        
        try {
          const result = JSON.parse(stdout);
          resolve(result);
        } catch (parseError) {
          console.error('Error parsing Python output:', parseError);
          console.error('Python stdout:', stdout);
          reject(new Error('Error parsing Python output'));
        }
      });
      
      // Enviar el PDF al proceso Python
      pythonProcess.stdin.write(pdfBase64);
      pythonProcess.stdin.end();
      
    } catch (error) {
      reject(error);
    }
  });
}