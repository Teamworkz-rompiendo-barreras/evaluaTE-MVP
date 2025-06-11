import React from 'react'
import { useForm } from 'react-hook-form'
import { useNavigate, Link } from 'react-router-dom'
import { useAppDispatch, useAppSelector } from '../../app/hooks'
import { savePreferences } from './personalSlice'
import ProgressBar from '../../components/ProgressBar'

type PrefData = {
  jobPreferences: string[]
  workMode: 'remoto' | 'presencial' | 'híbrido'
  availability: 'mañana' | 'tarde' | 'completa'
  startDate: string
  willingToRelocate: boolean
  hasDisabilityCert: boolean
}

export default function PreferencesStep() {
  const dispatch = useAppDispatch()
  const navigate = useNavigate()
  const current = useAppSelector(state => state.personal)

  const { register, handleSubmit, formState: { errors } } = useForm<PrefData>({
    defaultValues: {
      jobPreferences: current.jobPreferences,
      workMode: current.workMode,
      availability: current.availability,
      startDate: current.startDate,
      willingToRelocate: current.willingToRelocate,
      hasDisabilityCert: current.hasDisabilityCert,
    }
  })

  const onSubmit = (data: PrefData) => {
    if (data.jobPreferences.length === 0) {
      alert('Selecciona al menos un tipo de trabajo.')
      return
    }
    dispatch(savePreferences(data))
    navigate('/games')
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="max-w-md mx-auto p-4 space-y-6">
      <ProgressBar step={2} total={2} />

      <h2 className="text-xl font-bold">Paso 2 de 2: Tus preferencias</h2>

      <fieldset>
        <legend className="font-medium">¿Qué tipo de trabajo te interesa?</legend>
        {['Soporte','Administración','Ventas','Marketing','Desarrollo'].map(opt => (
          <label key={opt} className="block">
            <input
              type="checkbox"
              value={opt}
              {...register('jobPreferences')}
            /> {opt}
          </label>
        ))}
        {errors.jobPreferences && <p className="text-red-600">{errors.jobPreferences.message}</p>}
      </fieldset>

      <div>
        <label className="block font-medium">Modalidad</label>
        <select {...register('workMode', { required: true })}>
          <option value="remoto">Remoto</option>
          <option value="presencial">Presencial</option>
          <option value="híbrido">Híbrido</option>
        </select>
      </div>

      <div>
        <label className="block font-medium">Disponibilidad horaria</label>
        <select {...register('availability', { required: true })}>
          <option value="mañana">Mañana</option>
          <option value="tarde">Tarde</option>
          <option value="completa">Completa</option>
        </select>
      </div>

      <div>
        <label className="block font-medium">Fecha de incorporación</label>
        <input type="date" {...register('startDate', { required: true })} />
      </div>

      <div className="flex items-center">
        <input type="checkbox" {...register('willingToRelocate')} id="relocate" />
        <label htmlFor="relocate" className="ml-2">
          Estoy dispuesto a cambiar de residencia
        </label>
      </div>

      <div className="flex items-center">
        <input type="checkbox" {...register('hasDisabilityCert')} id="cert" />
        <label htmlFor="cert" className="ml-2">
          Tengo certificado de discapacidad
        </label>
      </div>

      <div className="flex justify-between">
        <Link to="/register/contact" className="btn-secondary">Anterior</Link>
        <button type="submit" className="btn-primary">Finalizar</button>
      </div>
    </form>
  )
}
