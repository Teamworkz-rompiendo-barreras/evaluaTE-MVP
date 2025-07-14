# Logs de Debug Agregados

## Logs Implementados

### 1. GameScenePage
- **ID del minijuego**: `GameScenePage - id del minijuego: [id]`
- **Ruta actual**: `GameScenePage - ruta actual: [pathname]`

### 2. useGameController
- **Inicio de juego**: `useGameController - startGame llamado con gameId: [id]`
- **Juego encontrado**: `useGameController - juego encontrado: [game]`
- **Juego iniciado**: `useGameController - juego iniciado correctamente`
- **Error**: `useGameController - ERROR: juego no encontrado`

### 3. GameCard
- **Clic en juego**: `GameCard - Clic en juego: [id] [title]`

### 4. GameDashboardPage
- **Navegación**: `GameDashboardPage - handleGameClick llamado con gameId: [id]`
- **Ruta de navegación**: `GameDashboardPage - navegando a: /game/[id]`
- **Disponibilidad**: `GameDashboardPage - isGameAvailable para gameId: [id] gameIndex: [index]`
- **Primer juego**: `GameDashboardPage - Primer juego, siempre disponible`
- **Juego anterior**: `GameDashboardPage - Juego anterior: [id] completado: [boolean] disponible: [boolean]`
- **Renderizado**: `GameDashboardPage - Renderizando juego: [id] index: [index] isCompleted: [boolean] isAvailable: [boolean] isCurrent: [boolean]`

### 5. ProtectedRoute (ya existentes)
- **Step**: `ProtectedRoute - step: [step]`
- **Datos de contacto**: `ProtectedRoute - hasContactData: [boolean]`
- **Preferencias**: `ProtectedRoute - hasPreferences: [boolean]`
- **Tipo de preferencias**: `ProtectedRoute - jobPreferences type: [string/object]`
- **Valor de preferencias**: `ProtectedRoute - jobPreferences value: [value]`

## Cómo Usar los Logs

### 1. Abrir la Consola del Navegador
- Presionar `F12` o `Ctrl+Shift+I`
- Ir a la pestaña "Console"

### 2. Seguir el Flujo
1. **Completar datos personales** → Ver logs de ProtectedRoute
2. **Completar preferencias** → Ver logs de ProtectedRoute y PreferencesStep
3. **Ir al dashboard** → Ver logs de GameDashboardPage
4. **Hacer clic en minijuego** → Ver logs de GameCard y GameDashboardPage
5. **Cargar minijuego** → Ver logs de GameScenePage y useGameController

### 3. Buscar Problemas Específicos

#### Si no aparece el dashboard:
- Buscar logs de `ProtectedRoute - step: games`
- Verificar `hasContactData` y `hasPreferences`

#### Si no se puede hacer clic en minijuegos:
- Buscar logs de `GameDashboardPage - Renderizando juego`
- Verificar `isAvailable: true`

#### Si el minijuego no carga:
- Buscar logs de `GameCard - Clic en juego`
- Buscar logs de `GameDashboardPage - handleGameClick`
- Buscar logs de `GameScenePage - id del minijuego`
- Buscar logs de `useGameController - startGame`

#### Si hay error al cargar:
- Buscar `useGameController - ERROR: juego no encontrado`

## Información Esperada

### Para el Primer Minijuego:
- **ID**: `decision-making`
- **Título**: "Primera llamada del día"
- **Disponibilidad**: Siempre disponible (index 0)
- **Ruta**: `/game/decision-making`

### Estados Correctos:
- `hasContactData: true`
- `hasPreferences: true`
- `isAvailable: true` (para el primer juego)
- `isCurrent: true` (para el primer juego)

## Comandos de Debug Adicionales

### Ver Estado Completo en Consola:
```javascript
// En la consola del navegador
console.log('Estado personal:', window.store.getState().personal);
console.log('Estado game:', window.store.getState().game);
console.log('Juegos disponibles:', window.store.getState().game.completedGames);
```

### Ver Juegos Cargados:
```javascript
// En la consola del navegador
import { games } from './src/data/games';
console.log('Juegos cargados:', games.map(g => ({ id: g.id, title: g.title })));
``` 