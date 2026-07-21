// src/features/personal/components/PreferencesStep.tsx
import { useRef } from 'react';
import { useForm, SubmitHandler } from 'react-hook-form'
import { useNavigate } from 'react-router-dom'

// Acciones desde Redux
import { useAppDispatch, useAppSelector } from './../../app/hooks'
import { savePreferences } from './personalSlice'

type PrefData = {
  jobPreferences: string 
  workMode: 'remoto' | 'presencial' | 'híbrido'
  availability: 'mañana' | 'tarde' | 'completa'
  startDate: 'inmediata' | '15_días' | '1_mes' | 'más_de_1_mes'
  willingToRelocate: boolean
  hasDisabilityCert: boolean
  specificNeeds: string 
}

export default function PreferencesStep() {
  const dispatch = useAppDispatch()
  const navigate = useNavigate()
  const current = useAppSelector((state) => state.personal)

  const submittedRef = useRef(false);

  const {
    register,
    handleSubmit,
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
    },
  })

  const onSubmit: SubmitHandler<PrefData> = (data) => {
    if (submittedRef.current) return;
    if (!data.jobPreferences || data.jobPreferences.trim().length < 3) return;
    if (!data.workMode) return;
    if (!data.availability) return;
    if (!data.startDate) return;

    const jobPrefObj = {
      areas: [data.jobPreferences],
      needs: data.specificNeeds ? [data.specificNeeds] : [],
      workMode: data.workMode,
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
          <p className="text-gray-600 dark:text-gray-300 mb-4">Tus preferencias laborales</p>
        </div>

        {/* Campo: Tipo de trabajo */}
        <div>
          <label htmlFor="jobPreferences" className="block font-medium mb-1 dark:text-gray-200">
            ¿Qué tipo de trabajo estás buscando? 🎯
          </label>
          <input
            id="jobPreferences"
            type="text"
            aria-invalid={errors.jobPreferences ? "true" : "false"}
            placeholder="Ej. Atención al cliente, Logística..."
            {...register('jobPreferences', {
              required: 'Campo obligatorio',
              minLength: { value: 3, message: 'Indica al menos 3 caracteres' },
            })}
            /* FIX Accesibilidad: Añadido text-gray-900 explícito y placeholder accesible */
            className={`w-full border rounded px-3 py-2 bg-white text-gray-900 placeholder-gray-500 dark:bg-gray-700 dark:text-white dark:placeholder-gray-400 dark:border-gray-600 focus:ring-2 focus:ring-blue-500 outline-none ${errors.jobPreferences ? 'border-red-500' : 'border-gray-300'}`}
          />
          {errors.jobPreferences && (
            <p role="alert" className="text-red-600 dark:text-red-400 text-sm mt-1">{errors.jobPreferences.message}</p>
          )}
        </div>

        {/* Campo: Modalidad */}
        <div>
          <label htmlFor="workMode" className="block font-medium mb-1 dark:text-gray-200">
            ¿En qué modalidad prefieres trabajar? 📡
          </label>
          <select
            id="workMode"
            aria-invalid={errors.workMode ? "true" : "false"}
            {...register('workMode', { required: 'Elige una opción' })}
            className={`w-full border rounded px-3 py-2 bg-white text-gray-900 dark:bg-gray-700 dark:text-white dark:border-gray-600 focus:ring-2 focus:ring-blue-500 outline-none ${errors.workMode ? 'border-red-500' : 'border-gray-300'}`}
          >
            <option value="">Selecciona una opción</option>
            <option value="remoto">Trabajo remoto</option>
            <option value="presencial">Presencial</option>
            <option value="híbrido">Híbrido</option>
          </select>
          {errors.workMode && (
            <p role="alert" className="text-red-600 dark:text-red-400 text-sm mt-1">{errors.workMode.message}</p>
          )}
        </div>

        {/* Campo: Disponibilidad horaria */}
        <div>
          <label htmlFor="availability" className="block font-medium mb-1 dark:text-gray-200">
            ¿Cuál es tu disponibilidad horaria? ⏰
          </label>
          <select
            id="availability"
            aria-invalid={errors.availability ? "true" : "false"}
            {...register('availability', { required: 'Elige una opción' })}
            className={`w-full border rounded px-3 py-2 bg-white text-gray-900 dark:bg-gray-700 dark:text-white dark:border-gray-600 focus:ring-2 focus:ring-blue-500 outline-none ${errors.availability ? 'border-red-500' : 'border-gray-300'}`}
          >
            <option value="">Selecciona una opción</option>
            <option value="mañana">Mañana</option>
            <option value="tarde">Tarde</option>
            <option value="completa">Completa</option>
          </select>
          {errors.availability && (
            <p role="alert" className="text-red-600 dark:text-red-400 text-sm mt-1">{errors.availability.message}</p>
          )}
        </div>

        {/* Campo: Incorporación */}
        <div>
          <label htmlFor="startDate" className="block font-medium mb-1 dark:text-gray-200">
            ¿Cuándo puedes incorporarte? 📅
          </label>
          <select
            id="startDate"
            aria-invalid={errors.startDate ? "true" : "false"}
            {...register('startDate', { required: 'Selecciona una fecha' })}
            className={`w-full border rounded px-3 py-2 bg-white text-gray-900 dark:bg-gray-700 dark:text-white dark:border-gray-600 focus:ring-2 focus:ring-blue-500 outline-none ${errors.startDate ? 'border-red-500' : 'border-gray-300'}`}
          >
            <option value="">Selecciona una opción</option>
            <option value="inmediata">Inmediatamente</option>
            <option value="15_días">En 15 días</option>
            <option value="1_mes">En 1 mes</option>
            <option value="más_de_1_mes">Más de 1 mes</option>
          </select>
          {errors.startDate && (
            <p role="alert" className="text-red-600 dark:text-red-400 text-sm mt-1">{errors.startDate.message}</p>
          )}
        </div>

        {/* Checkbox: Mudanza */}
        <div className="flex items-center space-x-2">
          <input
            id="relocate"
            type="checkbox"
            {...register('willingToRelocate')}
            className="h-5 w-5 text-blue-600 dark:bg-gray-700 dark:border-gray-600 focus:ring-blue-500"
          />
          <label htmlFor="relocate" className="font-medium text-gray-900 dark:text-gray-200">
            Estoy dispuesto/a a cambiar de ciudad si es necesario
          </label>
        </div>

        {/* Checkbox: Certificado de discapacidad */}
        <div className="flex items-center space-x-2">
          <input
            id="cert"
            type="checkbox"
            {...register('hasDisabilityCert')}
            className="h-5 w-5 text-blue-600 dark:bg-gray-700 dark:border-gray-600 focus:ring-blue-500"
          />
          <label htmlFor="cert" className="font-medium text-gray-900 dark:text-gray-200">
            Tengo certificado de discapacidad oficial reconocido
          </label>
        </div>

        {/* Campo: Necesidades específicas */}
        <div>
          <label htmlFor="specificNeeds" className="block font-medium mb-1 dark:text-gray-200">
            ¿Tienes alguna necesidad específica o adaptación que debamos conocer? 🤝
          </label>
          <textarea
            id="specificNeeds"
            placeholder="Ej. Necesito flexibilidad horaria, adaptaciones..."
            {...register('specificNeeds')}
            rows={3}
            className="w-full border rounded px-3 py-2 resize-none bg-white text-gray-900 placeholder-gray-500 border-gray-300 dark:bg-gray-700 dark:text-white dark:placeholder-gray-400 dark:border-gray-600 focus:ring-2 focus:ring-blue-500 outline-none"
          />
        </div>

        {/* Botones de navegación */}
        <div className="flex justify-between pt-4 gap-4">
          <button
            type="button"
            onClick={() => navigate('/register/contact')}
            className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white font-medium flex items-center gap-1 focus:outline-none focus:ring-2 focus:ring-gray-400 rounded px-2 py-1"
          >
            ← Volver atrás
          </button>
          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 transition-colors focus:ring-4 focus:ring-blue-300 dark:focus:ring-blue-800 outline-none font-semibold shadow-sm"
          >
            Continuar a los minijuegos
          </button>
        </div>
      </form>
    </div>
  )
}