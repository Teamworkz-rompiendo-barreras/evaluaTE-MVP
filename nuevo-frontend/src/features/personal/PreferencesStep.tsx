// src/features/personal/components/PreferencesStep.tsx
import { useRef } from 'react';
import { useForm, SubmitHandler } from 'react-hook-form'
import { useNavigate } from 'react-router-dom'

// Acciones desde Redux
import { useAppDispatch, useAppSelector } from './../../app/hooks'
import { savePreferences } from './personalSlice'

// Tipos definidos en skills.ts (Añadido gdprConsent solo para validación local)
type PrefData = {
  jobPreferences: string
  workMode: 'remoto' | 'presencial' | 'híbrido'
  availability: 'mañana' | 'tarde' | 'completa'
  startDate: 'inmediata' | '15_días' | '1_mes' | 'más_de_1_mes'
  willingToRelocate: boolean
  hasDisabilityCert: boolean
  specificNeeds: string
  gdprConsent?: boolean // Campo virtual para control legal
}

export default function PreferencesStep() {
  const dispatch = useAppDispatch()
  const navigate = useNavigate()
  const current = useAppSelector((state) => state.personal)

  const submittedRef = useRef(false);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<PrefData>({
    mode: 'onChange',
    defaultValues: {
      jobPreferences: typeof current.jobPreferences === 'object' && current.jobPreferences?.areas?.[0]
        ? current.jobPreferences?.areas?.[0]
        : (typeof current.jobPreferences === 'string' ? current.jobPreferences : ''),
      workMode: current.workMode || 'remoto',
      availability: current.availability || 'completa',
      startDate: current.startDate || 'inmediata',
      willingToRelocate: Boolean(current.willingToRelocate),
      hasDisabilityCert: Boolean(current.hasDisabilityCert),
      specificNeeds: typeof current.jobPreferences === 'object' && current.jobPreferences?.needs?.[0] 
        ? current.jobPreferences.needs[0] 
        : '',
      gdprConsent: Boolean(current.gdprConsent),
    },
  })

  // Lógica de Divulgación Progresiva: Observamos si hay datos de salud
  const watchDisability = watch('hasDisabilityCert');
  const watchNeeds = watch('specificNeeds');
  // Siempre requerimos consentimiento explícito para categorías especiales (datos de salud)
  const requiresConsent = (watchDisability || (watchNeeds && watchNeeds.trim().length > 0));

  const onSubmit: SubmitHandler<PrefData> = (data) => {
    if (submittedRef.current) return;
    
    if (!data.jobPreferences || data.jobPreferences.trim().length < 3) return;
    if (!data.workMode) return;
    if (!data.availability) return;
    if (!data.startDate) return;

    const jobPrefObj = {
      areas: [data.jobPreferences],
      desired_roles: [data.jobPreferences],
      desiredRoles: [data.jobPreferences],
      needs: data.specificNeeds ? [data.specificNeeds] : [],
      workMode: data.workMode,
      work_mode: data.workMode,
      availability: data.availability,
      willingToRelocate: data.willingToRelocate,
      hasDisabilityCert: data.hasDisabilityCert,
    };

    dispatch(savePreferences({
      jobPreferences: jobPrefObj,
      workMode: data.workMode,
      availability: data.availability,
      startDate: data.startDate,
      willingToRelocate: data.willingToRelocate,
      hasDisabilityCert: data.hasDisabilityCert,
      gdprConsent: Boolean(data.gdprConsent),
    }));
    
    submittedRef.current = true;
    navigate('/games');
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center p-4 transition-colors">
      <form
        onSubmit={handleSubmit(onSubmit)}
        className="max-w-md w-full bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 space-y-6 relative z-10 transition-colors"
      >
        <div className="text-center">
          <h2 className="text-xl font-semibold dark:text-white">Paso 2 de 2</h2>
          <p className="text-gray-600 dark:text-gray-400 mb-4">Tus preferencias laborales</p>
        </div>

        {/* Campo: Tipo de trabajo */}
        <div>
          <label htmlFor="jobPreferences" className="block font-medium mb-1 dark:text-gray-200">
            ¿Qué tipo de trabajo estás buscando? <span aria-hidden="true">🎯</span>
          </label>
          <input
            id="jobPreferences"
            type="text"
            placeholder="Ej. Atención al cliente, Logística, Desarrollo web…"
            {...register('jobPreferences', {
              required: 'Campo obligatorio',
              minLength: {
                value: 3,
                message: 'Indica al menos 3 caracteres',
              },
            })}
            className={`w-full border rounded px-3 py-2 dark:bg-gray-700 dark:border-gray-600 dark:text-white ${errors.jobPreferences ? 'border-red-500 focus:ring-red-500' : 'focus:ring-blue-500'}`}
          />
          {errors.jobPreferences && (
            <p className="text-red-600 dark:text-red-400 mt-1 text-sm font-medium" role="alert">{errors.jobPreferences.message}</p>
          )}
        </div>

        {/* Campo: Modalidad */}
        <div>
          <label htmlFor="workMode" className="block font-medium mb-1 dark:text-gray-200">
            ¿En qué modalidad prefieres trabajar? <span aria-hidden="true">📡</span>
          </label>
          <select
            id="workMode"
            {...register('workMode', { required: 'Elige una opción' })}
            className={`w-full border rounded px-3 py-2 dark:bg-gray-700 dark:border-gray-600 dark:text-white ${errors.workMode ? 'border-red-500 focus:ring-red-500' : 'focus:ring-blue-500'}`}
          >
            <option value="">Selecciona una opción</option>
            <option value="remoto">Trabajo remoto</option>
            <option value="presencial">Presencial</option>
            <option value="híbrido">Híbrido</option>
          </select>
          {errors.workMode && (
            <p className="text-red-600 dark:text-red-400 mt-1 text-sm font-medium" role="alert">{errors.workMode.message}</p>
          )}
        </div>

        {/* Campo: Disponibilidad horaria */}
        <div>
          <label htmlFor="availability" className="block font-medium mb-1 dark:text-gray-200">
            ¿Cuál es tu disponibilidad horaria? <span aria-hidden="true">⏰</span>
          </label>
          <select
            id="availability"
            {...register('availability', { required: 'Elige una opción' })}
            className={`w-full border rounded px-3 py-2 dark:bg-gray-700 dark:border-gray-600 dark:text-white ${errors.availability ? 'border-red-500 focus:ring-red-500' : 'focus:ring-blue-500'}`}
          >
            <option value="">Selecciona una opción</option>
            <option value="mañana">Mañana</option>
            <option value="tarde">Tarde</option>
            <option value="completa">Completa</option>
          </select>
          {errors.availability && (
            <p className="text-red-600 dark:text-red-400 mt-1 text-sm font-medium" role="alert">{errors.availability.message}</p>
          )}
        </div>

        {/* Campo: Incorporación */}
        <div>
          <label htmlFor="startDate" className="block font-medium mb-1 dark:text-gray-200">
            ¿Cuándo puedes incorporarte? <span aria-hidden="true">📅</span>
          </label>
          <select
            id="startDate"
            {...register('startDate', { required: 'Selecciona una fecha' })}
            className={`w-full border rounded px-3 py-2 dark:bg-gray-700 dark:border-gray-600 dark:text-white ${errors.startDate ? 'border-red-500 focus:ring-red-500' : 'focus:ring-blue-500'}`}
          >
            <option value="">Selecciona una opción</option>
            <option value="inmediata">Inmediatamente</option>
            <option value="15_días">En 15 días</option>
            <option value="1_mes">En 1 mes</option>
            <option value="más_de_1_mes">Más de 1 mes</option>
          </select>
          {errors.startDate && (
            <p className="text-red-600 dark:text-red-400 mt-1 text-sm font-medium" role="alert">{errors.startDate.message}</p>
          )}
        </div>

        {/* Checkbox: Mudanza */}
        <div className="flex items-center space-x-2">
          <input
            id="relocate"
            type="checkbox"
            {...register('willingToRelocate')}
            className="h-5 w-5 text-blue-600 rounded border-gray-300 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700"
          />
          <label htmlFor="relocate" className="font-medium dark:text-gray-200 cursor-pointer">
            Estoy dispuesto/a a cambiar de ciudad si es necesario
          </label>
        </div>

        {/* Checkbox: Certificado de discapacidad */}
        <div className="flex items-center space-x-2">
          <input
            id="cert"
            type="checkbox"
            {...register('hasDisabilityCert')}
            className="h-5 w-5 text-blue-600 rounded border-gray-300 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700"
          />
          <label htmlFor="cert" className="font-medium dark:text-gray-200 cursor-pointer">
            Tengo certificado de discapacidad oficial reconocido
          </label>
        </div>

        {/* Campo: Necesidades específicas */}
        <div>
          <label htmlFor="specificNeeds" className="block font-medium mb-1 dark:text-gray-200">
            ¿Tienes alguna necesidad específica o adaptación que debamos conocer? <span aria-hidden="true">🤝</span>
          </label>
          <textarea
            id="specificNeeds"
            placeholder="Ej. Necesito flexibilidad horaria, adaptaciones en el puesto de trabajo, accesibilidad específica, etc. (opcional)"
            {...register('specificNeeds')}
            rows={3}
            className="w-full border rounded px-3 py-2 resize-none dark:bg-gray-700 dark:border-gray-600 dark:text-white focus:ring-blue-500"
          />
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Esta información nos ayudará a encontrar oportunidades laborales más adecuadas para ti.
          </p>
        </div>

        {/* CORTAFUEGOS LEGAL: Consentimiento explícito condicional */}
        {requiresConsent && (
          <div 
            className="bg-blue-50 dark:bg-slate-800 p-4 rounded-lg border border-blue-100 dark:border-slate-700" 
            role="region" 
            aria-live="polite"
          >
             <p className="text-xs text-gray-700 dark:text-slate-300 mb-3">
               <strong>Transparencia:</strong> Usaremos esta información exclusivamente para que nuestra IA adapte tu informe y te recomiende entornos laborales que respeten tus necesidades. No se compartirá con empresas sin tu permiso.
             </p>
             <div className="flex items-start space-x-2">
               <input
                 id="gdprConsent"
                 type="checkbox"
                 {...register('gdprConsent', { 
                   required: requiresConsent ? 'Debes consentir el tratamiento de datos para aplicar adaptaciones.' : false 
                 })}
                 className="h-5 w-5 text-blue-600 mt-0.5 rounded border-gray-300 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700"
               />
               <label htmlFor="gdprConsent" className="text-sm font-medium text-gray-800 dark:text-slate-200 cursor-pointer">
                 Consiento explícitamente el tratamiento de mis datos de salud y adaptación para generar mi informe, según la <a href="/privacidad" target="_blank" rel="noopener noreferrer" className="text-blue-600 dark:text-blue-400 hover:underline">Política de Privacidad</a>.
               </label>
             </div>
             {errors.gdprConsent && (
               <p className="text-red-600 dark:text-red-400 mt-2 text-sm font-medium" role="alert">{errors.gdprConsent.message}</p>
             )}
          </div>
        )}

        {/* Botones de navegación */}
        <div className="flex justify-between items-center pt-4">
          <button
            type="button"
            onClick={() => navigate('/register/contact')}
            className="text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200 font-medium flex items-center gap-1"
          >
            <span aria-hidden="true">←</span> Volver atrás
          </button>
          <button
            type="submit"
            className="bg-blue-600 text-white py-2 px-6 rounded hover:bg-blue-700 transition-colors focus:ring-4 focus:ring-blue-300 dark:focus:ring-blue-800 font-medium"
          >
            Continuar
          </button>
        </div>
      </form>
    </div>
  )
}