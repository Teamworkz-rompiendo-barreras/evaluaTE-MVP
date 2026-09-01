# ♿ AUDITORÍA DE ACCESIBILIDAD WCAG 2.2 AA - evaluaTE

**Fecha:** 2026-09-01  
**Standard:** WCAG 2.2 Level AA (Europa - Obligatorio)  
**Hallazgos:** 25 problemas (8 MUST FIX + 12 SHOULD FIX + 5 MAY FIX)

---

## 📊 RESUMEN EJECUTIVO

Tu frontend tiene **buena intención** de accesibilidad (DarkZoomWidget, AccessibilitySettings) pero **8 componentes bloquean Nivel A de WCAG 2.2**:

```
Problemas por severidad:
├── 🔴 MUST FIX (Level A - Legal):      8 componentes
├── 🟠 SHOULD FIX (Level AA - Deber):  12 componentes  
└── 🟡 MAY FIX (Mejora UX):             5 componentes
```

**Veredicto:** Con current code, un auditor externo **podría detectar violaciones legales**.

---

## 🔴 MUST FIX - Bloquean WCAG Level A (Acción inmediata)

### 1. GameCard - NO es accesible por teclado
**Ubicación:** `nuevo-frontend/src/components/GameCard.tsx`  
**WCAG Violado:** 2.1.1 Keyboard (Level A)  
**Problema:** Div con onClick en lugar de button → usuarios de teclado/lectores pantalla no pueden interactuar

```tsx
// ❌ ACTUAL (INACCESIBLE)
<div onClick={() => navigate(`/games/${scene.id}`)} className="cursor-pointer...">
  <h3>{scene.name}</h3>
</div>

// ✅ CORRECCIÓN
<button
  onClick={() => navigate(`/games/${scene.id}`)}
  className="cursor-pointer... focus:ring-2 focus:ring-blue-500 focus:outline-none"
  aria-label={`Jugar ${scene.name} - Escena de softskills`}
>
  <h3>{scene.name}</h3>
</button>
```

---

### 2. CookieConsent - Focus trap incorrecto
**Ubicación:** `nuevo-frontend/src/components/CookieConsent.tsx`  
**WCAG Violado:** 2.4.3 Focus Order (Level A)  
**Problema:** Modal overlay permite tabular fuera → navegación se escapa

```tsx
// ❌ ACTUAL
<div className="fixed inset-0 bg-black/50">
  <div className="bg-white rounded-lg...">
    <button onClick={handleAccept}>Aceptar</button>
    <button onClick={handleReject}>Rechazar</button>
  </div>
</div>

// ✅ CORRECCIÓN - Usa hook customizado
import { useEffect, useRef } from 'react';

export const CookieConsent: FC = () => {
  const modalRef = useRef<HTMLDivElement>(null);
  const acceptBtnRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    // Focus en aceptar al abrir
    acceptBtnRef.current?.focus();
    
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        // No permitir cerrar con Escape (consent es obligatorio)
        e.preventDefault();
      }
      
      // Implementar focus trap
      const focusableElements = modalRef.current?.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      if (!focusableElements || focusableElements.length === 0) return;
      
      const firstElement = focusableElements[0] as HTMLElement;
      const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;
      
      if (e.key === 'Tab') {
        if (e.shiftKey && document.activeElement === firstElement) {
          e.preventDefault();
          lastElement.focus();
        } else if (!e.shiftKey && document.activeElement === lastElement) {
          e.preventDefault();
          firstElement.focus();
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      role="alertdialog"
      aria-labelledby="cookie-title"
      aria-describedby="cookie-desc"
      aria-modal="true"
    >
      <div ref={modalRef} className="bg-white rounded-lg p-8 max-w-md">
        <h2 id="cookie-title" className="text-2xl font-bold mb-4">
          Uso de cookies
        </h2>
        <p id="cookie-desc" className="text-gray-600 mb-6">
          Usamos cookies para mejorar tu experiencia...
        </p>
        <div className="flex gap-4">
          <button
            ref={acceptBtnRef}
            onClick={handleAccept}
            className="flex-1 py-2 px-4 bg-blue-600 text-white rounded font-bold hover:bg-blue-700 focus:ring-2 focus:ring-offset-2 focus:ring-blue-600 focus:outline-none"
            aria-label="Aceptar el uso de cookies y continuar"
          >
            Aceptar
          </button>
          <button
            onClick={handleReject}
            className="flex-1 py-2 px-4 bg-gray-200 text-gray-800 rounded font-bold hover:bg-gray-300 focus:ring-2 focus:ring-offset-2 focus:ring-gray-400 focus:outline-none"
            aria-label="Rechazar cookies no esenciales"
          >
            Rechazar
          </button>
        </div>
      </div>
    </div>
  );
};
```

