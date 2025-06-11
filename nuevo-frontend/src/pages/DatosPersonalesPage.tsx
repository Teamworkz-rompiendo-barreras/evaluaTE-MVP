import { useState } from "react";
import { useForm } from 'react-hook-form'
import { useAppDispatch, useAppSelector } from '../app/hooks'
import { saveContact } from '../features/personal/personalSlice'
import { useNavigate } from 'react-router-dom'
import ProgressBar from '../components/ProgressBar'
import logo from "../assets/Logo_teamworkz.png";   // ← import explícito

export default function DatosPersonalesPage() {
  const dispatch = useAppDispatch()
  const navigate = useNavigate()
  const current = useAppSelector(state => state.personal)

  const { register, handleSubmit, formState: { errors } } = useForm<{
    firstName: string
    lastName: string
    email: string
    whatsapp: string
  }>({
    defaultValues: {
      firstName: current.firstName,
      lastName: current.lastName,
      email: current.email,
      whatsapp: current.whatsapp,
    }
  })

  const onSubmit = (data: { firstName: string; lastName: string; email: string; whatsapp: string }) => {
    if (!data.email.trim() && !data.whatsapp.trim()) {
      alert('Debes indicar email o WhatsApp.')
      return
    }
    dispatch(saveContact(data))
    navigate('/register/preferences')
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="max-w-md mx-auto p-4 space-y-6">
      <ProgressBar step={1} total={2} />

      <h1 className="text-2xl font-bold">Paso 1 de 2: Datos de contacto</h1>

      <div>
        <label className="block font-medium">Nombre</label>
        <input {...register('firstName', { required: true })} className="input" />
        {errors.firstName && <p className="text-red-600">Obligatorio</p>}
      </div>

      <div>
        <label className="block font-medium">Apellido</label>
        <input {...register('lastName', { required: true })} className="input" />
        {errors.lastName && <p className="text-red-600">Obligatorio</p>}
      </div>

      <div>
        <label className="block font-medium">Email</label>
        <input type="email" {...register('email')} className="input" />
      </div>

      <div>
        <label className="block font-medium">WhatsApp</label>
        <input {...register('whatsapp')} className="input" />
      </div>

      <button type="submit" className="btn-primary w-full">Siguiente</button>
    </form>
  )
}
