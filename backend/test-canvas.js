const { createCanvas } = require('canvas');
const fs = require('fs');

// Cambia aquí: especifica 'pdf' como tipo de canvas
const canvas = createCanvas(200, 200, 'pdf');
const ctx = canvas.getContext('2d');
ctx.fillStyle = 'red';
ctx.fillRect(10, 10, 100, 100);

try {
  // Ahora no necesitas pasar el tipo MIME, solo llama a toBuffer()
  const buffer = canvas.toBuffer();
  console.log('Buffer:', buffer, 'Length:', buffer?.length);
  fs.writeFileSync('test.pdf', buffer);
  console.log('PDF generado correctamente como test.pdf');
} catch (err) {
  console.error('Error generando el PDF con canvas:', err);
} 