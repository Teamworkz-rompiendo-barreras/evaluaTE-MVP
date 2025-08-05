# Análisis de Dependencias No Utilizadas - EvaluaTE MVP

## Resumen Ejecutivo

Se ha realizado una revisión exhaustiva de todas las extensiones y recursos en la aplicación EvaluaTE MVP para identificar aquellas que no se están utilizando. Se encontraron varias dependencias que pueden ser eliminadas para optimizar el proyecto.

## Dependencias del Backend (requirements.txt)

### ✅ Dependencias EN USO:
- `fastapi==0.104.1` - Framework principal del backend
- `uvicorn[standard]==0.24.0` - Servidor ASGI
- `python-dotenv==1.0.0` - Variables de entorno
- `pypdf==3.17.4` - Procesamiento de PDFs
- `openai==1.84.0` - Integración con Azure OpenAI
- `python-multipart==0.0.20` - Manejo de archivos multipart
- `pytesseract==0.3.13` - OCR para PDFs escaneados
- `pillow==11.3.0` - Procesamiento de imágenes para OCR
- `PyMuPDF==1.23.8` - Extracción de texto de PDFs
- `reportlab==4.0.7` - Generación de PDFs de informes

### ❌ Dependencias NO UTILIZADAS:

#### 1. **Base de Datos (NO SE USA)**
- `sqlalchemy[asyncio]==1.4.54`
- `databases[postgresql]==0.6.0`
- `asyncpg==0.29.0`
- `psycopg2-binary==2.9.9`

**Justificación**: Aunque existe el archivo `db.py` con configuración de base de datos, no se encontró ningún uso de estas dependencias en el código principal. La aplicación no está guardando datos en base de datos.

#### 2. **Testing (NO SE USA)**
- `pytest==8.4.1`
- `httpx==0.28.1`

**Justificación**: No se encontraron archivos de testing en el backend que utilicen estas dependencias.

#### 3. **Azure Services (OPCIONAL)**
- `azure-ai-formrecognizer==3.3.3`
- `azure-storage-blob==12.19.0`

**Justificación**: Estas dependencias son opcionales y solo se usan si están configuradas las variables de entorno correspondientes. El código maneja su ausencia gracefully.

## Dependencias del Frontend (package.json)

### ✅ Dependencias EN USO:
- `react`, `react-dom` - Framework principal
- `react-router-dom` - Enrutamiento
- `@reduxjs/toolkit`, `react-redux`, `redux-persist` - Estado global
- `react-hook-form` - Formularios
- `react-hot-toast` - Notificaciones
- `react-markdown` - Renderizado de markdown
- `recharts` - Gráficos
- `@sentry/react`, `@sentry/tracing` - Monitoreo de errores
- `@nivo/radar` - Gráfico de radar
- `@apollo/client` - Cliente GraphQL (usado en queries.ts)

### ❌ Dependencias NO UTILIZADAS:

#### 1. **Testing (LIMITADO USO)**
- `cypress` y dependencias relacionadas
- `vitest` y dependencias relacionadas
- `msw` (Mock Service Worker)

**Justificación**: Aunque existen archivos de configuración y algunos tests, el uso es muy limitado y no crítico para la funcionalidad principal.

#### 2. **Dependencias de Desarrollo (OPCIONAL)**
- `@testing-library/*` - Testing utilities
- `@types/*` - TypeScript types (algunos pueden no ser necesarios)
- `eslint` y plugins - Linting
- `autoprefixer`, `postcss`, `tailwindcss` - CSS processing

**Justificación**: Estas son dependencias de desarrollo que pueden mantenerse para el desarrollo pero no son críticas para producción.

## Recomendaciones

### 1. Eliminación Inmediata (Backend)
```bash
# Eliminar dependencias de base de datos no utilizadas
pip uninstall sqlalchemy databases asyncpg psycopg2-binary

# Eliminar dependencias de testing no utilizadas
pip uninstall pytest httpx
```

### 2. Eliminación Opcional (Frontend)
```bash
# Eliminar dependencias de testing si no se planea usar
npm uninstall cypress cypress-file-upload @testing-library/jest-dom @testing-library/react @testing-library/user-event vitest @vitest/coverage-v8 msw start-server-and-test eslint-plugin-cypress
```

### 3. Mantener (Opcionales pero Útiles)
- Dependencias de Azure (opcionales)
- Dependencias de desarrollo (eslint, typescript, etc.)
- Dependencias de testing si se planea implementar testing en el futuro

## Impacto de la Eliminación

### Beneficios:
1. **Reducción del tamaño del proyecto**: Menos dependencias = menor tamaño
2. **Mejor mantenimiento**: Menos dependencias que mantener actualizadas
3. **Menor superficie de vulnerabilidades**: Menos dependencias = menos posibles vulnerabilidades
4. **Instalación más rápida**: Menos paquetes que descargar e instalar

### Riesgos:
1. **Funcionalidad futura**: Si se planea usar base de datos o testing, habría que reinstalar
2. **Desarrollo**: Algunas herramientas de desarrollo se perderían

## Conclusión

La aplicación EvaluaTE MVP tiene varias dependencias no utilizadas que pueden ser eliminadas de forma segura. Se recomienda eliminar las dependencias de base de datos y testing del backend, ya que no se están utilizando en absoluto. Las dependencias del frontend pueden mantenerse si se planea continuar con el desarrollo y testing. 