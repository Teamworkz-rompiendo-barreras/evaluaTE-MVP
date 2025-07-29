#!/bin/bash

echo "🔧 Solucionando problemas de dependencias..."
echo "============================================="

# Función para activar entorno virtual
activate_venv() {
    if [ -d "venv" ]; then
        source venv/bin/activate
        echo "✅ Entorno virtual activado desde ./venv"
        return 0
    elif [ -d ".venv" ]; then
        source .venv/bin/activate
        echo "✅ Entorno virtual activado desde ./.venv"
        return 0
    else
        echo "❌ No se encontró el entorno virtual"
        return 1
    fi
}

# Función para limpiar cache de pip
clean_pip_cache() {
    echo "🧹 Limpiando cache de pip..."
    pip cache purge
    echo "✅ Cache de pip limpiado"
}

# Función para actualizar pip
update_pip() {
    echo "📦 Actualizando pip..."
    pip install --upgrade pip
    echo "✅ Pip actualizado"
}

# Función para instalar dependencias del sistema
install_system_deps() {
    echo "🔧 Instalando dependencias del sistema..."
    
    # Verificar si estamos en Ubuntu/Debian
    if command -v apt-get &> /dev/null; then
        echo "📦 Instalando dependencias del sistema (Ubuntu/Debian)..."
        sudo apt-get update
        sudo apt-get install -y python3-dev build-essential libpq-dev
        echo "✅ Dependencias del sistema instaladas"
    else
        echo "⚠️  No se detectó apt-get. Instala manualmente:"
        echo "   - python3-dev"
        echo "   - build-essential" 
        echo "   - libpq-dev"
    fi
}

# Función para reinstalar dependencias del backend
reinstall_backend_deps() {
    echo "📦 Reinstalando dependencias del backend..."
    cd backend
    
    # Desinstalar asyncpg si está instalado
    pip uninstall asyncpg -y 2>/dev/null || true
    
    # Instalar dependencias una por una
    echo "🔧 Instalando dependencias básicas..."
    pip install fastapi==0.104.1 uvicorn[standard]==0.24.0 python-dotenv==1.0.0
    
    echo "🔧 Instalando asyncpg..."
    pip install asyncpg==0.29.0
    
    echo "🔧 Instalando dependencias de PDF..."
    pip install pypdf==3.17.4 PyMuPDF==1.23.8 reportlab==4.0.7
    
    echo "🔧 Instalando dependencias de IA..."
    pip install openai==1.84.0
    
    echo "🔧 Instalando dependencias de base de datos..."
    pip install sqlalchemy[asyncio]==1.4.54 databases[postgresql]==0.6.0 psycopg2-binary==2.9.9
    
    echo "🔧 Instalando dependencias de procesamiento..."
    pip install python-multipart==0.0.20 pytesseract==0.3.13 pillow==11.3.0
    
    echo "🔧 Instalando dependencias de testing..."
    pip install pytest==8.4.1 httpx==0.28.1
    
    echo "✅ Dependencias del backend reinstaladas"
    cd ..
}

# Función para verificar instalación
verify_installation() {
    echo "🔍 Verificando instalación..."
    
    python -c "import fastapi; print('✅ FastAPI instalado')" 2>/dev/null || echo "❌ FastAPI no instalado"
    python -c "import uvicorn; print('✅ Uvicorn instalado')" 2>/dev/null || echo "❌ Uvicorn no instalado"
    python -c "import asyncpg; print('✅ AsyncPG instalado')" 2>/dev/null || echo "❌ AsyncPG no instalado"
    python -c "import openai; print('✅ OpenAI instalado')" 2>/dev/null || echo "❌ OpenAI no instalado"
    python -c "import pypdf; print('✅ PyPDF instalado')" 2>/dev/null || echo "❌ PyPDF no instalado"
}

# Función principal
main() {
    echo "🚀 Iniciando solución de dependencias..."
    
    # Activar entorno virtual
    if ! activate_venv; then
        echo "❌ No se pudo activar el entorno virtual"
        exit 1
    fi
    
    # Preguntar si instalar dependencias del sistema
    read -p "¿Instalar dependencias del sistema? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        install_system_deps
    fi
    
    # Limpiar cache y actualizar pip
    clean_pip_cache
    update_pip
    
    # Reinstalar dependencias
    reinstall_backend_deps
    
    # Verificar instalación
    verify_installation
    
    echo ""
    echo "🎉 ¡Proceso completado!"
    echo "💡 Ahora puedes ejecutar: ./start_services.sh"
}

# Ejecutar función principal
main 