/* eslint-disable no-console */
// src/pages/UploadCVPage.tsx
import React, { useState } from 'react';
import { useDispatch } from 'react-redux';
import { Link, useNavigate } from 'react-router-dom';
import { saveCV, saveCvAnalysis } from '../features/personal/personalSlice';
import { useAppSelector } from '../app/hooks';
import type { RootState } from '../app/store';
import { buildApiUrl, API_CONFIG } from '../config/api';
import type { CvAnalysis } from '@/types/report';

export default function UploadCVPage() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const [file, setFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const cvFile = useAppSelector((state: RootState) => state.personal.cvFile);
  const cvAnalysis = useAppSelector((state: RootState) => state.personal.cvAnalysis)
  const gameData = useAppSelector((state: RootState) => state.game);
  const personalData = useAppSelector((state: RootState) => state.personal);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setError(null);
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      
      const validTypes = [
        'application/pdf', 
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/msword',
        'image/jpeg', 
        'image/png'
      ];
      const validExtensions = /\.(pdf|docx?|jpe?g|png)$/i;

      if (!validTypes.includes(selectedFile.type) && !validExtensions.test(selectedFile.name)) {
        setError('Formato no válido. Por favor, sube un PDF, documento de Word (DOCX) o Imagen (JPG/PNG).');
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
    if (!file || isLoading) return;

    setIsLoading(true);
    setError(null);

    try {
      const fileUrl = URL.createObjectURL(file);
      dispatch(saveCV({ fileName: file.name, fileContent: fileUrl }));

      const formData = new FormData();
      formData.append('cv_file', file);
      formData.append('game_results', JSON.stringify({
        completedGames: gameData.completedGames || [],
        softSkills: gameData.softSkills || []
      }));
      
      const fullName = `${personalData.firstName || ''} ${personalData.lastName || ''}`.trim();
      formData.append('preferences', JSON.stringify({
        jobPreferences: personalData.jobPreferences || {},
        workMode: personalData.workMode || '',
        availability: personalData.availability || '',
        willingToRelocate: personalData.willingToRelocate || false,
        fullName: fullName,
        email: personalData.email || '',
        phone: personalData.whatsapp || '',
        hasDisabilityCert: personalData.hasDisabilityCert || false
      }));

      const res = await fetch(buildApiUrl(API_CONFIG.ENDPOINTS.PDF_ANALYZE), {
        method: 'POST',
        body: formData
      });

      if (res.ok) {
        const analysisResult = await res.json();
        if (!analysisResult || typeof analysisResult !== 'object') {
          throw new Error('El servidor devolvió un análisis de CV inválido');
        }
        dispatch(saveCvAnalysis(analysisResult.cv_analysis || analysisResult));
        navigate('/resultados', { state: { rawReport: analysisResult } });
      } else {
        const errorData = await res.json().catch(() => ({}));
        const fallbackAnalysis: CvAnalysis = {
          structure_score: 0, coherence_score: 0, key_info_score: 0, clarity_score: 0, style_score: 0,
          evidence: {
            structure: errorData.detail || errorData.error || 'No se pudo analizar correctamente el CV.',
            coherence: '', key_info: '', clarity: '', style: ''
          },
          corrections: [], reordering_suggestions: [],
        };
        dispatch(saveCvAnalysis(fallbackAnalysis));
        
        if (errorData.detail) {
          setError(`Error en el análisis del CV: ${errorData.detail}`);
        } else {
          setError('Error al procesar el CV. Por favor, verifica que el archivo sea un formato soportado y no esté dañado.');
        }
        setIsLoading(false);
      }
    } catch (err) {
      setError('Error de conexión. Por favor, verifica tu conexión a internet e inténtalo de nuevo.');
      setIsLoading(false);
    }
  };

  if (cvFile) {
    return (
      <div className="p-6 max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold mb-4 text-gray-900 dark:text-white">Tu CV</h1>
        <p className="mb-4 text-gray-700 dark:text-gray-300">Ya has subido un documento: <span className="font-semibold">{cvFile.fileName}</span></p>
        
        {cvAnalysis && (
          <div className="mb-6 p-5 bg-blue-50 dark:bg-blue-900/30 border-l-4 border-blue-600 dark:border-blue-400 rounded-r-lg shadow-sm">
            <h3 className="font-bold text-blue-900 dark:text-blue-100 mb-2">Análisis Técnico Inicial:</h3>
            <ul className="list-disc list-inside text-blue-800 dark:text-blue-200 space-y-1">
              <li>Estructura: {cvAnalysis.structure_score}/5</li>
              <li>Coherencia: {cvAnalysis.coherence_score}/5</li>
              <li>Información clave: {cvAnalysis.key_info_score}/5</li>
              <li>Claridad: {cvAnalysis.clarity_score}/5</li>
              <li>Estilo: {cvAnalysis.style_score}/5</li>
            </ul>
          </div>
        )}

        {cvFile.fileName?.toLowerCase().endsWith('.pdf') ? (
            <object data={cvFile.fileContent} type="application/pdf" width="100%" height="500px" className="border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm" aria-label="Previsualización de tu currículum en PDF">
              <p className="text-gray-800 dark:text-white p-4">Tu navegador no soporta previsualización de PDFs. <a href={cvFile.fileContent} download={cvFile.fileName} className="text-blue-700 dark:text-blue-400 underline font-semibold focus:ring-2 focus:ring-blue-500">Descárgalo aquí</a>.</p>
            </object>
        ) : (
            <div className="flex flex-col items-center justify-center p-16 border-2 border-dashed border-gray-400 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-800">
                <span className="text-5xl mb-4" aria-hidden="true">📄</span>
                <p className="text-gray-700 dark:text-gray-200 text-center font-medium">Previsualización no disponible para este formato.<br/>El documento fue procesado correctamente.</p>
            </div>
        )}

        <div className="mt-8 flex flex-col sm:flex-row gap-4">
          <Link to="/games" className="w-full sm:w-auto text-center bg-gray-200 text-gray-800 dark:bg-gray-700 dark:text-gray-200 font-semibold px-6 py-3 rounded-lg shadow-sm hover:bg-gray-300 dark:hover:bg-gray-600 focus:outline-none focus:ring-4 focus:ring-gray-400 transition-colors">
            Volver a juegos
          </Link>
          <button
            onClick={() => navigate('/resultados')}
            className="w-full sm:w-auto bg-[#374BA6] text-white font-bold px-8 py-3 rounded-lg shadow-md hover:bg-[#2d3f96] focus:outline-none focus:ring-4 focus:ring-blue-300 dark:focus:ring-blue-800 transition-colors"
          >
            Ver informe completo →
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-lg mx-auto">
      <h1 className="text-3xl font-bold mb-4 text-gray-900 dark:text-white">Sube tu CV</h1>
      
      {/* FIX UX: Texto recortado exactamente según directriz */}
      <p className="mb-8 text-gray-700 dark:text-gray-300 leading-relaxed">
        Adjunta tu CV. Aceptamos <strong>PDF, Word (DOCX) o Imagen (JPG/PNG)</strong>.
      </p>

      {error && (
        <div role="alert" aria-live="assertive" className="mb-6 p-4 bg-red-50 dark:bg-red-900/30 text-red-800 dark:text-red-200 border-l-4 border-red-500 rounded-r-lg font-medium shadow-sm">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="relative group">
          <input
            id="cv-upload"
            type="file"
            accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
            onChange={handleChange}
            className="sr-only"
            aria-invalid={error ? "true" : "false"}
            disabled={isLoading}
          />
          <label 
            htmlFor="cv-upload"
            tabIndex={0}
            onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') document.getElementById('cv-upload')?.click(); }}
            className={`flex flex-col items-center justify-center w-full px-6 py-10 border-2 border-dashed rounded-xl cursor-pointer transition-all duration-200 focus:outline-none focus:ring-4 focus:ring-blue-300 dark:focus:ring-blue-800
              ${error ? 'border-red-400 bg-red-50 hover:bg-red-100 dark:bg-red-900/20' : 
                file ? 'border-green-500 bg-green-50 hover:bg-green-100 dark:bg-green-900/20 dark:border-green-400' : 
                'border-blue-300 bg-blue-50 text-blue-800 hover:bg-blue-100 dark:bg-gray-800 dark:border-gray-600 dark:hover:bg-gray-700'}`}
          >
            <span className="text-4xl mb-3" aria-hidden="true">{file ? '✅' : '📁'}</span>
            <span className={`font-semibold text-lg text-center ${file ? 'text-green-700 dark:text-green-400' : 'text-blue-800 dark:text-blue-300'}`}>
              {file ? file.name : "Haz clic aquí para seleccionar tu archivo"}
            </span>
            {!file && <span className="text-sm mt-2 text-gray-500 dark:text-gray-400 text-center">Tamaño máximo: 10MB</span>}
          </label>
        </div>

        <button
          type="submit"
          aria-disabled={!file || isLoading ? "true" : "false"}
          aria-busy={isLoading}
          onClick={(e) => {
            if (!file || isLoading) e.preventDefault();
          }}
          className={`px-8 py-3.5 rounded-lg flex items-center justify-center w-full font-bold text-lg focus:outline-none focus:ring-4 transition-all shadow-sm ${
            !file || isLoading
              ? 'bg-slate-200 text-slate-500 border border-slate-300 cursor-not-allowed dark:bg-slate-700 dark:text-slate-400 dark:border-slate-600'
              : 'bg-[#374BA6] text-white hover:bg-[#2d3f96] focus:ring-blue-300 dark:focus:ring-blue-800 shadow-md'
          }`}
        >
          {isLoading ? (
            <span className="flex items-center gap-2">
              <svg className="animate-spin h-5 w-5 text-current" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
              Analizando documento...
            </span>
          ) : 'Subir y continuar'}
        </button>
      </form>
    </div>
  );
}