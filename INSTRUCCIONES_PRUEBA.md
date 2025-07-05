# Instrucciones para Probar la Aplicación

## Pasos para Debuggear el Problema

### 1. Iniciar la Aplicación
```bash
cd nuevo-frontend
npm run dev
```

### 2. Flujo de Prueba

1. **Abrir el navegador** en `http://localhost:5173`

2. **Completar datos personales**:
   - Llenar nombre y apellidos
   - Llenar email o WhatsApp
   - Hacer clic en "Siguiente"
   - **Verificar**: Debe navegar a `/register/preferences`

3. **Completar preferencias**:
   - Llenar tipo de trabajo (ej: "Desarrollo web")
   - Seleccionar modalidad (ej: "remoto")
   - Seleccionar disponibilidad (ej: "completa")
   - Seleccionar incorporación (ej: "inmediata")
   - Hacer clic en "Finalizar y empezar minijuegos"
   - **Verificar**: Debe navegar a `/games`

4. **En el dashboard de minijuegos**:
   - **Verificar**: Debe mostrar la lista de minijuegos
   - Hacer clic en "Debug Estado" para ver los logs en la consola
   - Hacer clic en el primer minijuego (debería estar disponible)

### 3. Logs a Verificar

En la consola del navegador, buscar estos logs:

#### Al cargar el dashboard de minijuegos:
```
ProtectedRoute - step: games
ProtectedRoute - hasContactData: true/false
ProtectedRoute - hasPreferences: true/false
ProtectedRoute - jobPreferences type: string/object
ProtectedRoute - jobPreferences value: [valor]
```

#### Al hacer clic en "Debug Estado":
```
DEBUG - Estado completo: { personal: {...}, game: {...}, progress: {...} }
```

### 4. Posibles Problemas y Soluciones

#### Problema: Se queda en datos personales
- **Causa**: `hasContactData` es false
- **Solución**: Verificar que firstName y lastName se guarden correctamente

#### Problema: Se queda en preferencias
- **Causa**: `hasPreferences` es false
- **Solución**: Verificar que jobPreferences se guarde correctamente

#### Problema: No puede acceder a minijuegos
- **Causa**: Validación falla en ProtectedRoute
- **Solución**: Revisar logs de ProtectedRoute

#### Problema: Minijuego no inicia
- **Causa**: Problema con la ruta `/game/:id`
- **Solución**: Verificar que la navegación sea a `/game/1` no `/games/1`

### 5. Comandos de Debug

#### Verificar estado de Redux:
```javascript
// En la consola del navegador
console.log('Estado personal:', window.store.getState().personal);
console.log('Estado game:', window.store.getState().game);
```

#### Verificar rutas:
```javascript
// En la consola del navegador
console.log('Ruta actual:', window.location.pathname);
```

### 6. Archivos Clave para Revisar

1. **`personalSlice.ts`** - Lógica de guardado de datos
2. **`ProtectedRoute.tsx`** - Validaciones de navegación
3. **`PreferencesStep.tsx`** - Guardado de preferencias
4. **`GameDashboardPage.tsx`** - Navegación a minijuegos
5. **`App.tsx`** - Configuración de rutas

### 7. Cambios Recientes

- ✅ Agregado campo `completed` al estado personal
- ✅ Modificado `saveContact` para marcar `completed: true`
- ✅ Simplificado validaciones en `ProtectedRoute`
- ✅ Corregido rutas en `App.tsx`
- ✅ Agregado logs de debug

### 8. Próximos Pasos

Si el problema persiste:

1. Revisar logs de la consola
2. Verificar que el estado se guarde correctamente
3. Comprobar que las rutas funcionen
4. Verificar que no haya errores de JavaScript
5. Probar en modo incógnito para evitar cache 