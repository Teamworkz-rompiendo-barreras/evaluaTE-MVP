#!/bin/bash

# Script de inicio para modo PRODUCCIÓN - EvaluaTE
echo "🚀 EvaluaTE - Inicio en MODO PRODUCCIÓN"
echo "========================================"

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Función para verificar dependencias
check_dependencies() {
    echo -e "${BLUE}🔍 Verificando dependencias...${NC}"
    
    if ! command -v python3 >/dev/null 2>&1; then
        echo -e "${RED}❌ Python3 no encontrado${NC}"
        exit 1
    fi
    
    if ! command -v node >/dev/null 2>&1; then
        echo -e "${RED}❌ Node.js no encontrado${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Dependencias verificadas${NC}"
}

# Función para optimización de producción
production_optimization() {
    echo -e "${BLUE}⚙️  Aplicando optimizaciones de producción...${NC}"
    
    # Optimización de memoria
    if [ -f /proc/sys/vm/swappiness ]; then
        echo 5 | sudo tee /proc/sys/vm/swappiness >/dev/null 2>&1
    fi
    
    # Limpiar archivos temporales
    sudo rm -rf /tmp/* >/dev/null 2>&1
    sudo rm -rf /var/tmp/* >/dev/null 2>&1
    
    # Ajustar límites para producción
    ulimit -n 65536 >/dev/null 2>&1
    ulimit -u 32768 >/dev/null 2>&1
    
    echo -e "${GREEN}✅ Optimizaciones aplicadas${NC}"
}

# Función para build del frontend
build_frontend() {
    echo -e "${BLUE}🏗️  Construyendo frontend para producción...${NC}"
    
    cd nuevo-frontend
    
    # Limpiar build anterior
    rm -rf dist
    
    # Instalar dependencias si es necesario
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}📦 Instalando dependencias del frontend...${NC}"
        npm install
    fi
    
    # Build de producción
    echo -e "${YELLOW}🔨 Ejecutando build de producción...${NC}"
    npm run build
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Frontend construido exitosamente${NC}"
    else
        echo -e "${RED}❌ Error construyendo frontend${NC}"
        exit 1
    fi
    
    cd ..
}

# Función para verificar entorno virtual
check_virtual_env() {
    echo -e "${BLUE}🐍 Verificando entorno virtual...${NC}"
    
    if [ ! -d ".venv" ]; then
        echo -e "${RED}❌ Entorno virtual no encontrado${NC}"
        exit 1
    fi
    
    if [ ! -f ".venv/bin/activate" ]; then
        echo -e "${RED}❌ Entorno virtual corrupto${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Entorno virtual verificado${NC}"
}

# Función para verificar dependencias de Python
check_python_deps() {
    echo -e "${BLUE}📦 Verificando dependencias de Python...${NC}"
    
    source .venv/bin/activate
    
    if ! python -c "import fastapi, uvicorn" 2>/dev/null; then
        echo -e "${YELLOW}📦 Instalando dependencias de Python...${NC}"
        pip install -r backend/requirements.txt
    fi
    
    echo -e "${GREEN}✅ Dependencias de Python verificadas${NC}"
}

# Función para verificar configuración
check_configuration() {
    echo -e "${BLUE}⚙️  Verificando configuración...${NC}"
    
    if [ ! -f "backend/.env" ]; then
        echo -e "${RED}❌ Archivo .env no encontrado en backend${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Configuración verificada${NC}"
}

# Función para iniciar backend en modo producción
start_backend_production() {
    echo -e "${BLUE}🚀 Iniciando backend en modo producción...${NC}"
    
    cd backend
    
    # Configuración optimizada para producción
    export PYTHONPATH="${PYTHONPATH}:$(pwd)"
    
    # Iniciar con configuración de producción
    export PRODUCTION=true
    python main.py &
    BACKEND_PID=$!
    
    cd ..
    
    # Esperar a que el backend esté listo
    echo -e "${YELLOW}⏳ Esperando que el backend esté listo...${NC}"
    sleep 10
    
    # Verificar que el backend esté funcionando
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend iniciado correctamente${NC}"
    else
        echo -e "${RED}❌ Backend no responde${NC}"
        exit 1
    fi
}

# Función para servir frontend en modo producción
serve_frontend_production() {
    echo -e "${BLUE}🌐 Sirviendo frontend en modo producción...${NC}"
    
    cd nuevo-frontend
    
    # Usar un servidor estático ligero para producción
    if command -v npx >/dev/null 2>&1; then
        echo -e "${YELLOW}🚀 Iniciando servidor estático...${NC}"
        npx serve -s dist -l 3005 &
        FRONTEND_PID=$!
    else
        echo -e "${YELLOW}📦 Instalando serve...${NC}"
        npm install -g serve
        serve -s dist -l 3005 &
        FRONTEND_PID=$!
    fi
    
    cd ..
    
    # Esperar a que el frontend esté listo
    sleep 5
    
    # Verificar que el frontend esté funcionando
    if curl -s http://localhost:3005 >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Frontend servido correctamente${NC}"
    else
        echo -e "${RED}❌ Frontend no responde${NC}"
        exit 1
    fi
}

# Función para mostrar información final
show_final_info() {
    echo -e "${BLUE}📊 Información de acceso (PRODUCCIÓN):${NC}"
    echo -e "${GREEN}   🔧 Backend:  http://localhost:8000${NC}"
    echo -e "${GREEN}   📚 API Docs: http://localhost:8000/docs${NC}"
    echo -e "${GREEN}   🔍 Health:   http://localhost:8000/health${NC}"
    echo -e "${GREEN}   🌐 Frontend: http://localhost:3005${NC}"
    echo ""
    echo -e "${BLUE}📋 Comandos útiles:${NC}"
    echo -e "${YELLOW}   ./app.sh status    - Ver estado de servicios${NC}"
    echo -e "${YELLOW}   ./app.sh check     - Verificar conectividad${NC}"
    echo -e "${YELLOW}   ./app.sh stop      - Detener servicios${NC}"
    echo ""
    echo -e "${GREEN}🎉 ¡EvaluaTE está ejecutándose en MODO PRODUCCIÓN!${NC}"
    echo -e "${YELLOW}💡 Este modo es más estable y optimizado para uso real${NC}"
}

# Función para limpiar al salir
cleanup() {
    echo -e "${BLUE}🧹 Limpiando recursos...${NC}"
    
    # Detener procesos
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    # Detener otros servicios
    ./app.sh stop
}

# Capturar señal de interrupción
trap cleanup SIGINT SIGTERM

# Función principal
main() {
    echo -e "${BLUE}🚀 Iniciando EvaluaTE en modo PRODUCCIÓN...${NC}"
    
    # Verificar dependencias del sistema
    check_dependencies
    
    # Aplicar optimizaciones de producción
    production_optimization
    
    # Verificar entorno virtual
    check_virtual_env
    
    # Verificar dependencias de Python
    check_python_deps
    
    # Verificar configuración
    check_configuration
    
    # Construir frontend para producción
    build_frontend
    
    # Iniciar backend en modo producción
    start_backend_production
    
    # Servir frontend en modo producción
    serve_frontend_production
    
    # Mostrar información final
    show_final_info
    
    # Mantener el script corriendo
    echo -e "${BLUE}🔄 Manteniendo servicios activos... (Ctrl+C para detener)${NC}"
    wait
}

# Ejecutar función principal
main "$@" 