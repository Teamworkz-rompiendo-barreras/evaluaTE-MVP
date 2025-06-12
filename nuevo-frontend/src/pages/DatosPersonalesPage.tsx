// src/pages/DatosPersonalesPage.tsx
import React from "react";
import logo from "../assets/Logo_teamworkz.png";
import { useForm, SubmitHandler } from 'react-hook-form';
import { useAppDispatch, useAppSelector } from '../app/hooks';
import { saveContact } from '../features/personal/personalSlice';
import { useNavigate } from 'react-router-dom';
import ProgressBar from '../components/ProgressBar';

type ContactForm = {
  firstName: string;
  lastName: string;    // aquí escribirá los dos apellidos
  email: string;
  whatsapp: string;
};

export default function DatosPersonalesPage() {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const current = useAppSelector(state => state.personal);

  const { register, handleSubmit, formState: { errors } } = useForm<ContactForm>({
    defaultValues: {
      firstName: current.firstName,
      lastName:  current.lastName,
      email:     current.email,
      whatsapp:  current.whatsapp,
    }
  });

  const onSubmit: SubmitHandler<ContactForm> = (data) => {
    // Validamos que al menos email o WhatsApp tenga contenido
    if (!data.email.trim() && !data.whatsapp.trim()) {
      alert('Debes indicar email o WhatsApp.');
      return;
    }
    dispatch(saveContact(data));
    navigate('/register/preferences');
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="max-w-md mx-auto p-6 space-y-6">
      {/* Logo en la parte superior */}
      <div className="flex justify-center">
        <img src={logo} alt="Teamworkz" className="h-16" />
      </div>

      {/* Barra de progreso */}
      <ProgressBar step={1} total={2} />

      <h1 className="text-2xl font-bold text-center">
        Paso 1 de 2 – Datos de contacto
      </h1>

      {/* Nombre */}
      <div>
        <label htmlFor="firstName" className="block font-medium">
          Nombre
        </label>
        <input
          id="firstName"
          type="text"
          placeholder="Ej. Juan"
          {...register('firstName', { required: 'El nombre es obligatorio' })}
          className="input mt-1 w-full"
        />
        {errors.firstName && (
          <p className="text-red-600 mt-1">{errors.firstName.message}</p>
        )}
      </div>

      {/* Apellidos */}
      <div>
        <label htmlFor="lastName" className="block font-medium">
          Apellidos
        </label>
        <input
          id="lastName"
          type="text"
          placeholder="Ej. García Pérez"
          {...register('lastName', { required: 'Los apellidos son obligatorios' })}
          className="input mt-1 w-full"
        />
        {errors.lastName && (
          <p className="text-red-600 mt-1">{errors.lastName.message}</p>
        )}
      </div>

      {/* Email */}
      <div>
        <label htmlFor="email" className="block font-medium">
          Email (opcional)
        </label>
        <input
          id="email"
          type="email"
          placeholder="juan@example.com"
          {...register('email')}
          className="input mt-1 w-full"
        />
      </div>

      {/* WhatsApp */}
      <div>
        <label htmlFor="whatsapp" className="block font-medium">
          WhatsApp (opcional)
        </label>
        <input
          id="whatsapp"
          type="tel"
          placeholder="+34123456789"
          {...register('whatsapp')}
          className="input mt-1 w-full"
        />
      </div>

      {/* Botón Siguiente */}
      <button
        type="submit"
        className="btn-primary w-full py-2 mt-4"
      >
        Siguiente
      </button>
    </form>
  );
}
