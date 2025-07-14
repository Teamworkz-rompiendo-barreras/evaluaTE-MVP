# Configuración de Sentry para EvaluaTE

## ¿Qué es Sentry?

Sentry es una plataforma de monitoreo de errores que te permite:
- Capturar errores en tiempo real
- Ver stack traces detallados
- Monitorear el rendimiento de la aplicación
- Recibir notificaciones cuando algo falla

## Configuración Inicial

### 1. Crear cuenta en Sentry

1. Ve a [sentry.io](https://sentry.io)
2. Crea una cuenta gratuita
3. Crea un nuevo proyecto para "React"
4. Copia el DSN (Data Source Name)

### 2. Configurar variables de entorno

Crea un archivo `.env.local` en la raíz del proyecto:

```env
VITE_SENTRY_DSN=https://tu-dsn-de-sentry@sentry.io/project-id
VITE_APP_VERSION=1.0.0
```

### 3. Configurar Sentry

El archivo `src/sentry.ts` ya está configurado con:
- Inicialización automática
- Filtrado de errores
- Configuración de performance
- Funciones helper

## Uso en Componentes

### Hook useSentry

```tsx
import { useSentry } from '../hooks/useSentry';

function MiComponente() {
  const { captureError, captureMessage, setUser, addContext } = useSentry();

  const handleError = () => {
    try {
      // código que puede fallar
    } catch (error) {
      captureError(error, { 
        component: 'MiComponente',
        action: 'handleError' 
      });
    }
  };

  const handleUserAction = () => {
    captureMessage('Usuario completó acción importante', 'info');
    addContext('userAction', { timestamp: Date.now() });
  };

  return (
    // tu componente
  );
}
```

### Error Boundary

El `ErrorBoundary` ya está configurado en `main.tsx` y capturará automáticamente errores de React.

### Componentes con Sentry

```tsx
import { withSentry } from '../components/ErrorBoundary';

const MiComponenteConSentry = withSentry(MiComponente);
```

## Funciones Disponibles

### reportError(error, context?)
Reporta un error a Sentry con contexto adicional.

### reportMessage(message, level)
Reporta un mensaje informativo, warning o error.

### setUserContext(user)
Establece información del usuario para el contexto.

### clearUserContext()
Limpia la información del usuario.

## Dashboard de Sentry

Una vez configurado, podrás ver en el dashboard de Sentry:

1. **Issues**: Errores agrupados por tipo
2. **Performance**: Métricas de rendimiento
3. **Releases**: Versiones de la aplicación
4. **Users**: Información de usuarios afectados

## Configuración Avanzada

### Filtrado de Errores

En `src/sentry.ts`, puedes modificar la función `beforeSend` para filtrar errores específicos:

```ts
beforeSend(event) {
  // No reportar errores de red
  if (event.exception?.values?.[0]?.type === 'NetworkError') {
    return null;
  }
  return event;
}
```

### Muestreo de Transacciones

```ts
tracesSampleRate: 0.2, // Solo 20% de las transacciones
```

### Entornos

```ts
environment: import.meta.env.MODE, // development, production
```

## Monitoreo de Performance

Sentry también monitorea automáticamente:
- Tiempo de carga de páginas
- Navegación entre rutas
- Rendimiento de componentes

## Alertas

Puedes configurar alertas en Sentry para:
- Errores críticos
- Degradación de performance
- Nuevos tipos de errores

## Integración con CI/CD

Para releases automáticos, agrega a tu pipeline:

```bash
# Instalar Sentry CLI
npm install -g @sentry/cli

# Crear release
sentry-cli releases new $VERSION

# Subir source maps
sentry-cli releases files $VERSION upload-sourcemaps ./dist

# Finalizar release
sentry-cli releases finalize $VERSION
```

## Troubleshooting

### Sentry no se inicializa
- Verifica que `VITE_SENTRY_DSN` esté configurado
- Revisa la consola del navegador

### Errores no aparecen
- Verifica que estés en modo producción
- Revisa la configuración de filtros

### Performance no se monitorea
- Verifica que `BrowserTracing` esté configurado
- Revisa la configuración de `tracesSampleRate` 