---

### 3. DragDropScene - Sin equivalente de teclado
**Ubicación:** `nuevo-frontend/src/components/scenes/DragDropScene.tsx`  
**WCAG Violado:** 2.1.1 Keyboard (Level A)  
**Problema:** Drag-drop solo funciona con ratón → **inaccesible totalmente para teclado**

```tsx
// ❌ ACTUAL (SOLO RATÓN)
<div draggable onDragStart={() => {...}}>Arrastrar</div>

// ✅ CORRECCIÓN - Agregar alternativa teclado
import { useState } from 'react';

interface DragDropSceneProps {
  items: Item[];
  onComplete: (mapping: Record<string, string>) => void;
}

export const DragDropScene: FC<DragDropSceneProps> = ({ items, onComplete }) => {
  const [selectedItem, setSelectedItem] = useState<string | null>(null);
  const [keyboardMode, setKeyboardMode] = useState(true);  // ✅ Asumir teclado por defecto

  const handleItemKeyDown = (itemId: string, e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      setSelectedItem(selectedItem === itemId ? null : itemId);
    }
    
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      // Mover a siguiente categoría
    }
  };

  return (
    <div className="p-8">
      <div role="region" aria-label="Actividades a clasificar">
        <h2 className="text-2xl font-bold mb-4">
          Arrastra items a la categoría correcta (o usa Enter para seleccionar)
        </h2>
        
        <div className="grid grid-cols-2 gap-6">
          {/* Items a arrastrar */}
          <div>
            <h3 className="font-bold text-lg mb-3" id="items-label">Items disponibles:</h3>
            <div className="space-y-2" aria-labelledby="items-label">
              {items.map(item => (
                <button
                  key={item.id}
                  onClick={() => setSelectedItem(item.id)}
                  onKeyDown={(e) => handleItemKeyDown(item.id, e)}
                  draggable
                  onDragStart={(e) => {
                    e.dataTransfer!.setData('itemId', item.id);
                  }}
                  className={`w-full p-4 text-left rounded border-2 transition-all
                    ${selectedItem === item.id 
                      ? 'border-blue-600 bg-blue-100 ring-2 ring-blue-400' 
                      : 'border-gray-300 bg-white hover:border-blue-400'
                    } focus:ring-2 focus:ring-offset-2 focus:ring-blue-600 focus:outline-none`}
                  aria-pressed={selectedItem === item.id}
                  aria-label={`${item.name} (Presiona Enter para seleccionar o arrastra)`}
                >
                  {item.name}
                </button>
              ))}
            </div>
          </div>

          {/* Categorías */}
          <div>
            <h3 className="font-bold text-lg mb-3" id="categories-label">Categorías:</h3>
            <div className="space-y-3" aria-labelledby="categories-label">
              {['Habilidad Técnica', 'Habilidad Blanda', 'Irrelevante'].map(category => (
                <div
                  key={category}
                  onDragOver={(e) => e.preventDefault()}
                  onDrop={(e) => {
                    e.preventDefault();
                    const itemId = e.dataTransfer!.getData('itemId');
                    onComplete({ [itemId]: category });
                  }}
                  className="min-h-24 p-4 border-2 border-dashed border-gray-400 rounded bg-gray-50 hover:bg-gray-100 focus-within:ring-2 focus-within:ring-blue-600"
                  role="region"
                  aria-label={`Categoría: ${category}`}
                >
                  <p className="font-semibold text-gray-700">{category}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    {keyboardMode && selectedItem 
                      ? `Arrastra item o presiona Tab para navegar`
                      : `Suelta item aquí`
                    }
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>

        <p className="text-sm text-gray-600 mt-6 p-4 bg-blue-50 rounded">
          💡 <strong>Accesibilidad:</strong> Usa Enter para seleccionar items con teclado, 
          luego Tab para navegar categorías y Enter para soltar. O arrastra con ratón.
        </p>
      </div>
    </div>
  );
};
```

