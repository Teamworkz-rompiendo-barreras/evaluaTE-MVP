// src/pages/UploadCVPage.tsx
import React, { useState } from 'react'
import { useAppDispatch } from '../app/hooks'
import { saveCvAnalysis, type CvAnalysis } from '../features/personal/personalSlice'
import { useNavigate } from 'react-router-dom'

export default function UploadCVPage() {
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const dispatch = useAppDispatch()
  const navigate = useNavigate()

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setError(null)
    if (e.target.files?.[0]) {
      setFile(e.target.files[0])
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) return

    setLoading(true)
    setError(null)

    try {
      const form = new FormData()
      form.append('cv', file)

      const resp = await fetch('/api/upload-cv', {
        method: 'POST',
        body: form,
      })

      if (!resp.ok) {
        throw new Error(`Error en el servidor: ${resp.status}`)
      }

      // Aseguramos tipado
      const analysis = (await resp.json()) as CvAnalysis

      dispatch(saveCvAnalysis(analysis))
      navigate('/resultados')
    } catch (err: any) {
      console.error(err)
      setError('No se pudo analizar tu CV. Por favor, inténtalo de nuevo.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="max-w-md mx-auto p-6 space-y-4"
      aria-busy={loading}
    >
      <h1 className="text-2xl font-bold">Sube tu CV</h1>

      <input
        type="file"
        accept=".pdf"
        onChange={handleChange}
        disabled={loading}
        aria-label="Selecciona tu CV en PDF"
      />

      {error && (
        <p role="alert" className="text-red-600">
          {error}
        </p>
      )}

      <button
        type="submit"
        disabled={!file || loading}
        className="btn-primary mt-4 w-full disabled:opacity-50"
      >
        {loading ? 'Analizando…' : 'Analizar CV'}
      </button>
    </form>
  )
}
