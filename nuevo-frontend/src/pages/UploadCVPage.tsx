// src/pages/UploadCVPage.tsx
import React, { useState } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { useNavigate, Link } from 'react-router-dom'

// Importamos las acciones desde personalSlice
import { saveCV, saveCvAnalysis, saveSoftSkills, generateFinalReport } from '../features/personal/personalSlice'

export default function UploadCVPage() {
  const dispatch = useDispatch()
  const navigate = useNavigate()

  // Seleccionamos el archivo del CV desde el estado
  const cvFile = useSelector((state: unknown) => (state as { personal: { cvFile: { fileName: string; fileContent: string } | null } }).personal.cvFile)

  const [file, setFile] = useState<File | null>(null)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) return

    // Leer el archivo como base64
    const toBase64 = (file: File) => new Promise<string>((resolve, reject) => {
      const reader = new FileReader()
      reader.readAsDataURL(file)
      reader.onload = () => resolve(reader.result as string)
      reader.onerror = error => reject(error)
    })

    const fileContent = await toBase64(file)
    dispatch(saveCV({ fileName: file.name, fileContent }))
    
    // Simular análisis del CV (temporal para depuración)
    const mockCvAnalysis = {
      structure: 'bueno',
      coherence: 'bueno',
      experience: 'regular',
      skills: ['JavaScript', 'React', 'TypeScript', 'HTML', 'CSS'],
      education: ['Grado en Informática'],
      alerts: ['Considerar agregar más proyectos personales']
    }
    
    dispatch(saveCvAnalysis(mockCvAnalysis))
    
    // Simular soft skills evaluadas (temporal para depuración)
    const mockSoftSkills = [
      {
        skill: 'Toma de decisiones',
        level: 'alto' as const,
        score: 85,
        confidence: 0.85,
        feedback: 'Excelente capacidad para tomar decisiones informadas',
        interactions: []
      },
      {
        skill: 'Pensamiento analítico',
        level: 'medio' as const,
        score: 65,
        confidence: 0.65,
        feedback: 'Buen pensamiento analítico, con espacio para mejorar',
        interactions: []
      },
      {
        skill: 'Creatividad',
        level: 'alto' as const,
        score: 90,
        confidence: 0.90,
        feedback: 'Muy creativo/a en la resolución de problemas',
        interactions: []
      },
      {
        skill: 'Trabajo en equipo',
        level: 'medio' as const,
        score: 70,
        confidence: 0.70,
        feedback: 'Buen trabajo en equipo, mejora en comunicación',
        interactions: []
      },
      {
        skill: 'Curiosidad y aprendizaje',
        level: 'alto' as const,
        score: 88,
        confidence: 0.88,
        feedback: 'Excelente disposición para aprender',
        interactions: []
      },
      {
        skill: 'Resiliencia y flexibilidad',
        level: 'medio' as const,
        score: 60,
        confidence: 0.60,
        feedback: 'Buena adaptabilidad, puede mejorar bajo presión',
        interactions: []
      },
      {
        skill: 'Autoconciencia',
        level: 'alto' as const,
        score: 82,
        confidence: 0.82,
        feedback: 'Excelente autoconciencia y reflexión',
        interactions: []
      },
      {
        skill: 'Empatía',
        level: 'medio' as const,
        score: 75,
        confidence: 0.75,
        feedback: 'Buena empatía, puede mejorar en situaciones difíciles',
        interactions: []
      },
      {
        skill: 'Comunicación',
        level: 'medio' as const,
        score: 68,
        confidence: 0.68,
        feedback: 'Comunicación clara, mejora en presentaciones',
        interactions: []
      },
      {
        skill: 'Gestión del tiempo',
        level: 'bajo' as const,
        score: 45,
        confidence: 0.45,
        feedback: 'Necesita mejorar la gestión del tiempo',
        interactions: []
      }
    ]
    
    dispatch(saveSoftSkills(mockSoftSkills))
    
    // Generar reporte final después de subir el CV
    dispatch(generateFinalReport())
    
    navigate('/resultados')
  }

  // Si ya hay un CV subido, mostramos preview
  if (cvFile) {
    return (
      <div className="p-6 max-w-3xl mx-auto">
        <h1 className="text-2xl font-bold mb-4">Tu CV</h1>
        <p className="mb-4">Ya has subido un CV: {cvFile.fileName}</p>

        {/* Vista previa del PDF */}
        <object data={cvFile.fileContent} type="application/pdf" width="100%" height="600px">
          <p>Tu navegador no soporta previsualización de PDFs.</p>
        </object>

        {/* Botones de acción */}
        <div className="mt-6 flex gap-4">
          <Link to="/games" className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700">
            Volver a juegos
          </Link>
          <button
            onClick={() => {
              // Generar reporte si no existe
              if (!cvFile) {
                dispatch(generateFinalReport())
              }
              navigate('/resultados')
            }}
            className="bg-green-600 text-white px-6 py-2 rounded hover:bg-green-700"
          >
            Ver informe completo
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 max-w-md mx-auto">
      <h1 className="text-2xl font-bold mb-4">Sube tu CV</h1>
      <p className="mb-6">Adjunta tu CV en formato PDF para generar tu informe final.</p>

      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="file"
          accept=".pdf,.doc,.docx"
          onChange={handleChange}
          className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-violet-50 file:text-violet-700 hover:file:bg-violet-100"
        />
        <button
          type="submit"
          disabled={!file}
          className="bg-blue-600 text-white px-6 py-2 rounded disabled:opacity-50"
        >
          Subir y continuar
        </button>
      </form>
    </div>
  )
}