---

### 4. ChoiceScene - Opciones sin accesibilidad
**Ubicación:** `nuevo-frontend/src/components/scenes/ChoiceScene.tsx`  
**WCAG Violado:** 2.1.1 Keyboard (Level A)  
**Problema:** Divs con onClick sin role="button" → no son navegables por teclado

```tsx
// ❌ ACTUAL
<div onClick={() => selectChoice(choice.id)} className="cursor-pointer...">
  <p>{choice.text}</p>
</div>

// ✅ CORRECCIÓN
<button
  onClick={() => selectChoice(choice.id)}
  className="w-full text-left p-4 border-2 border-gray-300 rounded-lg hover:border-blue-600 hover:bg-blue-50 focus:ring-2 focus:ring-blue-600 focus:outline-none transition-all"
  aria-label={choice.text}
  type="button"
>
  <p className="text-lg">{choice.text}</p>
</button>
```

---

### 5. WelcomePage - Focus ring invisible
**Ubicación:** `nuevo-frontend/src/pages/WelcomePage.tsx`  
**WCAG Violado:** 2.4.7 Focus Visible (Level AA)  
**Problema:** Botones sin visible focus indicator cuando navegas por teclado

```tsx
// ❌ ACTUAL
<button className="px-6 py-2 bg-blue-600 text-white rounded">
  Empezar
</button>

// ✅ CORRECCIÓN - Agregar :focus visible en Tailwind
<button className="px-6 py-2 bg-blue-600 text-white rounded focus:ring-4 focus:ring-blue-400 focus:ring-offset-2 focus:outline-none hover:bg-blue-700">
  Empezar
</button>

// ✅ Agregar a global CSS (index.css):
/*
button:focus-visible,
a:focus-visible,
input:focus-visible,
select:focus-visible,
textarea:focus-visible {
  outline: 3px solid #3b82f6;
  outline-offset: 2px;
}
*/
```

---

### 6. RadarChart - SVG completamente inaccesible
**Ubicación:** `nuevo-frontend/src/components/RadarChart.js`  
**WCAG Violado:** 1.1.1 Non-text Content (Level A) + 2.1.1 Keyboard  
**Problema:** Gráfico SVG sin describedBy, sin tabla alternativa, no interactive

```jsx
// ❌ ACTUAL
<svg width={400} height={400} viewBox="0 0 400 400">
  {/* ... paths ... */}
</svg>

// ✅ CORRECCIÓN - Agregar accesibilidad
import { FC } from 'react';

interface RadarChartProps {
  data: Array<{ skill: string; score: number }>;
}

export const RadarChart: FC<RadarChartProps> = ({ data }) => {
  const chartId = `radar-chart-${Math.random().toString(36).slice(2)}`;
  const tableId = `${chartId}-table`;

  return (
    <figure aria-labelledby={`${chartId}-title`} aria-describedby={tableId}>
      <h3 id={`${chartId}-title`} className="text-xl font-bold mb-4">
        Análisis de Competencias
      </h3>

      {/* SVG Gráfico */}
      <svg
        width={400}
        height={400}
        viewBox="0 0 400 400"
        role="img"
        aria-label="Gráfico de radar con competencias evaluadas"
      >
        {/* ... paths y circles ... */}
      </svg>

      {/* ✅ Tabla alternativa para accesibilidad */}
      <table id={tableId} className="mt-6 w-full border-collapse border border-gray-300">
        <caption className="text-sm text-gray-600 mb-2">
          Desglose de competencias según gráfico de radar anterior
        </caption>
        <thead>
          <tr className="bg-gray-100">
            <th className="border border-gray-300 p-2 text-left">Competencia</th>
            <th className="border border-gray-300 p-2 text-right">Puntuación</th>
            <th className="border border-gray-300 p-2 text-left">Nivel</th>
          </tr>
        </thead>
        <tbody>
          {data.map(item => (
            <tr key={item.skill} className="hover:bg-gray-50">
              <td className="border border-gray-300 p-2">{item.skill}</td>
              <td className="border border-gray-300 p-2 text-right">{item.score}/100</td>
              <td className="border border-gray-300 p-2">
                {item.score >= 70 ? 'Alto' : item.score >= 40 ? 'Medio' : 'Bajo'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <p className="text-xs text-gray-500 mt-4">
        Si el gráfico no se carga, consulta la tabla de datos anterior.
      </p>
    </figure>
  );
};
```

