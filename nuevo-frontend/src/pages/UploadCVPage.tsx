// src/pages/UploadCVPage.tsx
import React, { useState, useEffect } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { useNavigate, Link } from 'react-router-dom'
import { saveCV } from '../features/progress/progressSlice' // Ajusta import si tu slice se llama distinto

export default function UploadCVPage() {
  const dispatch = useDispatch()
  const navigate = useNavigate()

  // Selector: posible CV ya subido
  const existingCV: File | null = useSelector(
    (state: any) => state.progress.cvFile || null
  )

  const [file, setFile] = useState<File | null>(null)

  // Si ya hay CV, redirige automáticamente a preview
  useEffect(() => {
    if (existingCV) {
      // No navega automáticamente, dejamos al usuario revisar
    }
  }, [existingCV])

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) return
    // Guarda en Redux
    dispatch(saveCV(file))
    // Avanza a preferencias
    navigate('/preferences')
  }

  // Si ya existe CV, mostramos preview + botón
  if (existingCV) {
    return (
      <div className="p-4">
        <h1 className="text-2xl font-bold mb-4">Tu CV</h1>
        <p className="mb-4">Ya has subido un CV. Puedes revisarlo aquí:</p>
        <object
          data={URL.createObjectURL(existingCV)}
          type="application/pdf"
          width="100%"
          height="600px"
        >
          <p>Tu navegador no soporta previsualizar PDFs.</p>
        </object>
        <Link
          to="/preferences"
          className="mt-6 inline-block bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700"
        >
          Siguiente: preferencias laborales
        </Link>
      </div>
    )
  }

  // Si no hay CV, mostramos formulario de subida
  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Sube tu CV</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="file"
          accept=".pdf,.doc,.docx"
          onChange={handleChange}
          className="block"
        />
        <button
          type="submit"
          disabled={!file}
          className="bg-blue-600 text-white px-6 py-2 rounded-lg disabled:opacity-50"
        >
          Subir y continuar
        </button>
      </form>
    </div>
  )
}
