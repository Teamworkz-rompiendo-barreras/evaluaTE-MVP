#!/bin/bash

# Script de despliegue para Azure App Service
# Este script configura el entorno para ejecutar tanto Node.js como Python

echo "Configurando entorno de despliegue para Azure..."

# Instalar dependencias de Node.js
echo "Instalando dependencias de Node.js..."
npm ci --production

# Compilar TypeScript
echo "Compilando TypeScript..."
npm run build

# Instalar dependencias de Python
echo "Instalando dependencias de Python..."
python -m pip install --upgrade pip
pip install -r requirements.txt

# Crear directorio de despliegue
echo "Preparando paquete de despliegue..."
mkdir -p deploy

# Copiar archivos compilados y necesarios
cp -r dist/* deploy/ 2>/dev/null || true
cp -r src/* deploy/ 2>/dev/null || true
cp package.json deploy/
cp requirements.txt deploy/
cp main.py deploy/
cp generate_report.py deploy/
cp models.py deploy/
cp db.py deploy/

# Crear directorio uploads si no existe
mkdir -p deploy/uploads

# Crear archivo de configuración para Azure
cat > deploy/startup.sh << 'EOF'
#!/bin/bash
# Script de inicio para Azure App Service

# Iniciar el servidor Node.js en segundo plano
node dist/index.js &
NODE_PID=$!

# Iniciar el servidor Python
python main.py &
PYTHON_PID=$!

# Esperar a que cualquiera de los procesos termine
wait $NODE_PID $PYTHON_PID
EOF

chmod +x deploy/startup.sh

echo "Paquete de despliegue creado en ./deploy/"
echo "Listo para desplegar a Azure App Service" 