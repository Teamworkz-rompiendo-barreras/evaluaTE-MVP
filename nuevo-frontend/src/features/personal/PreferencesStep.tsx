import React from "react";
import { useForm, SubmitHandler } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import { useAppDispatch, useAppSelector } from "../../app/hooks";
import { savePreferences } from "./personalSlice";
import { markGameComplete } from "../../features/progress/progressSlice";
import ProgressBar from "../../components/ProgressBar";

// Tipos para los datos del formulario
type PrefData = {
  jobPreferences: string;
  workMode: "remoto" | "presencial" | "híbrido";
  availability: "mañana" | "tarde" | "completa";
  startDate:
    | "inmediata"
    | "15_días"
    | "1_mes"
    | "más_de_1_mes";
  willingToRelocate: boolean;
  hasDisabilityCert: boolean;
};

export default function PreferencesStep() {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();

  // Accedemos al estado actual del personal
  const current = useAppSelector((state) => state.personal);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<PrefData>({
    defaultValues: {
      jobPreferences: current.jobPreferences || "",
      workMode: current.workMode || "presencial",
      availability: current.availability || "completa",
      startDate: current.startDate || "inmediata",
      willingToRelocate: Boolean(current.willingToRelocate),
      hasDisabilityCert: Boolean(current.hasDisabilityCert),
    },
  });

  const onSubmit: SubmitHandler<PrefData> = (data) => {
    if (!data.jobPreferences.trim()) {
      alert("Indica el tipo de trabajo que buscas.");
      return;
    }

    // Guardamos preferencias
    dispatch(savePreferences(data));

    // Marcamos el paso como completado
    dispatch(markGameComplete("preferences"));

    // Navegamos a juegos
    navigate("/games");
  };

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="max-w-md mx-auto p-6 space-y-6 bg-white rounded shadow"
    >
      {/* Barra de progreso */}
      <ProgressBar step={2} total={2} />

      {/* Título */}
      <h2 className="text-2xl font-bold text-center">
        Paso 2 de 2 - Tus preferencias
      </h2>

      {/* Campo: Tipo de trabajo */}
      <div>
        <label htmlFor="jobPreferences" className="block font-medium mb-1">
          ¿Qué tipo de trabajo estás buscando?
        </label>
        <input
          id="jobPreferences"
          type="text"
          placeholder="Ej. Atención al cliente, Recepción, Desarrollo web…"
          {...register("jobPreferences", {
            required: "Campo obligatorio",
          })}
          className="w-full border rounded px-3 py-2"
        />
        {errors.jobPreferences && (
          <p className="text-red-600 mt-1">
            {errors.jobPreferences.message}
          </p>
        )}
      </div>

      {/* Campo: Modalidad */}
      <div>
        <label htmlFor="workMode" className="block font-medium mb-1">
          Modalidad
        </label>
        <select
          id="workMode"
          {...register("workMode", { required: "Elige una opción" })}
          className="w-full border rounded px-3 py-2"
        >
          <option value="remoto">Remoto</option>
          <option value="presencial">Presencial</option>
          <option value="híbrido">Híbrido</option>
        </select>
      </div>

      {/* Campo: Disponibilidad horaria */}
      <div>
        <label htmlFor="availability" className="block font-medium mb-1">
          Disponibilidad horaria
        </label>
        <select
          id="availability"
          {...register("availability", { required: "Elige una opción" })}
          className="w-full border rounded px-3 py-2"
        >
          <option value="mañana">Mañana</option>
          <option value="tarde">Tarde</option>
          <option value="completa">Completa</option>
        </select>
      </div>

      {/* Campo: Incorporación */}
      <div>
        <label htmlFor="startDate" className="block font-medium mb-1">
          Fecha de incorporación
        </label>
        <select
          id="startDate"
          {...register("startDate", { required: "Selecciona una opción" })}
          className="w-full border rounded px-3 py-2"
        >
          <option value="inmediata">Inmediata</option>
          <option value="15_días">En 15 días</option>
          <option value="1_mes">En 1 mes</option>
          <option value="más_de_1_mes">Más de 1 mes</option>
        </select>
      </div>

      {/* Checkbox: Mudanza */}
      <div className="flex items-center space-x-2">
        <input
          id="relocate"
          type="checkbox"
          {...register("willingToRelocate")}
        />
        <label htmlFor="relocate" className="font-medium">
          Estoy dispuesto/a a cambiar de residencia
        </label>
      </div>

      {/* Checkbox: Certificado de discapacidad */}
      <div className="flex items-center space-x-2">
        <input
          id="cert"
          type="checkbox"
          {...register("hasDisabilityCert")}
        />
        <label htmlFor="cert" className="font-medium">
          Tengo certificado de discapacidad
        </label>
      </div>

      {/* Botones de navegación */}
      <div className="flex justify-between pt-4">
        <button
          type="button"
          onClick={() => navigate("/register/contact")}
          className="text-gray-600 hover:text-gray-800 font-medium"
        >
          ← Anterior
        </button>
        <button
          type="submit"
          className="py-2 px-4 bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
        >
          Finalizar
        </button>
      </div>
    </form>
  );
}