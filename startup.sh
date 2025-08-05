#!/bin/bash

# Script de inicio automático para EvaluaTE
echo "🚀 EvaluaTE - Inicio Automático Optimizado"
echo "=========================================="

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Función para verificar dependencias
check_dependencies() {
    echo -e "${BLUE}🔍 Verificando dependencias...${NC}"
    
    # Verificar Python
    if ! command -v python3 >/dev/null 2>&1; then
        echo -e "${RED}❌ Python3 no encontrado${NC}"
        return 1
    fi
    
    # Verificar Node.js
    if ! command -v node >/dev/null 2>&1; then
        echo -e "${RED}❌ Node.js no encontrado${NC}"
        return 1
    fi
    
    # Verificar npm
    if ! command -v npm >/dev/null 2>&1; then
        echo -e "${RED}❌ npm no encontrado${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✅ Dependencias verificadas${NC}"
    return 0
}

# Función para optimización inicial
initial_optimization() {
    echo -e "${BLUE}⚙️  Aplicando optimizaciones iniciales...${NC}"
    
    # Optimización básica de memoria
    if [ -f /proc/sys/vm/swappiness ]; then
        echo 10 | sudo tee /proc/sys/vm/swappiness >/dev/null 2>&1
    fi
    
    # Limpiar archivos temporales
    sudo rm -rf /tmp/* >/dev/null 2>&1
    sudo rm -rf /var/tmp/* >/dev/null 2>&1
    
    # Ajustar límites básicos
    ulimit -n 65536 >/dev/null 2>&1
    ulimit -u 32768 >/dev/null 2>&1
    
    echo -e "${GREEN}✅ Optimizaciones aplicadas${NC}"
}

# Función para verificar entorno virtual
check_virtual_env() {
    echo -e "${BLUE}🐍 Verificando entorno virtual...${NC}"
    
    if [ ! -d ".venv" ]; then
        echo -e "${RED}❌ Entorno virtual no encontrado${NC}"
        echo -e "${YELLOW}💡 Creando entorno virtual...${NC}"
        python3 -m venv .venv
    fi
    
    if [ ! -f ".venv/bin/activate" ]; then
        echo -e "${RED}❌ Entorno virtual corrupto${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✅ Entorno virtual verificado${NC}"
    return 0
}

# Función para verificar dependencias de Python
check_python_deps() {
    echo -e "${BLUE}📦 Verificando dependencias de Python...${NC}"
    
    source .venv/bin/activate
    
    # Verificar si requirements.txt existe
    if [ ! -f "backend/requirements.txt" ]; then
        echo -e "${RED}❌ requirements.txt no encontrado${NC}"
        return 1
    fi
    
    # Verificar dependencias críticas
    if ! python -c "import fastapi, uvicorn" 2>/dev/null; then
        echo -e "${YELLOW}📦 Instalando dependencias de Python...${NC}"
        pip install -r backend/requirements.txt
    fi
    
    echo -e "${GREEN}✅ Dependencias de Python verificadas${NC}"
    return 0
}

# Función para verificar dependencias de Node.js
check_node_deps() {
    echo -e "${BLUE}📦 Verificando dependencias de Node.js...${NC}"
    
    if [ ! -f "nuevo-frontend/package.json" ]; then
        echo -e "${RED}❌ package.json no encontrado${NC}"
        return 1
    fi
    
    # Verificar si node_modules existe
    if [ ! -d "nuevo-frontend/node_modules" ]; then
        echo -e "${YELLOW}📦 Instalando dependencias de Node.js...${NC}"
        cd nuevo-frontend
        npm install
        cd ..
    fi
    
    echo -e "${GREEN}✅ Dependencias de Node.js verificadas${NC}"
    return 0
}

# Función para verificar configuración
check_configuration() {
    echo -e "${BLUE}⚙️  Verificando configuración...${NC}"
    
    # Verificar archivo .env del backend
    if [ ! -f "backend/.env" ]; then
        echo -e "${RED}❌ Archivo .env no encontrado en backend${NC}"
        echo -e "${YELLOW}💡 Copia backend/env.example a backend/.env y configura las variables${NC}"
        return 1
    fi
    
    # Verificar que las variables críticas estén configuradas
    if ! grep -q "AZURE_OPENAI_API_KEY" backend/.env; then
        echo -e "${YELLOW}⚠️  AZURE_OPENAI_API_KEY no configurada${NC}"
    fi
    
    echo -e "${GREEN}✅ Configuración verificada${NC}"
    return 0
}

# Función para iniciar servicios
start_services() {
    echo -e "${BLUE}🚀 Iniciando servicios...${NC}"
    
    # Iniciar servicios usando el script principal
    ./app.sh start
    
    # Esperar a que los servicios estén listos
    sleep 10
    
    # Verificar conectividad
    if ./app.sh check; then
        echo -e "${GREEN}✅ Servicios iniciados correctamente${NC}"
        return 0
    else
        echo -e "${RED}❌ Problemas al iniciar servicios${NC}"
        return 1
    fi
}

# Función para iniciar monitoreo
start_monitoring() {
    echo -e "${BLUE}🔍 Iniciando monitoreo automático...${NC}"
    
    # Verificar si ya hay un monitor ejecutándose
    if pgrep -f "monitor.sh start" >/dev/null; then
        echo -e "${YELLOW}⚠️  Monitor ya está ejecutándose${NC}"
        return 0
    fi
    
    # Iniciar monitor en segundo plano
    nohup ./monitor.sh start > monitor.log 2>&1 &
    MONITOR_PID=$!
    
    echo $MONITOR_PID > monitor.pid
    echo -e "${GREEN}✅ Monitor iniciado (PID: $MONITOR_PID)${NC}"
    return 0
}

# Función para mostrar información final
show_final_info() {
    echo -e "${BLUE}📊 Información de acceso:${NC}"
    echo -e "${GREEN}   🔧 Backend:  http://localhost:8000${NC}"
    echo -e "${GREEN}   📚 API Docs: http://localhost:8000/docs${NC}"
    echo -e "${GREEN}   🔍 Health:   http://localhost:8000/health${NC}"
    echo -e "${GREEN}   🌐 Frontend: http://localhost:3005${NC}"
    echo ""
    echo -e "${BLUE}📋 Comandos útiles:${NC}"
    echo -e "${YELLOW}   ./app.sh status    - Ver estado de servicios${NC}"
    echo -e "${YELLOW}   ./app.sh check     - Verificar conectividad${NC}"
    echo -e "${YELLOW}   ./monitor.sh stats - Ver estadísticas del monitor${NC}"
    echo -e "${YELLOW}   tail -f monitor.log - Ver logs en tiempo real${NC}"
    echo ""
    echo -e "${GREEN}🎉 ¡EvaluaTE está listo para usar!${NC}"
}

# Función principal
main() {
    echo -e "${BLUE}🚀 Iniciando EvaluaTE con optimizaciones...${NC}"
    
    # Verificar dependencias del sistema
    if ! check_dependencies; then
        echo -e "${RED}❌ Dependencias del sistema no cumplidas${NC}"
        exit 1
    fi
    
    # Aplicar optimizaciones iniciales
    initial_optimization
    
    # Verificar entorno virtual
    if ! check_virtual_env; then
        echo -e "${RED}❌ Problemas con el entorno virtual${NC}"
        exit 1
    fi
    
    # Verificar dependencias de Python
    if ! check_python_deps; then
        echo -e "${RED}❌ Problemas con dependencias de Python${NC}"
        exit 1
    fi
    
    # Verificar dependencias de Node.js
    if ! check_node_deps; then
        echo -e "${RED}❌ Problemas con dependencias de Node.js${NC}"
        exit 1
    fi
    
    # Verificar configuración
    if ! check_configuration; then
        echo -e "${YELLOW}⚠️  Problemas de configuración detectados${NC}"
        echo -e "${YELLOW}💡 Revisa la configuración antes de continuar${NC}"
        read -p "¿Continuar de todas formas? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # Iniciar servicios
    if ! start_services; then
        echo -e "${RED}❌ No se pudieron iniciar los servicios${NC}"
        exit 1
    fi
    
    # Iniciar monitoreo
    start_monitoring
    
    # Mostrar información final
    show_final_info
}

# Función para limpiar al salir
cleanup() {
    echo -e "${BLUE}🧹 Limpiando recursos...${NC}"
    
    # Detener monitor si está ejecutándose
    if [ -f monitor.pid ]; then
        MONITOR_PID=$(cat monitor.pid)
        if kill -0 $MONITOR_PID 2>/dev/null; then
            kill $MONITOR_PID
            echo -e "${GREEN}✅ Monitor detenido${NC}"
        fi
        rm -f monitor.pid
    fi
    
    # Detener servicios
    ./app.sh stop
}

# Capturar señal de interrupción
trap cleanup SIGINT SIGTERM

# Ejecutar función principal
main "$@" 