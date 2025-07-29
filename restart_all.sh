#!/bin/bash

# Script para detener todos los servicios y reiniciar EvaluaTE
echo "🔄 Reiniciando EvaluaTE completamente..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para detener todos los servicios
stop_all_services() {
    echo -e "${BLUE}🛑 Deteniendo todos los servicios...${NC}"
    
    # Detener procesos de backend
    echo -e "${YELLOW}📋 Deteniendo procesos de backend...${NC}"
    pkill -f "uvicorn.*main:app" 2>/dev/null || true
    pkill -f "python.*main.py" 2>/dev/null || true
    pkill -f "fastapi" 2>/dev/null || true
    
    # Detener procesos de frontend
    echo -e "${YELLOW}📋 Deteniendo procesos de frontend...${NC}"
    pkill -f "vite" 2>/dev/null || true
    pkill -f "npm.*run.*dev" 2>/dev/null || true
    pkill -f "node.*vite" 2>/dev/null || true
    
    # Detener procesos en puertos específicos
    echo -e "${YELLOW}📋 Liberando puertos...${NC}"
    
    # Puerto 8000 (backend)
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${YELLOW}   🔧 Liberando puerto 8000...${NC}"
        lsof -Pi :8000 -sTCP:LISTEN -t | xargs kill -9 2>/dev/null || true
    fi
    
    # Puerto 5173 (frontend)
    if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${YELLOW}   🎨 Liberando puerto 5173...${NC}"
        lsof -Pi :5173 -sTCP:LISTEN -t | xargs kill -9 2>/dev/null || true
    fi
    
    # Puerto 3000 (alternativo frontend)
    if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${YELLOW}   🎨 Liberando puerto 3000...${NC}"
        lsof -Pi :3000 -sTCP:LISTEN -t | xargs kill -9 2>/dev/null || true
    fi
    
    # Esperar un momento para que los procesos se cierren
    sleep 3
    
    echo -e "${GREEN}✅ Todos los servicios detenidos${NC}"
}

# Función para verificar que los puertos estén libres
check_ports_free() {
    echo -e "${BLUE}🔍 Verificando que los puertos estén libres...${NC}"
    
    local ports=(8000 5173 3000)
    local all_free=true
    
    for port in "${ports[@]}"; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
            echo -e "${RED}❌ Puerto $port aún está ocupado${NC}"
            all_free=false
        else
            echo -e "${GREEN}✅ Puerto $port libre${NC}"
        fi
    done
    
    if [ "$all_free" = false ]; then
        echo -e "${YELLOW}⚠️  Algunos puertos aún están ocupados. Intentando forzar cierre...${NC}"
        sleep 2
        stop_all_services
        sleep 3
    fi
}

# Función para limpiar archivos temporales
cleanup_temp_files() {
    echo -e "${BLUE}🧹 Limpiando archivos temporales...${NC}"
    
    # Limpiar archivos de Python
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyo" -delete 2>/dev/null || true
    
    # Limpiar archivos de Node.js
    find . -name "node_modules/.cache" -type d -exec rm -rf {} + 2>/dev/null || true
    
    # Limpiar logs temporales
    find . -name "*.log" -size +10M -delete 2>/dev/null || true
    
    echo -e "${GREEN}✅ Limpieza completada${NC}"
}

# Función para verificar estructura del proyecto
check_project_structure() {
    echo -e "${BLUE}📁 Verificando estructura del proyecto...${NC}"
    
    local required_files=(
        "backend/main.py"
        "backend/cv_analyzer.py"
        "nuevo-frontend/package.json"
        "start_simple.sh"
    )
    
    for file in "${required_files[@]}"; do
        if [ -f "$file" ]; then
            echo -e "${GREEN}✅ $file${NC}"
        else
            echo -e "${RED}❌ $file no encontrado${NC}"
            return 1
        fi
    done
    
    echo -e "${GREEN}✅ Estructura del proyecto correcta${NC}"
    return 0
}

# Función para reiniciar servicios
restart_services() {
    echo -e "${BLUE}🚀 Reiniciando servicios...${NC}"
    
    # Verificar que los puertos estén libres
    check_ports_free
    
    # Iniciar servicios usando el script simplificado
    echo -e "${GREEN}🎉 Iniciando EvaluaTE...${NC}"
    ./start_simple.sh
}

# Función principal
main() {
    echo -e "${BLUE}🔄 Iniciando reinicio completo de EvaluaTE...${NC}"
    echo ""
    
    # Verificar que estamos en el directorio correcto
    if [ ! -f "backend/main.py" ]; then
        echo -e "${RED}❌ Error: No estás en el directorio raíz de EvaluaTE${NC}"
        echo -e "${BLUE}💡 Navega al directorio del proyecto y ejecuta este script${NC}"
        exit 1
    fi
    
    # Detener todos los servicios
    stop_all_services
    
    # Limpiar archivos temporales
    cleanup_temp_files
    
    # Verificar estructura del proyecto
    if ! check_project_structure; then
        echo -e "${RED}❌ Error en la estructura del proyecto${NC}"
        exit 1
    fi
    
    # Esperar un momento antes de reiniciar
    echo -e "${BLUE}⏳ Esperando 5 segundos antes de reiniciar...${NC}"
    sleep 5
    
    # Reiniciar servicios
    restart_services
}

# Ejecutar función principal
main 