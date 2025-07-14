// src/features/personal/components/PreferencesStep.tsx
import React, { useRef } from 'react'
import { useForm, SubmitHandler } from 'react-hook-form'
import { useNavigate } from 'react-router-dom'

// Acciones desde Redux
import { useAppDispatch, useAppSelector } from './../../app/hooks'
import { savePreferences } from './personalSlice'

// Componentes reutilizables
// import ProgressBar from './../../components/ProgressBar'

// Tipos definidos en skills.ts
type PrefData = {
  jobPreferences: string // Ej: "Desarrollo web"
  workMode: 'remoto' | 'presencial' | 'híbrido'
  availability: 'mañana' | 'tarde' | 'completa'
  startDate: 'inmediata' | '15_días' | '1_mes' | 'más_de_1_mes'
  willingToRelocate: boolean
  hasDisabilityCert: boolean
}

export default function PreferencesStep() {
  const dispatch = useAppDispatch()
  const navigate = useNavigate()
  const current = useAppSelector((state) => state.personal)

  // Nuevo: referencia para saber si se ha enviado el formulario
  const submittedRef = useRef(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<PrefData>({
    mode: 'onChange', // Validación en tiempo real
    defaultValues: {
      jobPreferences: typeof current.jobPreferences === 'string'
        ? current.jobPreferences
        : (current.jobPreferences?.areas?.[0] || ''),
      workMode: current.workMode || 'remoto',
      availability: current.availability || 'completa',
      startDate: current.startDate || 'inmediata',
      willingToRelocate: Boolean(current.willingToRelocate),
      hasDisabilityCert: Boolean(current.hasDisabilityCert),
    },
  })

  const onSubmit: SubmitHandler<PrefData> = (data) => {
    if (submittedRef.current) return;
    // Validación extra por seguridad
    if (!data.jobPreferences || data.jobPreferences.trim().length < 3) return;
    if (!data.workMode) return;
    if (!data.availability) return;
    if (!data.startDate) return;

    const jobPrefObj = {
      areas: [data.jobPreferences],
      needs: [],
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
    // Navega a /games tras guardar preferencias
    navigate('/games');
  }

  // Eliminamos el useEffect problemático que causaba redirecciones automáticas

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <form
        onSubmit={handleSubmit(onSubmit)}
        className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 space-y-6 relative z-10"
      >
        {/* Barra de progreso */}
        <div className="text-center">
          <h2 className="text-xl font-semibold">Paso 2 de 2</h2>
          <p className="text-gray-600 mb-4">Tus preferencias laborales</p>
        </div>

        {/* ProgressBar temporalmente deshabilitado */}
        {/* <ProgressBar current={2} total={2} /> */}

        {/* Campo: Tipo de trabajo */}
        <div>
          <label htmlFor="jobPreferences" className="block font-medium mb-1">
            ¿Qué tipo de trabajo estás buscando? 🎯
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
            className={`w-full border rounded px-3 py-2 ${errors.jobPreferences ? 'border-red-500' : ''}`}
          />
          {errors.jobPreferences && (
            <p className="text-red-600 mt-1">{errors.jobPreferences.message}</p>
          )}
        </div>

        {/* Campo: Modalidad */}
        <div>
          <label htmlFor="workMode" className="block font-medium mb-1">
            ¿En qué modalidad prefieres trabajar? 📡
          </label>
          <select
            id="workMode"
            {...register('workMode', { required: 'Elige una opción' })}
            className={`w-full border rounded px-3 py-2 ${errors.workMode ? 'border-red-500' : ''}`}
          >
            <option value="">Selecciona una opción</option>
            <option value="remoto">Trabajo remoto</option>
            <option value="presencial">Presencial</option>
            <option value="híbrido">Híbrido</option>
          </select>
          {errors.workMode && (
            <p className="text-red-600 mt-1">{errors.workMode.message}</p>
          )}
        </div>

        {/* Campo: Disponibilidad horaria */}
        <div>
          <label htmlFor="availability" className="block font-medium mb-1">
            ¿Cuál es tu disponibilidad horaria? ⏰
          </label>
          <select
            id="availability"
            {...register('availability', { required: 'Elige una opción' })}
            className={`w-full border rounded px-3 py-2 ${errors.availability ? 'border-red-500' : ''}`}
          >
            <option value="">Selecciona una opción</option>
            <option value="mañana">Mañana</option>
            <option value="tarde">Tarde</option>
            <option value="completa">Completa</option>
          </select>
          {errors.availability && (
            <p className="text-red-600 mt-1">{errors.availability.message}</p>
          )}
        </div>

        {/* Campo: Incorporación */}
        <div>
          <label htmlFor="startDate" className="block font-medium mb-1">
            ¿Cuándo puedes incorporarte? 📅
          </label>
          <select
            id="startDate"
            {...register('startDate', { required: 'Selecciona una fecha' })}
            className={`w-full border rounded px-3 py-2 ${errors.startDate ? 'border-red-500' : ''}`}
          >
            <option value="">Selecciona una opción</option>
            <option value="inmediata">Inmediatamente</option>
            <option value="15_días">En 15 días</option>
            <option value="1_mes">En 1 mes</option>
            <option value="más_de_1_mes">Más de 1 mes</option>
          </select>
          {errors.startDate && (
            <p className="text-red-600 mt-1">{errors.startDate.message}</p>
          )}
        </div>

        {/* Checkbox: Mudanza */}
        <div className="flex items-center space-x-2">
          <input
            id="relocate"
            type="checkbox"
            {...register('willingToRelocate')}
            className="h-5 w-5 text-blue-600"
          />
          <label htmlFor="relocate" className="font-medium">
            Estoy dispuesto/a a cambiar de ciudad si es necesario
          </label>
        </div>

        {/* Checkbox: Certificado de discapacidad */}
        <div className="flex items-center space-x-2">
          <input
            id="cert"
            type="checkbox"
            {...register('hasDisabilityCert')}
            className="h-5 w-5 text-blue-600"
          />
          <label htmlFor="cert" className="font-medium">
            Tengo certificado de discapacidad oficial reconocido
          </label>
        </div>

        {/* Botones de navegación */}
        <div className="flex justify-between pt-4">
          <button
            type="button"
            onClick={() => navigate('/register/contact')}
            className="text-gray-600 hover:text-gray-800 font-medium flex items-center gap-1"
          >
            ← Volver atrás
          </button>
          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 transition-colors"
          >
            Finalizar y empezar minijuegos
          </button>
        </div>
      </form>
    </div>
  )
}