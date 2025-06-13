// src/pages/UploadCVPage.tsx
import React, { useState } from 'react'
import { useAppDispatch } from '../app/hooks'
import { saveCvAnalysis } from '../features/personal/personalSlice'
import { useNavigate } from 'react-router-dom'

export default function UploadCVPage() {
  const [file, setFile] = useState<File|null>(null)
  const dispatch = useAppDispatch()
  const navigate = useNavigate()

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) setFile(e.target.files[0])
  }
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) return
    // Lógica de envío a tu backend / Azure Cognitive Services
    const form = new FormData()
    form.append('cv', file)
    const resp = await fetch('/api/upload-cv', { method: 'POST', body: form })
    const analysis = await resp.json()
    dispatch(saveCvAnalysis(analysis))
    navigate('/resultados')
  }

  return (
    <form onSubmit={handleSubmit} className="max-w-md mx-auto p-6 space-y-4">
      <h1 className="text-2xl font-bold">Sube tu CV</h1>
      <input type="file" accept=".pdf" onChange={handleChange} />
      <button
        type="submit"
        disabled={!file}
        className="btn-primary mt-4 w-full"
      >
        Analizar CV
      </button>
    </form>
  )
}

