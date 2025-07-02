// backend/src/services/pdfService.ts
import { createCanvas, loadImage } from 'canvas';
import { join } from 'path';

export const createPdf = async (data: any) => {
  const { gameData, cvAnalysis, jobPreferences } = data;

  const canvas = createCanvas(800, 1200);
  const ctx = canvas.getContext('2d');

  // Cargar fondo
  const background = await loadImage(join(__dirname, '../assets/background.png'));
  ctx.drawImage(background, 0, 0, canvas.width, canvas.height);

  // Estilos básicos
  ctx.font = '24px Arial';
  ctx.fillStyle = '#000';

  // Título
  ctx.fillText('Tu Informe Final', 50, 50);

  // Mapa de habilidades (ejemplo)
  ctx.fillText('Mapa de Habilidades', 50, 100);
  ctx.drawImage(await loadImage(join(__dirname, '../assets/radar-chart.png')), 50, 150, 300, 300);

  // Fortalezas más destacadas
  ctx.fillText('Fortalezas más destacadas', 50, 470);
  gameData.forEach((game: any, index: number) => {
    ctx.fillText(`${game.subject}: ${game.dA}`, 50, 500 + index * 30);
  });

  // Áreas de mejora
  ctx.fillText('Áreas a mejorar', 50, 700);
  ctx.fillText('Gestión emocional', 50, 730);
  ctx.fillText('Curiosidad y aprendizaje continuo', 50, 760);

  // Recomendaciones laborales
  ctx.fillText('Recomendaciones laborales', 50, 800);
  ctx.fillText('Tipos de puestos recomendados:', 50, 830);
  jobPreferences.areas.forEach((area: string, index: number) => {
    ctx.fillText(`- ${area}`, 50, 860 + index * 30);
  });

  // Análisis del CV
  ctx.fillText('Análisis de tu CV', 50, 1000);
  ctx.fillText(cvAnalysis.structure, 50, 1030);
  ctx.fillText(cvAnalysis.coherence, 50, 1060);
  ctx.fillText(cvAnalysis.experience, 50, 1090);

  // Próximos pasos sugeridos
  ctx.fillText('Próximos pasos sugeridos', 50, 1130);
  ctx.fillText('Formación sugerida:', 50, 1160);
  ctx.fillText('Portales de empleo recomendados:', 50, 1190);

  return canvas.toBuffer('application/pdf');
};