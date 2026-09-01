/* eslint-disable no-console */
// src/pages/UploadCVPage.tsx
import React, { useState } from 'react';
import { useDispatch } from 'react-redux';
import { Link, useNavigate } from 'react-router-dom';
import { saveCV, generateFinalReport } from '../features/personal/personalSlice';
import { useAppSelector } from '../app/hooks';
import type { RootState } from '../app/store';

export default function UploadCVPage() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const [file, setFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const cvFile = useAppSelector((state: RootState) => state.personal.cvFile);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setError(null);
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      
      if (!selectedFile.type.includes('pdf')) {
        setError('Por favor, selecciona un archivo PDF válido.');
        return;
      }
      if (selectedFile.size > 10 * 1024 * 1024) {
        setError('El archivo es demasiado grande. Máximo 10MB.');
        return;
      }
      setFile(selectedFile);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setIsLoading(true);
    setError(null);

    try {
      const toBase64 = (file: File) => new Promise<string>((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result as string);
        reader.onerror = error => reject(error);
      });

      const fileContent = await toBase64(file);
      // Guardamos en estado local. La evaluación IA se hará de forma unificada en ResultadosPage (SSE)
      dispatch(saveCV({ fileName: file.name, fileContent }));
      
      dispatch(generateFinalReport());
      navigate('/resultados');

    } catch (err: any) {
      setError(err.message || 'Error al procesar el archivo en el navegador.');
    } finally {
      setIsLoading(false);
    }
  };

  if (cvFile) {
    return (
      <div className="p-6 max-w-3xl mx-auto">
        <h1 className="text-2xl font-bold mb-4">Tu CV</h1>
        <p className="mb-4">Documento preparado: <strong>{cvFile.fileName}</strong></p>

        <object data={cvFile.fileContent} type="application/pdf" width="100%" height="600px" title="Previsualización de tu currículum">
          <p>Tu navegador no soporta la previsualización de archivos PDF.</p>
        </object>

        <div className="mt-6 flex gap-4">
          <Link to="/games" className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 transition-colors focus:ring-4 focus:ring-blue-300 outline-none">
            Volver a juegos
          </Link>
          <button
            onClick={() => navigate('/resultados')}
            className="bg-green-600 text-white px-6 py-2 rounded hover:bg-green-700 transition-colors focus:ring-4 focus:ring-green-300 outline-none"
          >
            Generar Informe IA
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-md mx-auto">
      <h1 className="text-2xl font-bold mb-4">Sube tu CV</h1>
      <p className="mb-6">Adjunta tu CV en formato PDF para iniciar el análisis.</p>

      {error && (
        <div role="alert" className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded font-medium">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4" noValidate>
        <div>
          <label htmlFor="cv-upload" className="block text-sm font-medium text-gray-700 mb-1">
            Seleccionar archivo PDF
          </label>
          <input
            id="cv-upload" type="file" accept=".pdf" onChange={handleChange} disabled={isLoading} aria-busy={isLoading}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-violet-50 file:text-violet-700 hover:file:bg-violet-100 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-violet-600 focus:border-transparent"
          />
        </div>

        <button
          type="submit" disabled={!file || isLoading} aria-live="polite"
          className="w-full bg-blue-600 text-white px-6 py-2 rounded disabled:opacity-50 flex items-center justify-center transition-colors hover:bg-blue-700 focus:outline-none focus:ring-4 focus:ring-blue-300"
        >
          {isLoading ? 'Preparando documento...' : 'Subir y continuar'}
        </button>
      </form>
    </div>
  );
}