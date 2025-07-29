#!/bin/bash

# Script para iniciar solo el frontend de EvaluaTE
echo "🎨 Iniciando solo el frontend de EvaluaTE..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para verificar si estamos en el directorio correcto
check_directory() {
    if [ ! -f "nuevo-frontend/package.json" ]; then
        echo -e "${RED}❌ Error: No estás en el directorio raíz de EvaluaTE${NC}"
        echo -e "${BLUE}💡 Navega al directorio del proyecto y ejecuta este script${NC}"
        exit 1
    fi
}

# Función para verificar dependencias de Node.js
check_node_deps() {
    echo -e "${BLUE}📦 Verificando dependencias de Node.js...${NC}"
    
    cd nuevo-frontend
    
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}⚠️  node_modules no encontrado${NC}"
        echo -e "${BLUE}📦 Instalando dependencias...${NC}"
        npm install
    else
        echo -e "${GREEN}✅ Dependencias de Node.js encontradas${NC}"
    fi
    
    cd ..
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
    echo -e "${GREEN}🎉 ¡Frontend iniciado correctamente!${NC}"
    echo -e "${BLUE}📋 Información de acceso:${NC}"
    echo -e "   🌐 Frontend: ${GREEN}http://localhost:5173${NC}"
    echo ""
    echo -e "${YELLOW}💡 Para iniciar el backend en otra terminal:${NC}"
    echo -e "   ./start_backend_only.sh"
    echo ""
    echo -e "${YELLOW}💡 Para detener el frontend:${NC}"
    echo -e "   Presiona Ctrl+C en esta terminal"
    echo ""
    echo -e "${BLUE}🔍 Para ver logs:${NC}"
    echo -e "   cd nuevo-frontend && npm run dev"
}

# Función para limpiar al salir
cleanup() {
    echo -e "${YELLOW}🛑 Deteniendo frontend...${NC}"
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    pkill -f "vite" 2>/dev/null || true
    echo -e "${GREEN}✅ Frontend detenido${NC}"
    exit 0
}

# Configurar trap para limpiar al salir
trap cleanup SIGINT SIGTERM

# Ejecutar funciones principales
check_directory
check_node_deps
start_frontend
show_info

# Mantener el script ejecutándose
echo -e "${BLUE}⏳ Frontend ejecutándose... Presiona Ctrl+C para detener${NC}"
wait 