# Azure AI Document Intelligence para EvaluaTE

## 🚀 ¿Qué es Azure AI Document Intelligence?

Azure AI Document Intelligence (anteriormente Form Recognizer) es un servicio de Azure que utiliza inteligencia artificial para extraer texto, información estructurada y datos clave de documentos como CVs, facturas, formularios, etc.

## 🎯 Beneficios para EvaluaTE

### Antes (OCR tradicional):
- ❌ Extracción básica de texto
- ❌ Pérdida de estructura del documento
- ❌ Dificultad para identificar secciones específicas
- ❌ Baja precisión en CVs complejos
- ❌ No reconoce relaciones entre datos

### Después (Document Intelligence):
- ✅ Extracción inteligente de texto e información estructurada
- ✅ Reconocimiento automático de secciones de CV
- ✅ Identificación precisa de habilidades técnicas
- ✅ Extracción de experiencia laboral estructurada
- ✅ Análisis de formación académica
- ✅ Reconocimiento de idiomas y niveles
- ✅ Alta precisión incluso en CVs complejos

## 📋 Configuración

### 1. Crear recurso en Azure

1. Ve a [Azure Portal](https://portal.azure.com)
2. Busca "Document Intelligence" o "Form Recognizer"
3. Haz clic en "Crear"
4. Completa la información:
   - **Suscripción**: Tu suscripción de Azure
   - **Grupo de recursos**: Crea uno nuevo o usa existente
   - **Región**: Elige la más cercana a ti
   - **Nombre del recurso**: Ej: `evaluaTE-document-intelligence`
   - **Plan de precios**: 
     - **Free (F0)**: Para pruebas (500 páginas/mes)
     - **Standard (S0)**: Para producción (10,000 páginas/mes)

### 2. Configurar en EvaluaTE

Ejecuta el script de configuración automática:

```bash
cd backend
python setup_document_intelligence.py
```

O configura manualmente las variables en `.env`:

```env
# Azure AI Document Intelligence Configuration
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://tu-recurso.cognitiveservices.azure.com/
AZURE_DOCUMENT_INTELLIGENCE_KEY=tu_document_intelligence_key_aqui

# Azure Storage Configuration (opcional)
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=tu-cuenta;AccountKey=tu-clave;EndpointSuffix=core.windows.net
AZURE_STORAGE_CONTAINER=cv-uploads
```

### 3. Instalar dependencias

```bash
pip install azure-ai-formrecognizer==3.4.0 azure-storage-blob==12.19.0
```

## 🧪 Pruebas

### Verificar configuración

```bash
python verify_ai_setup.py
```

### Probar funcionalidad

```bash
python test_document_intelligence.py
```

## 🔧 Funcionamiento

### Flujo de análisis

1. **Recepción del CV**: El usuario sube un PDF
2. **Análisis con Document Intelligence**: 
   - Extrae texto completo del documento
   - Identifica secciones automáticamente
   - Extrae información estructurada
3. **Procesamiento de datos**:
   - Información de contacto
   - Experiencia laboral
   - Formación académica
   - Habilidades técnicas
   - Idiomas
   - Proyectos
4. **Análisis de calidad**:
   - Puntuación de estructura
   - Puntuación de completitud
   - Fortalezas y debilidades
5. **Resultado**: Datos estructurados para el informe

### Fallback automático

Si Document Intelligence no está disponible o falla, el sistema automáticamente usa el método tradicional (OCR + análisis de texto).

## 📊 Comparación de resultados

### Ejemplo de CV analizado

**CV de entrada**: PDF con experiencia en desarrollo web, formación en informática, habilidades en JavaScript/React

### Resultados Document Intelligence:
- ✅ **Habilidades técnicas**: JavaScript, React, TypeScript, Node.js, HTML, CSS
- ✅ **Experiencia**: 2 posiciones identificadas correctamente
- ✅ **Formación**: Grado en Informática detectado
- ✅ **Idiomas**: Español (nativo), Inglés (C1), Francés (B2)
- ✅ **Puntuación**: 85/100

### Resultados método tradicional:
- ⚠️ **Habilidades técnicas**: JavaScript, React (parcial)
- ⚠️ **Experiencia**: 1 posición detectada
- ⚠️ **Formación**: Información básica
- ⚠️ **Idiomas**: No detectados
- ⚠️ **Puntuación**: 45/100

## 💰 Costos

### Plan Free (F0)
- **Precio**: Gratis
- **Límite**: 500 páginas/mes
- **Ideal para**: Pruebas y desarrollo

### Plan Standard (S0)
- **Precio**: $1.50 USD por 1,000 páginas
- **Límite**: 10,000 páginas/mes
- **Ideal para**: Producción

### Estimación de costos para EvaluaTE
- **100 CVs/mes**: ~$0.15 USD
- **1,000 CVs/mes**: ~$1.50 USD
- **10,000 CVs/mes**: ~$15.00 USD

## 🔒 Seguridad y privacidad

- Los documentos se procesan temporalmente
- No se almacenan permanentemente en Azure
- Los datos se eliminan automáticamente
- Cumple con GDPR y regulaciones de privacidad

## 🚨 Solución de problemas

### Error: "Document Intelligence no configurado"
```bash
# Verificar variables de entorno
echo $AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT
echo $AZURE_DOCUMENT_INTELLIGENCE_KEY

# Reconfigurar
python setup_document_intelligence.py
```

### Error: "Dependencias no instaladas"
```bash
pip install azure-ai-formrecognizer==3.4.0 azure-storage-blob==12.19.0
```

### Error: "Credenciales inválidas"
1. Verifica el endpoint en Azure Portal
2. Regenera la key en "Keys and Endpoint"
3. Actualiza el archivo `.env`

### Error: "Límite de cuota excedido"
- Verifica el uso en Azure Portal
- Considera actualizar al plan Standard
- Espera al siguiente mes (plan Free)

## 📈 Métricas y monitoreo

### Métricas disponibles
- Páginas procesadas
- Tiempo de respuesta
- Tasa de éxito
- Errores por tipo

### Monitoreo en Azure Portal
1. Ve al recurso Document Intelligence
2. Sección "Métricas"
3. Selecciona métricas deseadas
4. Configura alertas si es necesario

## 🔄 Actualizaciones

### Actualizar dependencias
```bash
pip install --upgrade azure-ai-formrecognizer azure-storage-blob
```

### Actualizar configuración
```bash
python setup_document_intelligence.py
```

## 📞 Soporte

- **Documentación oficial**: [Azure AI Document Intelligence](https://docs.microsoft.com/en-us/azure/ai-services/document-intelligence/)
- **Precios**: [Pricing](https://azure.microsoft.com/en-us/pricing/details/ai-services/)
- **Soporte técnico**: [Azure Support](https://azure.microsoft.com/en-us/support/)

## 🎉 ¡Listo!

Una vez configurado, Document Intelligence mejorará significativamente la precisión del análisis de CVs en EvaluaTE, proporcionando información más estructurada y completa para generar informes de empleabilidad más precisos. 