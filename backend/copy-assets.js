const fs = require('fs');
const path = require('path');

// Función para copiar directorio recursivamente
function copyDir(src, dest) {
  // Crear directorio de destino si no existe
  if (!fs.existsSync(dest)) {
    fs.mkdirSync(dest, { recursive: true });
  }

  // Leer archivos del directorio fuente
  const files = fs.readdirSync(src);

  files.forEach(file => {
    const srcPath = path.join(src, file);
    const destPath = path.join(dest, file);

    if (fs.statSync(srcPath).isDirectory()) {
      // Si es un directorio, copiar recursivamente
      copyDir(srcPath, destPath);
    } else {
      // Si es un archivo, copiarlo
      fs.copyFileSync(srcPath, destPath);
      console.log(`Copiado: ${srcPath} -> ${destPath}`);
    }
  });
}

// Rutas
const srcAssets = path.join(__dirname, 'src/assets');
const distAssets = path.join(__dirname, 'dist/src/assets');

try {
  // Copiar assets
  if (fs.existsSync(srcAssets)) {
    copyDir(srcAssets, distAssets);
    console.log('✅ Assets copiados correctamente');
  } else {
    console.error('❌ No se encontró el directorio src/assets');
    process.exit(1);
  }
} catch (error) {
  console.error('❌ Error copiando assets:', error);
  process.exit(1);
} 