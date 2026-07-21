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

  const { register, handleSubmit, setError, formState: { errors } } = useForm<ContactForm>({
    defaultValues: {
      firstName: current.firstName,
      lastName:  current.lastName,
      email:     current.email,
      whatsapp:  current.whatsapp,
      dataConsent: false,
    }
  });

  const onSubmit: SubmitHandler<ContactForm> = (data) => {
    // 1. Validación unificada y accesible (Sin alerts)
    if (!data.email.trim() && !data.whatsapp.trim()) {
      setError('root.serverError', { 
        type: 'manual', 
        message: 'Por favor, indícanos un email o número de WhatsApp para poder contactarte.' 
      });
      return;
    }

    // 2. Guardamos el timestamp del consentimiento para auditoría RGPD
    const contactData = {
      ...data,
      consentTimestamp: new Date().toISOString(),
      consentVersion: 'v1.0'
    };

    dispatch(saveContact(contactData));
    navigate('/register/preferences');
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center p-4 transition-colors">
      <form onSubmit={handleSubmit(onSubmit)} className="max-w-md w-full bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 space-y-6 relative z-10 transition-colors">
        
        <div className="flex justify-center">
          <img src={logo} alt="Logotipo de Teamworkz" className="h-16" />
        </div>

        <ProgressBar current={1} total={2} />

        <h1 className="text-2xl font-bold text-center dark:text-gray-100">
          Paso 1 de 2 – Datos de contacto
        </h1>

        {/* Mensaje de error general accesible */}
        {errors.root?.['serverError'] && (
          <div role="alert" aria-live="assertive" className="p-4 mb-4 text-sm text-red-800 rounded-lg bg-red-50 dark:bg-red-900/30 dark:text-red-400">
            {errors.root['serverError']?.message}
          </div>
        )}

        <div>
          <label htmlFor="firstName" className="block font-medium dark:text-gray-200">
            Nombre
          </label>
          <input
            id="firstName"
            type="text"
            placeholder="Ej. Juan"
            aria-invalid={errors.firstName ? "true" : "false"}
            {...register('firstName', { required: 'El nombre es obligatorio' })}
            className="input mt-1 w-full bg-gray-700 text-white placeholder-gray-400 border-gray-600 focus:ring-blue-500 focus:border-blue-500"
          />
          {errors.firstName && (
            <p role="alert" className="text-red-600 dark:text-red-400 text-sm mt-1">{errors.firstName.message}</p>
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
            aria-invalid={errors.lastName ? "true" : "false"}
            {...register('lastName', { required: 'Los apellidos son obligatorios' })}
            className="input mt-1 w-full bg-gray-700 text-white placeholder-gray-400 border-gray-600 focus:ring-blue-500 focus:border-blue-500"
          />
          {errors.lastName && (
            <p role="alert" className="text-red-600 dark:text-red-400 text-sm mt-1">{errors.lastName.message}</p>
          )}
        </div>

        <div>
          <label htmlFor="email" className="block font-medium dark:text-gray-200">
            Email (opcional)
          </label>
          <input
            id="email"
            type="email"
            placeholder="juan@ejemplo.com"
            {...register('email')}
            className="input mt-1 w-full bg-gray-700 text-white placeholder-gray-400 border-gray-600 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <div>
          <label htmlFor="whatsapp" className="block font-medium dark:text-gray-200">
            WhatsApp (opcional)
          </label>
          <input
            id="whatsapp"
            type="tel"
            placeholder="+34 600 00 00 00"
            {...register('whatsapp')}
            className="input mt-1 w-full bg-gray-700 text-white placeholder-gray-400 border-gray-600 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <div className="flex items-start mt-4">
          <input
            id="dataConsent"
            type="checkbox"
            aria-invalid={errors.dataConsent ? "true" : "false"}
            {...register('dataConsent', { required: 'Debes aceptar la política de privacidad para continuar.' })}
            className="mt-1 mr-3 w-5 h-5 text-blue-600 rounded border-gray-300 focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 dark:bg-gray-700 dark:border-gray-600"
          />
          <label htmlFor="dataConsent" className="text-sm dark:text-gray-300">
            He leído y acepto la{' '}
            <Link to="/privacidad" className="text-blue-600 dark:text-blue-400 underline hover:text-blue-800">
              política de privacidad y el uso de mis datos
            </Link>.
          </label>
        </div>
        {errors.dataConsent && (
          <p role="alert" className="text-red-600 dark:text-red-400 text-sm mt-1">{errors.dataConsent.message}</p>
        )}

        <button
          type="submit"
          className="w-full py-3 mt-6 text-lg font-semibold text-white bg-blue-600 rounded-lg hover:bg-blue-700 focus:ring-4 focus:outline-none focus:ring-blue-300 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800"
        >
          Siguiente
        </button>
      </form>
    </div>
  );
}

export default DatosPersonalesPage;