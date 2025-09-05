/* eslint-disable no-console */
// src/pages/UploadCVPage.tsx
import React, { useState } from 'react';
import { useDispatch } from 'react-redux';
import { Link, useNavigate } from 'react-router-dom';
import { saveCV, saveCvAnalysis, generateFinalReport } from '../features/personal/personalSlice';
import { useAppSelector } from '../app/hooks';
import type { RootState } from '../app/store';
import { buildApiUrl, API_CONFIG } from '../config/api';

interface CvAnalysis {
  feedback: string;
  strengths?: string[];
  skills?: string[];
  weaknesses?: string[];
  structure?: string;
  coherence?: string;
  experience?: string;
  education?: string[];
  alerts?: string[];
}

export default function UploadCVPage() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const [file, setFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const cvFile = useAppSelector((state: RootState) => state.personal.cvFile);
  const cvAnalysis = useAppSelector((state: RootState) => state.personal.cvAnalysis) as CvAnalysis | null;

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setError(null) // Limpiar errores anteriores
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0]
      
      // Validar tipo de archivo
      if (!selectedFile.type.includes('pdf')) {
        setError('Por favor, selecciona un archivo PDF válido.')
        return
      }
      
      // Validar tamaño (máximo 10MB)
      if (selectedFile.size > 10 * 1024 * 1024) {
        setError('El archivo es demasiado grande. Máximo 10MB.')
        return
      }
      
      setFile(selectedFile)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) return

    setIsLoading(true)
    setError(null)

    try {
      // Leer el archivo como base64 para la preview
      const toBase64 = (file: File) => new Promise<string>((resolve, reject) => {
        const reader = new FileReader()
        reader.readAsDataURL(file)
        reader.onload = () => resolve(reader.result as string)
        reader.onerror = error => reject(error)
      })

      const fileContent = await toBase64(file)
      dispatch(saveCV({ fileName: file.name, fileContent }))

      // Enviar el archivo al backend para análisis real
      const formData = new FormData();
      formData.append('file', file);
      formData.append('userId', 'user-ester-2025');
      formData.append('fullName', 'Ester Pérez Ribada');
      formData.append('softSkills', JSON.stringify([]));
      formData.append('jobPreferences', JSON.stringify({}));
      formData.append('completedGames', JSON.stringify([]));
      
      // Enviando CV para análisis...
      const res = await fetch(buildApiUrl(API_CONFIG.ENDPOINTS.PDF_ANALYZE), {
        method: 'POST',
        body: formData
      });
      
              // Respuesta del servidor recibida
      
      if (res.ok) {
        const cvAnalysis = await res.json();
                  // Análisis de CV recibido exitosamente
        
        // Verificar que el análisis tiene la estructura esperada
        if (!cvAnalysis || typeof cvAnalysis !== 'object') {
          // console.error('❌ Análisis de CV inválido:', cvAnalysis);
          throw new Error('El servidor devolvió un análisis de CV inválido');
        }
        
        // DEBUG: Log del análisis recibido
        if (import.meta.env.DEV) {
          console.log('🔍 DEBUG - Análisis de CV recibido del backend:', cvAnalysis);
        }
        
        // Guardar el análisis en el estado de Redux
        dispatch(saveCvAnalysis(cvAnalysis));
        
        if (import.meta.env.DEV) {
          console.log('🔍 DEBUG - Análisis de CV guardado en Redux');
        }
        
        // Verificar que se guardó correctamente
        if (cvAnalysis && (cvAnalysis.strengths?.length > 0 || cvAnalysis.skills?.length > 0 || cvAnalysis.weaknesses?.length > 0)) {
          if (import.meta.env.DEV) {
            console.log('🔍 DEBUG - CV analizado con datos reales');
          }
          // CV analizado con datos reales
        } else {
          if (import.meta.env.DEV) {
            console.log('🔍 DEBUG - CV analizado pero sin datos significativos');
          }
          // CV analizado pero sin datos significativos
        }
      } else {
        const errorData = await res.json().catch(() => ({}));
                  // Error del servidor en análisis de CV
        
        // Crear un análisis básico con información del error
        const fallbackAnalysis = {
          strengths: [],
          weaknesses: [],
          feedback: errorData.detail || errorData.error || 'No se pudo analizar completamente el CV',
          structure: 'regular',
          coherence: 'regular',
          experience: 'regular',
          skills: [],
          education: [],
          alerts: [errorData.detail || errorData.error || 'Error en el análisis del CV']
        };
        
        dispatch(saveCvAnalysis(fallbackAnalysis));
                  // Usando análisis de fallback
        
        // Mostrar error específico al usuario
        if (errorData.detail) {
          setError(`Error en el análisis del CV: ${errorData.detail}`);
        } else {
          setError('Error al procesar el CV. Por favor, verifica que el archivo sea un PDF válido.');
        }
      }
    } catch (err) {
              // Error de conexión en análisis de CV
      // No mostrar error al usuario si es un error de conexión con Azure OpenAI
      // ya que esto es normal cuando no está configurado
      if (err instanceof Error && err.message?.includes('Azure OpenAI no configurado')) {
        // Azure OpenAI no configurado, usando análisis básico
      } else {
        setError('Error de conexión. Por favor, verifica tu conexión a internet e inténtalo de nuevo.');
      }
      
      // Crear un análisis básico para errores de conexión
      dispatch(saveCvAnalysis({
        feedback: 'No se pudo conectar con el servidor para analizar el CV',
        strengths: [],
        skills: [],
        weaknesses: [],
        structure: 'regular',
        coherence: 'regular',
        experience: 'regular',
        education: [],
        alerts: ['Error de conexión al analizar el CV']
      }));
      
      setIsLoading(false)
      return
    }

    // Generar reporte final después de subir el CV
    // Generando reporte final...
    dispatch(generateFinalReport())
    navigate('/resultados')
  }

  // Si ya hay un CV subido, mostramos preview
  if (cvFile) {
    return (
      <div className="p-6 max-w-3xl mx-auto">
        <h1 className="text-2xl font-bold mb-4">Tu CV</h1>
        <p className="mb-4">Ya has subido un CV: {cvFile.fileName}</p>

        {/* Mostrar información del análisis si está disponible */}
        {cvAnalysis && (
          <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded">
            <h3 className="font-semibold text-blue-800 mb-2">Análisis del CV:</h3>
            <p className="text-blue-700">{cvAnalysis.feedback}</p>
            {cvAnalysis.strengths && cvAnalysis.strengths.length > 0 && (
              <div className="mt-2">
                <strong className="text-green-700">Fortalezas:</strong>
                <ul className="list-disc list-inside text-green-600">
                  {(Array.isArray(cvAnalysis.strengths) ? cvAnalysis.strengths : []).map((strength: string, index: number) => (
                    <li key={index}>{strength}</li>
                  ))}
                </ul>
              </div>
            )}
            {cvAnalysis.skills && cvAnalysis.skills.length > 0 && (
              <div className="mt-2">
                <strong className="text-purple-700">Habilidades detectadas:</strong>
                <ul className="list-disc list-inside text-purple-600">
                  {(Array.isArray(cvAnalysis.skills) ? cvAnalysis.skills : []).map((skill: string, index: number) => (
                    <li key={index}>{skill}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

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

      {/* Mostrar mensaje de error */}
      {error && (
        <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="file"
          accept=".pdf"
          onChange={handleChange}
          disabled={isLoading}
          className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-violet-50 file:text-violet-700 hover:file:bg-violet-100 disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={!file || isLoading}
          className="bg-blue-600 text-white px-6 py-2 rounded disabled:opacity-50 flex items-center justify-center"
        >
          {isLoading ? (
            <>
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Analizando CV...
            </>
          ) : (
            'Subir y continuar'
          )}
        </button>
      </form>
    </div>
  )
}