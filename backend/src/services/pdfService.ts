// backend/src/services/pdfService.ts
import { createCanvas, loadImage } from 'canvas';
import { join } from 'path';
import path from 'path';

// Función para obtener la ruta correcta de las imágenes
function getImagePath(imageName: string): string {
  // En desarrollo: src/assets/
  // En producción: dist/src/assets/
  const possiblePaths = [
    join(__dirname, '../assets', imageName),
    join(__dirname, '../../src/assets', imageName),
    join(process.cwd(), 'src/assets', imageName),
    join(process.cwd(), 'dist/src/assets', imageName)
  ];
  
  for (const imagePath of possiblePaths) {
    try {
      require('fs').accessSync(imagePath);
      return imagePath;
    } catch (err) {
      // Continuar con la siguiente ruta
    }
  }
  
  throw new Error(`No se encontró la imagen ${imageName} en ninguna de las rutas esperadas`);
}

async function safeLoadImage(path: string, label: string) {
  try {
    return await loadImage(path);
  } catch (err) {
    throw new Error(`No se pudo cargar la imagen (${label}): ${path}. Asegúrate de que el archivo es una imagen PNG válida.`);
  }
}

// Función para validar datos de entrada
function validateData(data: any) {
  const errors: string[] = [];

  // Validar gameData
  if (!data.gameData) {
    errors.push('gameData es requerido');
  } else if (!Array.isArray(data.gameData)) {
    errors.push('gameData debe ser un array');
  }

  // Validar cvAnalysis
  if (!data.cvAnalysis) {
    errors.push('cvAnalysis es requerido');
  } else if (typeof data.cvAnalysis !== 'object') {
    errors.push('cvAnalysis debe ser un objeto');
  }

  // Validar jobPreferences
  if (!data.jobPreferences) {
    errors.push('jobPreferences es requerido');
  } else if (typeof data.jobPreferences !== 'object') {
    errors.push('jobPreferences debe ser un objeto');
  } else if (!Array.isArray(data.jobPreferences.areas)) {
    errors.push('jobPreferences.areas debe ser un array');
  }

  if (errors.length > 0) {
    throw new Error(`Datos inválidos: ${errors.join(', ')}`);
  }
}

export const createPdf = async (data: any) => {
  // Validar datos de entrada
  validateData(data);

  const { gameData, cvAnalysis, jobPreferences } = data;

  // Crear canvas en formato PDF
  const canvas = createCanvas(800, 1200, 'pdf');
  const ctx = canvas.getContext('2d');

  // Cargar fondo
  const background = await safeLoadImage(getImagePath('background.png'), 'background');
  ctx.drawImage(background, 0, 0, canvas.width, canvas.height);

  // Estilos básicos
  ctx.font = '24px Arial';
  ctx.fillStyle = '#000';

  // Título
  ctx.fillText('Tu Informe Final', 50, 50);

  // Mapa de habilidades (ejemplo)
  ctx.fillText('Mapa de Habilidades', 50, 100);
  const radarChart = await safeLoadImage(getImagePath('radarchart.png'), 'radarchart');
  ctx.drawImage(radarChart, 50, 150, 300, 300);

  // Fortalezas más destacadas
  ctx.fillText('Fortalezas más destacadas', 50, 470);
  if (Array.isArray(gameData)) {
    gameData.forEach((game: any, index: number) => {
      const subject = game?.subject || 'Sin nombre';
      const dA = game?.dA || 0;
      ctx.fillText(`${subject}: ${dA}`, 50, 500 + index * 30);
    });
  }

  // Áreas de mejora
  ctx.fillText('Áreas a mejorar', 50, 700);
  ctx.fillText('Gestión emocional', 50, 730);
  ctx.fillText('Curiosidad y aprendizaje continuo', 50, 760);

  // Recomendaciones laborales
  ctx.fillText('Recomendaciones laborales', 50, 800);
  ctx.fillText('Tipos de puestos recomendados:', 50, 830);
  if (Array.isArray(jobPreferences.areas)) {
    jobPreferences.areas.forEach((area: string, index: number) => {
      ctx.fillText(`- ${area}`, 50, 860 + index * 30);
    });
  }

  // Análisis del CV
  ctx.fillText('Análisis de tu CV', 50, 1000);
  const structure = cvAnalysis?.structure || 'No especificado';
  const coherence = cvAnalysis?.coherence || 'No especificado';
  const experience = cvAnalysis?.experience || 'No especificado';
  ctx.fillText(structure, 50, 1030);
  ctx.fillText(coherence, 50, 1060);
  ctx.fillText(experience, 50, 1090);

  // Próximos pasos sugeridos
  ctx.fillText('Próximos pasos sugeridos', 50, 1130);
  ctx.fillText('Formación sugerida:', 50, 1160);
  ctx.fillText('Portales de empleo recomendados:', 50, 1190);

  console.log('¡Entrando a generatePDF!');
  let pdfBuffer;
  try {
    // Generar buffer PDF correctamente
    pdfBuffer = canvas.toBuffer();
    if (!pdfBuffer || !Buffer.isBuffer(pdfBuffer) || pdfBuffer.length === 0) {
      console.error('El buffer PDF es inválido o está vacío:', pdfBuffer);
      throw new Error('No se pudo generar el PDF: el buffer es inválido o está vacío. Puede ser un problema de la librería canvas o del entorno.');
    }
    console.log('Tamaño del buffer PDF:', pdfBuffer.length);
  } catch (err) {
    console.error('Error al generar el buffer PDF:', err);
    throw err;
  }
  return pdfBuffer;
};