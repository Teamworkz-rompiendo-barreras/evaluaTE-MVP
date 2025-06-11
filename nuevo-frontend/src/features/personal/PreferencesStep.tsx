// src/features/personal/PreferencesStep.tsx
import React from 'react'
import { useForm, SubmitHandler } from 'react-hook-form'
import { useNavigate, Link } from 'react-router-dom'
import { useAppDispatch, useAppSelector } from '../../app/hooks'
import { savePreferences } from './personalSlice'
import ProgressBar from '../../components/ProgressBar'

type PrefData = {
  jobPreferences: string     // ahora texto libre
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

  const { register, handleSubmit, formState: { errors } } = useForm<PrefData>({
   defaultValues: {
     jobPreferences:    current.jobPreferences,
     workMode:          current.workMode,
     availability:      current.availability,
     startDate:         current.startDate,
     willingToRelocate: current.willingToRelocate,
     hasDisabilityCert: current.hasDisabilityCert
   } as PrefData  // fuerza a TS a ver aquí un PrefData completo
 });

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

      <h2 className="text-2xl font-bold">Paso 2 de 2 - Tus preferencias</h2>

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

      <div>
        <label htmlFor="workMode" className="block font-medium">Modalidad</label>
        <select
          id="workMode"
          {...register('workMode', { required: 'Elige modalidad' })}
          className="mt-1 block w-full border rounded px-3 py-2"
        >
          <option value="remoto">Remoto</option>
          <option value="presencial">Presencial</option>
          <option value="híbrido">Híbrido</option>
        </select>
      </div>

      <div>
        <label htmlFor="availability" className="block font-medium">Disponibilidad horaria</label>
        <select
          id="availability"
          {...register('availability', { required: 'Elige disponibilidad' })}
          className="mt-1 block w-full border rounded px-3 py-2"
        >
          <option value="mañana">Mañana</option>
          <option value="tarde">Tarde</option>
          <option value="completa">Completa</option>
        </select>
      </div>

      <div>
        <label htmlFor="startDate" className="block font-medium">Incorporación</label>
        <select
          id="startDate"
          {...register('startDate', { required: 'Selecciona opción' })}
          className="mt-1 block w-full border rounded px-3 py-2"
        >
          <option value="inmediata">Inmediata</option>
          <option value="15_días">En 15 días</option>
          <option value="1_mes">En 1 mes</option>
          <option value="más_de_1_mes">Más de 1 mes</option>
        </select>
      </div>

      <div className="flex items-center">
        <input
          id="relocate"
          type="checkbox"
          {...register('willingToRelocate')}
          className="mr-2"
        />
        <label htmlFor="relocate">Estoy dispuesto/a a cambiar de residencia</label>
      </div>

      <div className="flex items-center">
        <input
          id="cert"
          type="checkbox"
          {...register('hasDisabilityCert')}
          className="mr-2"
        />
        <label htmlFor="cert">Tengo certificado de discapacidad</label>
      </div>

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