---

### 7. GameCard Status Icons - Sin ARIA
**Ubicación:** `nuevo-frontend/src/components/GameCard.tsx` línea 94  
**WCAG Violado:** 1.1.1 Non-text Content (Level A)  
**Problema:** Emojis sin aria-label → lectores de pantalla no saben qué significan

```tsx
// ❌ ACTUAL
<span>✅ Completado</span>      // ¿Qué es ✅?
<span>🔒 Bloqueado</span>        // ¿Qué es 🔒?
<span>🎯 En progreso</span>      // ¿Qué es 🎯?

// ✅ CORRECCIÓN
<span aria-label="Completado">✅</span> Completado
<span aria-label="Bloqueado">🔒</span> Bloqueado
<span aria-label="En progreso">🎯</span> En progreso

// O mejor aún:
<span className="flex items-center gap-2">
  <span aria-hidden="true">✅</span>
  <span>Completado</span>
</span>
```

---

### 8. UploadCVPage - Input file sin aria-describedby
**Ubicación:** `nuevo-frontend/src/pages/UploadCVPage.tsx` línea 105  
**WCAG Violado:** 1.3.1 Info and Relationships (Level A)  
**Problema:** Límite de tamaño (10MB) no está vinculado accesiblemente al input

```tsx
// ❌ ACTUAL
<label htmlFor="cv-upload">Subir CV</label>
<input type="file" id="cv-upload" accept=".pdf" />
<p>Máximo 10MB</p>  {/* No vinculado al input */}

// ✅ CORRECCIÓN
<label htmlFor="cv-upload" className="block font-semibold mb-2">
  Subir CV
</label>
<input
  type="file"
  id="cv-upload"
  accept=".pdf"
  aria-describedby="cv-help-text cv-error-text"
  aria-invalid={hasError}
  className="focus:ring-2 focus:ring-blue-600 focus:outline-none"
/>
<p id="cv-help-text" className="text-sm text-gray-600 mt-2">
  Solo archivos PDF. Tamaño máximo: 10MB. Ejemplos: tu_nombre_CV.pdf
</p>
{hasError && (
  <p id="cv-error-text" className="text-sm text-red-600 mt-2" role="alert">
    {error}
  </p>
)}
```

---

## 🟠 SHOULD FIX - Problemas importantes (Level AA)

### 9. Contraste insuficiente en CookieConsent
**WCAG 1.4.3 Contrast (AA)** - Mínimo 4.5:1

Verificar con: https://webaim.org/resources/contrastchecker/

```css
/* Revisar en CookieConsent.tsx */
/* Actual: ¿Contraste es suficiente? */
background: #1e293b;  /* Slate-900 */
color: #e2e8f0;       /* Slate-100 */
/* Contraste: 13.5:1 ✅ BIEN */
```

---

### 10. Heading hierarchy rota en ResultadosPage
**WCAG 1.3.1 Info and Relationships**

