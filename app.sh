#!/bin/bash

# Script único para EvaluaTE - Funcionalidades esenciales
echo "🚀 EvaluaTE - Script de Control"
echo "==============================="

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Función para activar entorno virtual
activate_env() {
    if [ ! -d ".venv" ]; then
        echo -e "${RED}❌ Entorno virtual no encontrado${NC}"
        exit 1
    fi
    source .venv/bin/activate
    echo -e "${GREEN}✅ Entorno virtual activado${NC}"
}

# Función para iniciar servicios
start() {
    echo -e "${BLUE}🚀 Iniciando servicios...${NC}"
    
    activate_env
    
    # Iniciar backend
    echo -e "${YELLOW}Iniciando backend...${NC}"
    cd backend
    python main.py &
    BACKEND_PID=$!
    cd ..
    
    # Esperar backend
    sleep 5
    
    # Iniciar frontend
    echo -e "${YELLOW}Iniciando frontend...${NC}"
    cd nuevo-frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    echo -e "${GREEN}✅ Servicios iniciados${NC}"
    echo -e "${BLUE}Backend: http://localhost:8000${NC}"
    echo -e "${BLUE}Frontend: http://localhost:3005${NC}"
}

# Función para detener servicios
stop() {
    echo -e "${BLUE}🛑 Deteniendo servicios...${NC}"
    
    pkill -f "python main.py" 2>/dev/null || true
    pkill -f "vite" 2>/dev/null || true
    pkill -f "npm" 2>/dev/null || true
    
    echo -e "${GREEN}✅ Servicios detenidos${NC}"
}

# Función para limpiar recursos
clean() {
    echo -e "${BLUE}🧹 Limpiando recursos...${NC}"
    
    # Detener Cursor si consume mucha memoria
    CURSOR_MEMORY=$(ps aux | grep -E "(cursor-server|bootstrap-fork)" | grep -v grep | awk '{sum+=$6} END {print sum/1024}')
    if [ -n "$CURSOR_MEMORY" ] && (( $(echo "$CURSOR_MEMORY > 400" | bc -l) )); then
        echo -e "${YELLOW}Deteniendo Cursor (consumía ${CURSOR_MEMORY}MB)...${NC}"
        pkill -f "cursor-server" 2>/dev/null || true
    fi
    
    # Limpiar caché
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    
    echo -e "${GREEN}✅ Limpieza completada${NC}"
}

# Función para mostrar estado
status() {
    echo -e "${BLUE}📊 Estado de servicios:${NC}"
    
    if lsof -i :8000 >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend: Activo${NC}"
    else
        echo -e "${RED}❌ Backend: Inactivo${NC}"
    fi
    
    if lsof -i :3005 >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Frontend: Activo${NC}"
    else
        echo -e "${RED}❌ Frontend: Inactivo${NC}"
    fi
    
    # Memoria disponible
    MEM_AVAILABLE=$(free -h | grep Mem | awk '{print $7}')
    echo -e "${BLUE}💾 Memoria disponible: $MEM_AVAILABLE${NC}"
}

# Función para mostrar ayuda
help() {
    echo -e "${BLUE}📋 Comandos disponibles:${NC}"
    echo "  start   - Iniciar servicios"
    echo "  stop    - Detener servicios"
    echo "  restart - Reiniciar servicios con verificación"
    echo "  status  - Mostrar estado"
    echo "  check   - Verificar conectividad"
    echo "  clean   - Limpiar recursos"
    echo "  help    - Mostrar esta ayuda"
}

# Función para verificar conectividad
check_connectivity() {
    echo -e "${BLUE}🔍 Verificando conectividad...${NC}"
    
    # Verificar backend
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend responde correctamente${NC}"
    else
        echo -e "${RED}❌ Backend no responde${NC}"
        return 1
    fi
    
    # Verificar frontend
    if curl -s http://localhost:3005 >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Frontend responde correctamente${NC}"
    else
        echo -e "${RED}❌ Frontend no responde${NC}"
        return 1
    fi
    
    return 0
}

# Función para reiniciar con verificación
restart_with_check() {
    echo -e "${BLUE}🔄 Reiniciando servicios con verificación...${NC}"
    stop
    sleep 3
    start
    sleep 5
    
    if check_connectivity; then
        echo -e "${GREEN}✅ Reinicio exitoso${NC}"
    else
        echo -e "${RED}❌ Problemas detectados después del reinicio${NC}"
        return 1
    fi
}

# Función principal
case "$1" in
    "start")
        start
        ;;
    "stop")
        stop
        ;;
    "restart")
        restart_with_check
        ;;
    "check")
        check_connectivity
        ;;
    "status")
        status
        ;;
    "clean")
        clean
        ;;
    "help"|"")
        help
        ;;
    *)
        echo -e "${RED}❌ Comando desconocido: $1${NC}"
        help
        exit 1
        ;;
esac 