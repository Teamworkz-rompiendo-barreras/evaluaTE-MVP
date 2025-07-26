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
      
      // Validar que el archivo sea un PDF
      if (!req.file.mimetype.includes('pdf')) {
        console.error('El archivo no es un PDF válido:', req.file.mimetype);
        return res.status(400).json({ error: 'El archivo debe ser un PDF válido.' });
      }
      
      // Validar tamaño del archivo (máximo 10MB)
      if (req.file.size > 10 * 1024 * 1024) {
        console.error('El archivo es demasiado grande:', req.file.size);
        return res.status(400).json({ error: 'El archivo es demasiado grande. Máximo 10MB.' });
      }
      
      // Usar Python para analizar el CV
      const pythonResult = await analyzeCVWithPython(req.file.buffer);
      
      // Log completo del resultado recibido de Python
      console.log('=== RESULTADO COMPLETO DE PYTHON ===');
      console.log(JSON.stringify(pythonResult, null, 2));
      
      if (pythonResult.error) {
        console.error('Error en análisis Python:', pythonResult.error);
        return res.status(500).json({ 
          error: `Error al analizar el CV: ${pythonResult.error}`,
          details: 'El archivo puede estar corrupto o no contener texto extraíble.'
        });
      }
      
      // Extraer el análisis del resultado de Python
      const analysis = pythonResult.analysis;
      
      if (!analysis) {
        console.error('No se pudo extraer el análisis del resultado de Python');
        return res.status(500).json({ 
          error: 'No se pudo procesar el análisis del CV.',
          details: 'El archivo puede no contener información extraíble.'
        });
      }
      
      // Log del análisis extraído
      console.log('=== ANÁLISIS EXTRAÍDO DEL RESULTADO ===');
      console.log(JSON.stringify(analysis, null, 2));
      
      // Convertir el resultado de Python al formato esperado por el frontend
      const cvAnalysis = {
        structure: analysis?.structure || 'regular',
        coherence: analysis?.coherence || 'regular',
        experience: analysis?.experience || 'regular',
        skills: analysis?.skills || [],
        softSkills: analysis?.softSkills || [],
        education: analysis?.education || [],
        strengths: analysis?.strengths || [],
        weaknesses: analysis?.weaknesses || [],
        feedback: analysis?.feedback || 'Análisis básico del CV completado.',
        alerts: analysis?.alerts || []
      };
      
      // Log del objeto final enviado al frontend
      console.log('=== OBJETO cvAnalysis ENVIADO AL FRONTEND ===');
      console.log(JSON.stringify(cvAnalysis, null, 2));
      
      return res.json(cvAnalysis);
      
    } catch (error) {
      console.error('Error analizando el CV:', error);
      return res.status(500).json({ 
        error: 'Error interno del servidor al analizar el CV.',
        details: error instanceof Error ? error.message : 'Error desconocido'
      });
    }
  }
];

async function analyzeCVWithPython(pdfBuffer: Buffer): Promise<any> {
  return new Promise((resolve, reject) => {
    try {
      console.log('Iniciando análisis con Python...');
      
      // Crear un script Python temporal que reciba el buffer
      const pythonScript = `
import sys
import json
import base64
import traceback

try:
    from cv_analyzer import extract_pdf_info
    
    # Recibir el PDF como base64 desde stdin
    pdf_base64 = sys.stdin.read().strip()
    pdf_buffer = base64.b64decode(pdf_base64)
    
    # Analizar el CV
    result = extract_pdf_info(pdf_buffer)
    
    # Enviar resultado como JSON
    print(json.dumps(result, ensure_ascii=False))
    
except Exception as e:
    error_result = {
        "error": f"Error en Python: {str(e)}",
        "traceback": traceback.format_exc()
    }
    print(json.dumps(error_result, ensure_ascii=False))
    sys.exit(1)
`;

      // Convertir el buffer a base64
      const pdfBase64 = pdfBuffer.toString('base64');
      
      console.log('Ejecutando Python con entorno virtual...');
      
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
        console.log('Python stdout:', data.toString());
      });
      
      pythonProcess.stderr.on('data', (data) => {
        stderr += data.toString();
        console.log('Python stderr:', data.toString());
      });
      
      pythonProcess.on('close', (code) => {
        console.log(`Proceso Python terminado con código: ${code}`);
        
        if (code !== 0) {
          console.error('Error en Python:', stderr);
          reject(new Error(`Python process exited with code ${code}: ${stderr}`));
          return;
        }
        
        try {
          const result = JSON.parse(stdout);
          console.log('Resultado parseado exitosamente');
          resolve(result);
        } catch (parseError) {
          console.error('Error parsing Python output:', parseError);
          console.error('Python stdout:', stdout);
          reject(new Error('Error parsing Python output'));
        }
      });
      
      pythonProcess.on('error', (error) => {
        console.error('Error ejecutando Python:', error);
        reject(new Error(`Error ejecutando Python: ${error.message}`));
      });
      
      // Enviar el PDF al proceso Python
      pythonProcess.stdin.write(pdfBase64);
      pythonProcess.stdin.end();
      
    } catch (error) {
      console.error('Error en analyzeCVWithPython:', error);
      reject(error);
    }
  });
}