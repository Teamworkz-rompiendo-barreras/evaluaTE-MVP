#!/bin/bash

# Script para detener todos los servicios de EvaluaTE
echo "🛑 Deteniendo todos los servicios de EvaluaTE..."

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

# Función para mostrar información final
show_info() {
    echo -e "${GREEN}🎉 ¡Todos los servicios detenidos!${NC}"
    echo ""
    echo -e "${BLUE}📋 Para reiniciar servicios:${NC}"
    echo -e "   🚀 Inicio completo: ${GREEN}./start_simple.sh${NC}"
    echo -e "   🔧 Solo backend:    ${GREEN}./start_backend_only.sh${NC}"
    echo -e "   🎨 Solo frontend:   ${GREEN}./start_frontend_only.sh${NC}"
    echo -e "   🔄 Reinicio completo: ${GREEN}./restart_all.sh${NC}"
    echo ""
    echo -e "${BLUE}📋 Puertos liberados:${NC}"
    echo -e "   🔧 Puerto 8000 (backend): ${GREEN}Libre${NC}"
    echo -e "   🎨 Puerto 5173 (frontend): ${GREEN}Libre${NC}"
    echo -e "   🎨 Puerto 3000 (alternativo): ${GREEN}Libre${NC}"
}

# Función principal
main() {
    echo -e "${BLUE}🛑 Iniciando detención de todos los servicios...${NC}"
    echo ""
    
    # Verificar que estamos en el directorio correcto
    if [ ! -f "backend/main.py" ]; then
        echo -e "${RED}❌ Error: No estás en el directorio raíz de EvaluaTE${NC}"
        echo -e "${BLUE}💡 Navega al directorio del proyecto y ejecuta este script${NC}"
        exit 1
    fi
    
    # Detener todos los servicios
    stop_all_services
    
    # Verificar que los puertos estén libres
    check_ports_free
    
    # Mostrar información final
    show_info
}

# Ejecutar función principal
main 