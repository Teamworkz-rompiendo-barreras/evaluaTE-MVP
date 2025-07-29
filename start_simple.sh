#!/bin/bash

# Script de inicio simplificado para EvaluaTE
echo "🚀 Iniciando EvaluaTE de forma simplificada..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para verificar si estamos en el directorio correcto
check_directory() {
    if [ ! -f "backend/main.py" ]; then
        echo -e "${RED}❌ Error: No estás en el directorio raíz de EvaluaTE${NC}"
        echo -e "${BLUE}💡 Navega al directorio del proyecto y ejecuta este script${NC}"
        exit 1
    fi
}

# Función para activar entorno virtual
activate_venv() {
    echo -e "${BLUE}🔍 Activando entorno virtual...${NC}"
    
    if [ ! -d "backend/venv" ]; then
        echo -e "${RED}❌ Entorno virtual no encontrado${NC}"
        echo -e "${YELLOW}🔧 Creando entorno virtual...${NC}"
        cd backend
        python3 -m venv venv
        cd ..
    fi
    
    source backend/venv/bin/activate
    
    if [ -z "$VIRTUAL_ENV" ]; then
        echo -e "${RED}❌ Error: No se pudo activar el entorno virtual${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Entorno virtual activado: $VIRTUAL_ENV${NC}"
}

# Función para verificar archivo .env
check_env_file() {
    if [ ! -f "backend/.env" ]; then
        echo -e "${YELLOW}⚠️  Archivo .env no encontrado${NC}"
        echo -e "${BLUE}📝 Creando archivo .env de ejemplo...${NC}"
        cat > "backend/.env" << EOF
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_ENDPOINT=your_endpoint_here
AZURE_OPENAI_DEPLOYMENT=your_deployment_here
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Database Configuration (if needed)
DATABASE_URL=your_database_url_here

# Other Configuration
DEBUG=True
LOG_LEVEL=INFO
EOF
        echo -e "${GREEN}✅ Archivo .env creado. Por favor, configura tus credenciales.${NC}"
    else
        echo -e "${GREEN}✅ Archivo .env encontrado${NC}"
    fi
}

# Función para iniciar backend
start_backend() {
    echo -e "${BLUE}🚀 Iniciando backend...${NC}"
    
    cd backend
    
    # Verificar si el puerto 8000 está ocupado
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${YELLOW}⚠️  Puerto 8000 ya está en uso${NC}"
        echo -e "${BLUE}💡 Deteniendo proceso anterior...${NC}"
        pkill -f "uvicorn.*main:app" || true
        sleep 2
    fi
    
    echo -e "${GREEN}✅ Iniciando servidor backend en puerto 8000...${NC}"
    python main.py &
    BACKEND_PID=$!
    
    cd ..
    
    # Esperar a que el backend esté listo
    echo -e "${BLUE}⏳ Esperando a que el backend esté listo...${NC}"
    for i in {1..30}; do
        if curl -s http://localhost:8000/ > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Backend iniciado correctamente${NC}"
            break
        fi
        if [ $i -eq 30 ]; then
            echo -e "${RED}❌ Timeout: Backend no respondió en 30 segundos${NC}"
            exit 1
        fi
        sleep 1
    done
}

# Función para iniciar frontend
start_frontend() {
    echo -e "${BLUE}🎨 Iniciando frontend...${NC}"
    
    cd nuevo-frontend
    
    # Verificar si el puerto 5173 está ocupado
    if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${YELLOW}⚠️  Puerto 5173 ya está en uso${NC}"
        echo -e "${BLUE}💡 Deteniendo proceso anterior...${NC}"
        pkill -f "vite" || true
        sleep 2
    fi
    
    echo -e "${GREEN}✅ Iniciando servidor frontend en puerto 5173...${NC}"
    npm run dev &
    FRONTEND_PID=$!
    
    cd ..
    
    # Esperar a que el frontend esté listo
    echo -e "${BLUE}⏳ Esperando a que el frontend esté listo...${NC}"
    for i in {1..30}; do
        if curl -s http://localhost:5173/ > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Frontend iniciado correctamente${NC}"
            break
        fi
        if [ $i -eq 30 ]; then
            echo -e "${RED}❌ Timeout: Frontend no respondió en 30 segundos${NC}"
            exit 1
        fi
        sleep 1
    done
}

# Función para mostrar información final
show_info() {
    echo -e "${GREEN}🎉 ¡EvaluaTE iniciado correctamente!${NC}"
    echo -e "${BLUE}📋 Información de acceso:${NC}"
    echo -e "   🌐 Frontend: ${GREEN}http://localhost:5173${NC}"
    echo -e "   🔧 Backend:  ${GREEN}http://localhost:8000${NC}"
    echo -e "   📚 API Docs: ${GREEN}http://localhost:8000/docs${NC}"
    echo ""
    echo -e "${YELLOW}💡 Para detener los servicios:${NC}"
    echo -e "   Presiona Ctrl+C en esta terminal"
    echo ""
    echo -e "${BLUE}🔍 Para ver logs:${NC}"
    echo -e "   Backend:  tail -f backend/logs/app.log"
    echo -e "   Frontend: cd nuevo-frontend && npm run dev"
}

# Función para limpiar al salir
cleanup() {
    echo -e "${YELLOW}🛑 Deteniendo servicios...${NC}"
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    pkill -f "uvicorn.*main:app" 2>/dev/null || true
    pkill -f "vite" 2>/dev/null || true
    echo -e "${GREEN}✅ Servicios detenidos${NC}"
    exit 0
}

# Configurar trap para limpiar al salir
trap cleanup SIGINT SIGTERM

# Ejecutar funciones principales
check_directory
activate_venv
check_env_file
start_backend
start_frontend
show_info

# Mantener el script ejecutándose
echo -e "${BLUE}⏳ Servicios ejecutándose... Presiona Ctrl+C para detener${NC}"
wait 