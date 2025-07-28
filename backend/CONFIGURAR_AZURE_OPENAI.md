# Configuración de Azure OpenAI

## Problema identificado
El error de conexión que aparece en el informe se debe a que **Azure OpenAI no está configurado correctamente** en el backend. Esto causa que:

1. **El análisis de CV falla** porque no puede conectarse a Azure OpenAI para procesar el texto extraído del PDF
2. **El informe se genera** pero con datos limitados porque no puede analizar completamente el CV
3. **El frontend muestra el error** porque detecta que hay un problema de conexión

## Solución

### Paso 1: Configurar Azure OpenAI

1. **Crear recurso en Azure Portal**
   - Ve a https://portal.azure.com
   - Busca "Azure OpenAI" y crea un nuevo recurso
   - Selecciona tu suscripción y grupo de recursos
   - Elige una región (recomendado: East US o West Europe)
   - Dale un nombre al recurso (ej: "evaluador-openai")

2. **Obtener las credenciales**
   - Una vez creado, ve a "Keys and Endpoint"
   - Copia la "Key 1" (será tu `AZURE_OPENAI_API_KEY`)
   - Copia el "Endpoint" (será tu `AZURE_OPENAI_ENDPOINT`)

3. **Crear un deployment**
   - Ve a "Model deployments"
   - Haz clic en "Create"
   - Selecciona un modelo (recomendado: GPT-4o)
   - Dale un nombre al deployment (ej: "gpt-4o-cv-analysis")
   - Anota este nombre (será tu `AZURE_OPENAI_DEPLOYMENT`)

### Paso 2: Configurar el archivo .env

1. **Copiar el archivo de ejemplo**
   ```bash
   cp env.example .env
   ```

2. **Editar el archivo .env**
   ```bash
   nano .env
   ```

3. **Completar con tus valores**
   ```env
   AZURE_OPENAI_API_KEY=tu_api_key_aqui
   AZURE_OPENAI_ENDPOINT=https://tu-recurso.openai.azure.com
   AZURE_OPENAI_DEPLOYMENT=gpt-4o-cv-analysis
   AZURE_OPENAI_API_VERSION=2024-02-15-preview
   ```

### Paso 3: Reiniciar el servidor

```bash
# Detener el servidor actual (Ctrl+C)
# Luego reiniciar
python main.py
```

### Paso 4: Verificar la configuración

Puedes usar el script de prueba incluido:

```bash
python test_azure_openai.py
```

## Resultado esperado

Después de configurar Azure OpenAI correctamente:

1. **El análisis de CV funcionará completamente** - podrá extraer y analizar el contenido del PDF
2. **El informe se generará sin errores** - incluirá análisis detallado del CV
3. **No aparecerán mensajes de error** - la aplicación funcionará de manera fluida

## Notas importantes

- **Costo**: Azure OpenAI tiene un costo por uso. Configura límites de gasto en tu cuenta de Azure
- **Regiones**: Asegúrate de que el deployment esté en la misma región que tu recurso
- **Modelos**: GPT-4o es recomendado para análisis de CV, pero puedes usar otros modelos disponibles

## Solución temporal

Si no quieres configurar Azure OpenAI ahora, la aplicación seguirá funcionando con análisis básico del CV. El informe se generará pero con información limitada sobre el CV. 