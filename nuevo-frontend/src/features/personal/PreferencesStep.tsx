// src/features/personal/PreferencesStep.tsx
import React from 'react'
import { useForm, SubmitHandler } from 'react-hook-form'          // ← importamos SubmitHandler
import { useNavigate, Link } from 'react-router-dom'
import { useAppDispatch, useAppSelector } from '../../app/hooks'
import { savePreferences } from './personalSlice'
import ProgressBar from '../../components/ProgressBar'

type PrefData = {
  jobPreferences: string
  workMode: 'remoto' | 'presencial' | 'híbrido'
  availability: 'mañana' | 'tarde' | 'completa'
  startDate: 'inmediata' | '15_días' | '1_mes' | 'más_de_1_mes'
  willingToRelocate: boolean
  hasDisabilityCert: boolean
}

export default function PreferencesStep() {
  const dispatch = useAppDispatch()
  const navigate = useNavigate()
  const current = useAppSelector(s => s.personal)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<PrefData>({
    defaultValues: {
      jobPreferences:    current.jobPreferences,
      workMode:          current.workMode,
      availability:      current.availability,
      startDate:         current.startDate as PrefData['startDate'],
      willingToRelocate: current.willingToRelocate,
      hasDisabilityCert: current.hasDisabilityCert,
    }
  })

  // ← anotamos explícitamente la firma
  const onSubmit: SubmitHandler<PrefData> = data => {
    if (!data.jobPreferences.trim()) {
      alert('Indica el tipo de trabajo que buscas.')
      return
    }
    dispatch(savePreferences(data))
    navigate('/games')
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="max-w-md mx-auto p-6 space-y-6">
      <ProgressBar step={2} total={2} />

      <h2 className="text-2xl font-bold">Paso 2 de 2 – Tus preferencias</h2>

      <div>
        <label htmlFor="jobPreferences" className="block font-medium">
          ¿Qué tipo de trabajo estás buscando?
        </label>
        <input
          id="jobPreferences"
          type="text"
          {...register('jobPreferences', { required: 'Campo obligatorio' })}
          placeholder="Ej. Atención al cliente, Recepción, Desarrollo web…"
          className="mt-1 block w-full border rounded px-3 py-2"
        />
        {errors.jobPreferences && (
          <p className="text-red-600 mt-1">{errors.jobPreferences.message}</p>
        )}
      </div>

      {/* resto de campos (workMode, availability, startDate, checkboxes…) */}

      <div className="flex justify-between">
        <Link to="/register/contact" className="text-gray-600 hover:underline">
          ← Anterior
        </Link>
        <button
          type="submit"
          className="py-2 px-4 bg-green-600 text-white rounded hover:bg-green-700"
        >
          Finalizar
        </button>
      </div>
    </form>
  )
}

