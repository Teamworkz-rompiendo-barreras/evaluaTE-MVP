#!/bin/bash

echo "🚀 Iniciando servicios de EvaluaTE MVP..."
echo "=========================================="

# Función para verificar si un puerto está en uso
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "⚠️  Puerto $1 ya está en uso"
        return 1
    else
        echo "✅ Puerto $1 disponible"
        return 0
    fi
}

# Función para activar el entorno virtual
activate_venv() {
    if [ -d "venv" ]; then
        echo "🔧 Activando entorno virtual..."
        source venv/bin/activate
        echo "✅ Entorno virtual activado"
        return 0
    elif [ -d ".venv" ]; then
        echo "🔧 Activando entorno virtual..."
        source .venv/bin/activate
        echo "✅ Entorno virtual activado"
        return 0
    else
        echo "❌ No se encontró el entorno virtual"
        echo "💡 Crea el entorno virtual con: python -m venv venv"
        return 1
    fi
}

# Función para instalar dependencias del backend
install_backend_deps() {
    echo "📦 Instalando dependencias del backend..."
    cd backend
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        echo "✅ Dependencias del backend instaladas"
    else
        echo "⚠️  No se encontró requirements.txt en el backend"
    fi
    cd ..
}

# Función para instalar dependencias del frontend
install_frontend_deps() {
    echo "📦 Instalando dependencias del frontend..."
    cd nuevo-frontend
    if [ -f "package.json" ]; then
        npm install
        echo "✅ Dependencias del frontend instaladas"
    else
        echo "⚠️  No se encontró package.json en el frontend"
    fi
    cd ..
}

# Función para arrancar el backend
start_backend() {
    echo "🔧 Iniciando backend..."
    cd backend
    
    # Verificar si main.py existe
    if [ ! -f "main.py" ]; then
        echo "❌ No se encontró main.py en el backend"
        cd ..
        return 1
    fi
    
    # Verificar puerto 8000
    if ! check_port 8000; then
        echo "💡 El backend se ejecutará en el puerto 8000"
    fi
    
    echo "🚀 Ejecutando backend con uvicorn y timeouts extendidos..."
    # Usar configuración con timeouts extendidos
    python uvicorn_config.py &
    BACKEND_PID=$!
    echo "✅ Backend iniciado con timeouts extendidos (PID: $BACKEND_PID)"
    cd ..
}

# Función para arrancar el frontend
start_frontend() {
    echo "🔧 Iniciando frontend..."
    cd nuevo-frontend
    
    # Verificar si package.json existe
    if [ ! -f "package.json" ]; then
        echo "❌ No se encontró package.json en el frontend"
        cd ..
        return 1
    fi
    
    # Verificar puerto 3005
    if ! check_port 3005; then
        echo "💡 El frontend se ejecutará en el puerto 3005"
    fi
    
    echo "🚀 Ejecutando frontend con npm run dev..."
    npm run dev &
    FRONTEND_PID=$!
    echo "✅ Frontend iniciado (PID: $FRONTEND_PID)"
    cd ..
}

# Función para mostrar información de los servicios
show_info() {
    echo ""
    echo "📋 Información de los servicios:"
    echo "================================"
    echo "🔧 Backend: http://localhost:8000"
    echo "🌐 Frontend: http://localhost:3005"
    echo "📚 API Docs: http://localhost:8000/docs"
    echo ""
    echo "💡 Para detener los servicios, presiona Ctrl+C"
    echo ""
}

# Función para limpiar procesos al salir
cleanup() {
    echo ""
    echo "🛑 Deteniendo servicios..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo "✅ Backend detenido"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "✅ Frontend detenido"
    fi
    echo "👋 ¡Hasta luego!"
    exit 0
}

# Capturar Ctrl+C para limpiar procesos
trap cleanup SIGINT

# Ejecutar el script principal
main() {
    # Activar entorno virtual
    if ! activate_venv; then
        exit 1
    fi
    
    # Instalar dependencias si es necesario
    read -p "¿Instalar dependencias? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        install_backend_deps
        install_frontend_deps
    fi
    
    # Arrancar servicios
    start_backend
    start_frontend
    
    # Mostrar información
    show_info
    
    # Mantener el script ejecutándose
    echo "⏳ Servicios ejecutándose... Presiona Ctrl+C para detener"
    wait
}

# Ejecutar función principal
main 