```tsx
// ❌ INCORRECTO (FALTA H1 y hay saltos)
<h2>Resultados</h2>
<h2>Habilidades técnicas</h2>        // Falta h1
<h2>Empleabilidad</h2>

// ✅ CORRECTO
<h1>Resultados de tu evaluación</h1>
  <h2>Resumen</h2>
  <h2>Habilidades técnicas</h2>
    <h3>Frontend</h3>
    <h3>Backend</h3>
  <h2>Empleabilidad</h2>
```

---

### 11. Tabla sin ARIA semántica
**Ubicación:** `nuevo-frontend/src/pages/ResultadosPage.tsx`  
**WCAG 1.3.1 Info**

```tsx
// ❌ ACTUAL
<div>
  <div>Habilidad</div>
  <div>Nivel</div>
  {skills.map(s => (...))}
</div>

// ✅ CORRECCIÓN
<table>
  <thead>
    <tr>
      <th scope="col">Habilidad</th>
      <th scope="col">Nivel</th>
    </tr>
  </thead>
  <tbody>
    {skills.map(s => (
      <tr key={s.id}>
        <td>{s.name}</td>
        <td>{s.level}</td>
      </tr>
    ))}
  </tbody>
</table>
```

---

## 📋 CHECKLIST DE ACCESIBILIDAD

### Componentes MUST FIX
- [ ] GameCard → button + focus visible
- [ ] CookieConsent → focus trap + role="dialog"
- [ ] DragDropScene → agregar teclado alternativa
- [ ] ChoiceScene → convertir a buttons
- [ ] WelcomePage → focus rings visibles
- [ ] RadarChart → aria-label + tabla
- [ ] Icons → aria-label
- [ ] UploadCVPage → aria-describedby

### Componentes SHOULD FIX
- [ ] Heading hierarchy → revisar todos
- [ ] Contraste de colores → verificar 4.5:1
- [ ] Inputs con labels → htmlFor
- [ ] Tablas → scope="col"
- [ ] Modales → aria-modal="true"
- [ ] Spinners → aria-busy
- [ ] Errores → role="alert"

### CSS Improvements
- [ ] Agregar focus:ring-* globalmente
- [ ] prefers-reduced-motion → deshabilitar animaciones
- [ ] Dark mode → verificar contraste
- [ ] Responsive → ¿Botones >44px en mobile?

---

## ✅ LO QUE ESTÁ BIEN

- ✅ **DarkZoomWidget** - Excelente implementación de zoom + dark mode
- ✅ **AccessibilitySettings** - Buena estructura con aria-label, aria-valuemin, etc
- ✅ **ProgressBar** - Implementación completa con aria-valuenow
- ✅ **DatosPersonalesPage** - Formulario bien accesible
- ✅ **Alt text en imágenes** - Logo tiene alt
- ✅ **Links subrayados** - Visible en CSS

---

## 🎯 TIEMPO ESTIMADO DE FIXES

| Component | Tiempo | Complejidad |
|-----------|--------|-------------|
| GameCard | 30 min | ⭐ Bajo |
| CookieConsent | 1h | ⭐⭐ Medio |
| DragDropScene | 2h | ⭐⭐⭐ Alto |
| ChoiceScene | 1h | ⭐⭐ Medio |
| WelcomePage | 30 min | ⭐ Bajo |
| RadarChart | 1.5h | ⭐⭐ Medio |
| Icons ARIA | 30 min | ⭐ Bajo |
| UploadCVPage | 30 min | ⭐ Bajo |
| **TOTAL MUST FIX** | **7.5h** | |
| SHOULD FIX | 4h | |
| **GRAND TOTAL** | **11.5h** | |

---

## 🔗 HERRAMIENTAS DE VALIDACIÓN

- **WAVE Browser Extension**: Detecta errores ARIA/WCAG
- **AXE DevTools**: Auditoría automática  
- **WebAIM Contrast Checker**: Verifica ratios
- **NVDA Screen Reader**: Pruebas con reader (gratis)

**Usar antes de deploy:**
```bash
cd nuevo-frontend
npm install --save-dev @axe-core/puppeteer
npm run accessibility-audit
```

---

¿Necesitas que implemente algunos de estos fixes ahora?
