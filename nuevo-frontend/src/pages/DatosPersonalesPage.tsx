// src/pages/DatosPersonalesPage.tsx
import React from "react";
import logo from "../assets/Logo_teamworkz.png";
import { useForm, SubmitHandler } from 'react-hook-form';
import { useAppDispatch, useAppSelector } from '../app/hooks';
import { saveContact } from '../features/personal/personalSlice';
import { useNavigate, Link } from 'react-router-dom';
import ProgressBar from '../components/ProgressBar';

type ContactForm = {
  firstName: string;
  lastName: string;
  email: string;
  whatsapp: string;
  dataConsent: boolean;
};

const DatosPersonalesPage: React.FC = () => {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const current = useAppSelector(state => state.personal);

  const { register, handleSubmit, formState: { errors } } = useForm<ContactForm>({
    defaultValues: {
      firstName: current.firstName,
      lastName:  current.lastName,
      email:     current.email,
      whatsapp:  current.whatsapp,
      dataConsent: false,
    }
  });

  const onSubmit: SubmitHandler<ContactForm> = (data) => {
    if (!data.email.trim() && !data.whatsapp.trim()) {
      alert('Debes indicar email o WhatsApp.');
      return;
    }
    // Persist the dataConsent flag so we don't need to ask again
    dispatch(saveContact({
      firstName: data.firstName,
      lastName: data.lastName,
      email: data.email,
      whatsapp: data.whatsapp,
      dataConsent: data.dataConsent,
    }));
    navigate('/register/preferences');
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center p-4 transition-colors">
      <form onSubmit={handleSubmit(onSubmit)} className="max-w-md w-full bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 space-y-6 relative z-10 transition-colors" noValidate>
        
        <div className="flex justify-center">
          <img src={logo} alt="Teamworkz" className="h-16" />
        </div>

        <ProgressBar current={1} total={2} />

        <h1 className="text-2xl font-bold text-center dark:text-gray-100">
          Paso 1 de 2 – Datos de contacto
        </h1>

        <div>
          <label htmlFor="firstName" className="block font-medium dark:text-gray-200">
            Nombre
          </label>
          <input
            id="firstName"
            type="text"
            placeholder="Ej. Juan"
            {...register('firstName', { required: 'El nombre es obligatorio' })}
            className={`input mt-1 w-full dark:bg-gray-700 dark:border-gray-600 dark:text-white ${errors.firstName ? 'border-red-500' : ''}`}
            aria-invalid={errors.firstName ? "true" : "false"}
            aria-describedby={errors.firstName ? "firstName-error" : undefined}
          />
          {errors.firstName && (
            <p id="firstName-error" className="text-red-600 dark:text-red-400 mt-1 text-sm font-medium" aria-live="assertive">{errors.firstName.message}</p>
          )}
        </div>

        <div>
          <label htmlFor="lastName" className="block font-medium dark:text-gray-200">
            Apellidos
          </label>
          <input
            id="lastName"
            type="text"
            placeholder="Ej. García Pérez"
            {...register('lastName', { required: 'Los apellidos son obligatorios' })}
            className={`input mt-1 w-full dark:bg-gray-700 dark:border-gray-600 dark:text-white ${errors.lastName ? 'border-red-500' : ''}`}
            aria-invalid={errors.lastName ? "true" : "false"}
            aria-describedby={errors.lastName ? "lastName-error" : undefined}
          />
          {errors.lastName && (
            <p id="lastName-error" className="text-red-600 dark:text-red-400 mt-1 text-sm font-medium" aria-live="assertive">{errors.lastName.message}</p>
          )}
        </div>

        <div>
          <label htmlFor="email" className="block font-medium dark:text-gray-200">
            Email (opcional)
          </label>
          <input
            id="email"
            type="email"
            placeholder="juan@example.com"
            {...register('email')}
            className="input mt-1 w-full dark:bg-gray-700 dark:border-gray-600 dark:text-white"
          />
        </div>

        <div>
          <label htmlFor="whatsapp" className="block font-medium dark:text-gray-200">
            WhatsApp (opcional)
          </label>
          <input
            id="whatsapp"
            type="tel"
            placeholder="+34123456789"
            {...register('whatsapp')}
            className="input mt-1 w-full dark:bg-gray-700 dark:border-gray-600 dark:text-white"
          />
        </div>

        <div className="flex items-start mt-2">
          <input
            id="dataConsent"
            type="checkbox"
            {...register('dataConsent', { required: 'Debes aceptar la política de privacidad.' })}
            className="mt-1 mr-2 w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 dark:bg-gray-700 dark:border-gray-600"
            aria-invalid={errors.dataConsent ? "true" : "false"}
            aria-describedby={errors.dataConsent ? "dataConsent-error" : undefined}
          />
          <label htmlFor="dataConsent" className="text-sm select-none dark:text-gray-300">
            He leído y acepto la{' '}
            <Link
              to="/privacidad"
              className="text-blue-600 dark:text-blue-400 underline hover:text-blue-800 dark:hover:text-blue-300 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded"
            >
              política de privacidad y el uso de mis datos personales
            </Link>.
          </label>
        </div>
        {errors.dataConsent && (
          <p id="dataConsent-error" className="text-red-600 dark:text-red-400 text-xs font-bold mt-1" aria-live="assertive">{errors.dataConsent.message}</p>
        )}

        <button
          type="submit"
          className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 mt-6 text-lg font-semibold rounded transition-colors focus:outline-none focus:ring-4 focus:ring-blue-300"
        >
          Siguiente
        </button>
      </form>
    </div>
  );
}

export default DatosPersonalesPage;