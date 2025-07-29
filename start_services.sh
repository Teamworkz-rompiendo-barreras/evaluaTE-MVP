#!/bin/bash

# Script de inicio para EvaluaTE - Siempre activa el entorno correcto
echo "🚀 Iniciando servicios de EvaluaTE..."

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

# Función para verificar y activar entorno virtual
activate_venv() {
    echo -e "${BLUE}🔍 Verificando entorno virtual...${NC}"
    
    if [ ! -d "backend/venv" ]; then
        echo -e "${RED}❌ Entorno virtual no encontrado${NC}"
        echo -e "${YELLOW}🔧 Creando entorno virtual...${NC}"
        cd backend
        python3 -m venv venv
        cd ..
    fi
    
    echo -e "${GREEN}✅ Activando entorno virtual...${NC}"
    source backend/venv/bin/activate
    
    # Verificar que el entorno está activado
    if [ -z "$VIRTUAL_ENV" ]; then
        echo -e "${RED}❌ Error: No se pudo activar el entorno virtual${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}🎉 Entorno virtual activado: $VIRTUAL_ENV${NC}"
}

# Función para verificar dependencias críticas
check_critical_deps() {
    echo -e "${BLUE}📋 Verificando dependencias críticas...${NC}"
    
    local critical_deps=(
        "fastapi"
        "uvicorn"
        "openai"
        "PyMuPDF"
        "python-dotenv"
    )
    
    local missing_deps=()
    
    for dep in "${critical_deps[@]}"; do
        if ! python -c "import ${dep//-/_}" 2>/dev/null; then
            echo -e "${YELLOW}⚠️  Faltante: $dep${NC}"
            missing_deps+=("$dep")
        else
            echo -e "${GREEN}✅ $dep${NC}"
        fi
    done
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        echo -e "${YELLOW}📦 Instalando dependencias faltantes...${NC}"
        pip install "${missing_deps[@]}"
        
        # Verificar instalación
        for dep in "${missing_deps[@]}"; do
            if python -c "import ${dep//-/_}" 2>/dev/null; then
                echo -e "${GREEN}✅ $dep instalado correctamente${NC}"
            else
                echo -e "${RED}❌ Error instalando $dep${NC}"
                echo -e "${YELLOW}💡 Ejecuta: ./fix_dependencies.sh${NC}"
                exit 1
            fi
        done
    fi
}

# Función para verificar variables de entorno
check_env_file() {
    echo -e "${BLUE}🔐 Verificando archivo .env...${NC}"
    
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
    echo -e "${BLUE}🚀 Iniciando frontend...${NC}"
    
    if [ ! -d "nuevo-frontend" ]; then
        echo -e "${RED}❌ Directorio nuevo-frontend no encontrado${NC}"
        return 1
    fi
    
    cd nuevo-frontend
    
    # Verificar si node_modules existe
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}⚠️  node_modules no encontrado, instalando dependencias...${NC}"
        npm install
    fi
    
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
            echo -e "${YELLOW}⚠️  Timeout: Frontend no respondió en 30 segundos${NC}"
            break
        fi
        sleep 1
    done
}

# Función para mostrar información final
show_info() {
    echo -e "${GREEN}🎉 ¡Servicios iniciados correctamente!${NC}"
    echo -e "${BLUE}📋 Información de acceso:${NC}"
    echo -e "   🌐 Frontend: http://localhost:5173"
    echo -e "   🔧 Backend: http://localhost:8000"
    echo -e "   📚 API Docs: http://localhost:8000/docs"
    echo -e ""
    echo -e "${BLUE}💡 Comandos útiles:${NC}"
    echo -e "   📊 Ver logs del backend: tail -f backend/logs/app.log"
    echo -e "   🛑 Detener servicios: pkill -f 'python main.py' && pkill -f 'vite'"
    echo -e "   🔄 Reiniciar: ./start_services.sh"
    echo -e ""
    echo -e "${YELLOW}⚠️  Para detener los servicios, presiona Ctrl+C${NC}"
}

# Función para limpiar al salir
cleanup() {
    echo -e "${BLUE}🛑 Deteniendo servicios...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    pkill -f "python main.py" || true
    pkill -f "vite" || true
    echo -e "${GREEN}✅ Servicios detenidos${NC}"
    exit 0
}

# Capturar Ctrl+C
trap cleanup SIGINT

# Función principal
main() {
    echo -e "${BLUE}🚀 Iniciando EvaluaTE...${NC}"
    
    # Verificar directorio
    check_directory
    
    # Activar entorno virtual
    activate_venv
    
    # Verificar dependencias críticas
    check_critical_deps
    
    # Verificar archivo .env
    check_env_file
    
    # Iniciar backend
    start_backend
    
    # Iniciar frontend
    start_frontend
    
    # Mostrar información
    show_info
    
    # Mantener el script ejecutándose
    while true; do
        sleep 1
    done
}

# Ejecutar función principal
main "$@" 