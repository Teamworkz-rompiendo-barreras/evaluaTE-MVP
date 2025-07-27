# EvaluaTE MVP Backend - Guía de Desarrollo

## 🚀 Inicio Rápido

### 1. Activar el entorno virtual
```bash
# Opción 1: Script automático
source activate_venv.sh

# Opción 2: Manual
source venv/bin/activate
```

### 2. Verificar dependencias
```bash
python start_app.py
```

### 3. Ejecutar la aplicación
```bash
# Opción 1: Con uvicorn (recomendado para desarrollo)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Opción 2: Directamente
python main.py
```

## 🔧 Configuración del Entorno de Desarrollo

### VS Code
El proyecto incluye configuración automática para VS Code:
- **Interprete de Python**: Se configura automáticamente para usar `./venv/bin/python`
- **Linting**: Pyright configurado para detectar el entorno virtual
- **Auto-completado**: Habilitado para todas las dependencias

### Pyright (Linter)
La configuración está en `pyrightconfig.json`:
- Detecta automáticamente el entorno virtual
- Incluye todas las dependencias instaladas
- Configurado para ignorar archivos innecesarios

## 📦 Dependencias

### Principales
- `fastapi==0.104.1` - Framework web
- `uvicorn[standard]==0.24.0` - Servidor ASGI
- `openai==1.84.0` - Cliente de OpenAI/Azure
- `pypdf==3.17.4` - Procesamiento de PDFs
- `pydantic` - Validación de datos
- `python-dotenv==1.0.0` - Variables de entorno

### Instalación
```bash
pip install -r requirements.txt
```

## 🐛 Solución de Problemas

### Error: "Import could not be resolved"
**Causa**: El entorno virtual no está activado o el linter no lo detecta.

**Solución**:
1. Activar el entorno virtual: `source venv/bin/activate`
2. Reiniciar VS Code
3. Verificar que el interprete de Python sea `./venv/bin/python`

### Error: "Module not found"
**Causa**: Dependencias no instaladas.

**Solución**:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Error: Variables de entorno no encontradas
**Causa**: Archivo `.env` faltante o mal configurado.

**Solución**:
1. Copiar `env.example` a `.env`
2. Configurar las variables de Azure OpenAI:
   - `AZURE_OPENAI_API_KEY`
   - `AZURE_OPENAI_ENDPOINT`
   - `AZURE_OPENAI_DEPLOYMENT`
   - `AZURE_OPENAI_API_VERSION`

## 📁 Estructura del Proyecto

```
backend/
├── main.py                 # Aplicación principal FastAPI
├── generate_report.py      # Generación de informes con IA
├── cv_analyzer.py          # Análisis de CVs
├── pdf_service.py          # Servicios de PDF
├── requirements.txt        # Dependencias
├── pyrightconfig.json      # Configuración del linter
├── .vscode/settings.json   # Configuración de VS Code
├── activate_venv.sh        # Script de activación
├── start_app.py           # Script de verificación
└── venv/                  # Entorno virtual
```

## 🔍 Verificación de Funcionamiento

### Test de Importaciones
```bash
python -c "from main import app; from generate_report import generar_informe; print('✅ Todo OK')"
```

### Test de Endpoints
```bash
# Iniciar la aplicación
uvicorn main:app --reload

# En otro terminal, probar endpoints
curl http://localhost:8000/
```

## 📝 Notas Importantes

1. **Siempre activar el entorno virtual** antes de trabajar
2. **No modificar** `pyrightconfig.json` sin necesidad
3. **Verificar dependencias** con `python start_app.py`
4. **Usar el script de activación** para desarrollo: `source activate_venv.sh`

## 🆘 Soporte

Si encuentras problemas:
1. Ejecuta `python start_app.py` para diagnóstico
2. Verifica que el entorno virtual esté activado
3. Revisa que todas las dependencias estén instaladas
4. Consulta los logs de la aplicación 