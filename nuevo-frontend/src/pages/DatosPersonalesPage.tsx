import { useState } from "react";
import { useForm } from 'react-hook-form'
import { useAppDispatch, useAppSelector } from '../app/hooks'
import { saveContact } from '../features/personal/personalSlice'
import { useNavigate } from 'react-router-dom'
import ProgressBar from '../components/ProgressBar'
import logo from "../assets/Logo_teamworkz.png";   // ← import explícito

export default function DatosPersonalesPage() {
  const [nombre, setNombre] = useState("");
  const [apellido, setApellido] = useState("");
  const navigate = useNavigate();

  return (
    <main className="flex flex-col items-center p-6 gap-4 min-h-screen">
      <img src={logo} alt="Logo EvalúaTE" className="w-48" />

      <h1 className="text-2xl font-bold">Datos personales</h1>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          navigate("/games");
        }}
        className="flex flex-col gap-4 w-full max-w-md"
      >
        <label className="flex flex-col">
          Nombre
          <input
            type="text"
            required
            value={nombre}
            onChange={(e) => setNombre(e.target.value)}
            className="border p-2 rounded"
          />
        </label>

        <label className="flex flex-col">
          Apellido
          <input
            type="text"
            required
            value={apellido}
            onChange={(e) => setApellido(e.target.value)}
            className="border p-2 rounded"
          />
        </label>

        <button type="submit" className="bg-blue-600 text-white p-2 rounded">
          Ir a evaluación de soft skills
        </button>
      </form>
    </main>
  );
}
