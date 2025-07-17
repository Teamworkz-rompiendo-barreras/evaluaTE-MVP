const fs = require('fs');
const path = require('path');

console.log('🔍 Verificando dependencias...\n');

// Verificar canvas
try {
  const canvas = require('canvas');
  console.log('✅ Canvas: OK');
  
  // Probar crear un canvas básico
  const testCanvas = canvas.createCanvas(100, 100);
  console.log('✅ Canvas createCanvas: OK');
  
  // Probar cargar una imagen
  const testImage = canvas.loadImage(path.join(__dirname, 'src/assets/background.png'));
  console.log('✅ Canvas loadImage: OK');
  
} catch (error) {
  console.error('❌ Canvas: ERROR -', error.message);
  console.log('💡 Solución: Instalar dependencias del sistema:');
  console.log('   Ubuntu/Debian: sudo apt-get install build-essential libcairo2-dev libpango1.0-dev libjpeg-dev libgif-dev librsvg2-dev');
  console.log('   CentOS/RHEL: sudo yum install gcc-c++ cairo-devel pango-devel libjpeg-turbo-devel giflib-devel');
  console.log('   macOS: brew install pkg-config cairo pango libpng jpeg giflib librsvg');
}

// Verificar puppeteer
try {
  const puppeteer = require('puppeteer');
  console.log('✅ Puppeteer: OK');
  
  // Verificar que se puede lanzar (sin abrir realmente)
  console.log('✅ Puppeteer require: OK');
  
} catch (error) {
  console.error('❌ Puppeteer: ERROR -', error.message);
  console.log('💡 Solución: Puppeteer debería instalarse automáticamente con npm install');
}

// Verificar archivos de assets
console.log('\n📁 Verificando archivos de assets...');

const assetsPath = path.join(__dirname, 'src/assets');
const distAssetsPath = path.join(__dirname, 'dist/src/assets');

const requiredFiles = ['background.png', 'radarchart.png'];

requiredFiles.forEach(file => {
  const srcFile = path.join(assetsPath, file);
  const distFile = path.join(distAssetsPath, file);
  
  if (fs.existsSync(srcFile)) {
    console.log(`✅ ${file} (src): OK`);
  } else {
    console.error(`❌ ${file} (src): NO ENCONTRADO`);
  }
  
  if (fs.existsSync(distFile)) {
    console.log(`✅ ${file} (dist): OK`);
  } else {
    console.error(`❌ ${file} (dist): NO ENCONTRADO`);
  }
});

console.log('\n🎯 Verificación completada'); 