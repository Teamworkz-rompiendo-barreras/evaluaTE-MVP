const { createCanvas } = require('canvas');
const fs = require('fs');

const canvas = createCanvas(200, 200);
const ctx = canvas.getContext('2d');
ctx.fillStyle = 'red';
ctx.fillRect(10, 10, 100, 100);

try {
  const buffer = canvas.toBuffer('application/pdf');
  console.log('Buffer:', buffer, 'Length:', buffer?.length);
  fs.writeFileSync('test.pdf', buffer);
  console.log('PDF generado correctamente como test.pdf');
} catch (err) {
  console.error('Error generando el PDF con canvas:', err);
} 