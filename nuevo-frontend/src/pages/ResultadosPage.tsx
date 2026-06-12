/* eslint-disable no-console */
/* eslint-disable @typescript-eslint/no-explicit-any */
/* eslint-disable @typescript-eslint/no-unused-vars */
/* eslint-disable no-unused-vars */
// src/pages/ResultadosPage.tsx
import React, { useEffect, useState, useRef } from 'react';
import processRadarData from './processRadarData';
import { useAppSelector } from '../app/hooks';
import type { RootState } from '../app/store';
import { buildApiUrl, API_CONFIG } from '../config/api';
import { ResponsiveRadar } from '@nivo/radar';
import logo from '../assets/Logo_teamworkz.png';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useMemo } from 'react';
import type { CvAnalysis } from '@/types/report';
import type { JobPreference } from '@/types/preferences';
import { resolveJobPreferences } from '@/utils/jobPreferences';
import '../styles/print.css';
import '../styles/report.css'; // Importar los nuevos estilos
import '../styles/stars.css'; // Importar estilos para estrellas
import { validateSoftSkills, filterValidSoftSkills } from '../utils/data-validation';
import { useDispatch } from 'react-redux';
import { generateFinalReport, saveCvAnalysis, saveSoftSkills } from '../features/personal/personalSlice';
import useCvRating from '../hooks/useCvRating';
import { convertBackendResponseToNewFormat, generateNewFormatReport, getPrettyGameName, type NewReportSchema, type PersonalData, type NormalizedJobPreferences, type UsefulTools } from '../config/reportConfig';
import { useAuth } from '../context/AuthContext';
import html2pdf from 'html2pdf.js'; 
// (import duplicado eliminado)

// Definir tipos locales para evitar importaciones problemáticas

// Tipos del rating del CV
type CvStars = 1 | 2 | 3 | 4 | 5;



// Tipo para los datos del radar
interface RadarDataItem {
  skill?: string;
  softskill?: string;
  score: number;
  [key: string]: unknown;
}

// Función para extraer el bloque JSON radarData del Markdown
function extractRadarData(markdown: string): RadarDataItem[] {
  const regex = /```json\s*([\s\S]*?)\s*```/g;
  const matches = [...markdown.matchAll(regex)];
  for (const match of matches) {
    try {
      if (match[1]) {
        const json = JSON.parse(match[1]);
        if (json && Array.isArray(json.radarData)) {
          return json.radarData;
        }
      }
    } catch (e) {
      // Ignorar errores de parseo
    }
  }
  return [];
}


// Función helper para mapeo seguro


// Eliminada: helper no usado tras la remaquetación del informe





// (Eliminado) Helper antiguo de estrellas no utilizado



// Componente para renderizar estrellas (sin regex/escapes que rompan el lint)
// Variante para diagnóstico con estilo dorado uniforme
const StarsGold: React.FC<{ n: CvStars }> = ({ n }) => {
  const filled = "★".repeat(n);
  const empty = "☆".repeat(5 - n);
  return (
    <span aria-label={`${n} de 5`}>
      <span
        className="star-filled"
        style={{
          color: '#fbbf24 !important',
          fontWeight: 'bold',
          fontSize: '1.25rem',
          textShadow: '0 1px 2px rgba(0, 0, 0, 0.1)'
        }}
      >
        {filled}
      </span>
      <span
        className="star-empty"
        style={{
          color: '#fbbf24 !important',
          opacity: '0.3',
          fontSize: '1.25rem'
        }}
      >
        {empty}
      </span>
    </span>
  );
};

// Eliminado: indicador circular de porcentaje (ScoreBadge)

const ResultadosPage: React.FC = () => {
  const { user, loading: authLoading } = useAuth();
  const dispatch = useDispatch();
  const personal = useAppSelector((state: RootState) => state.personal);
  const report = personal?.report;
  const fecha = new Date().toLocaleDateString();
  const game = useAppSelector((state: RootState) => state.game);
  const [info, setInfo] = useState<NewReportSchema | null>(null);
  // Priorizar el análisis que viene del informe IA; si no, usar el del estado local
  // Preferir el análisis más rico: primero el guardado en Redux, luego el del informe IA
  const cvAnalysis: CvAnalysis | undefined = (() => {
    const reportInfo = info as NewReportSchema | null | undefined;
    const fromReport = reportInfo?.cv_analysis;
    const fromState = personal?.cvAnalysis;

    const hasDetails = (ca: any): boolean =>
      !!(
        (ca?.cv_details && Object.values(ca.cv_details).some((v: any) => Array.isArray(v) && v.length > 0)) ||
        (Array.isArray(ca?.experience_detailed) && ca.experience_detailed.length > 0) ||
        (Array.isArray(ca?.education_detailed) && ca.education_detailed.length > 0) ||
        (Array.isArray(ca?.languages) && ca.languages.length > 0) ||
        (Array.isArray(ca?.software) && ca.software.length > 0) ||
        (Array.isArray(ca?.skills) && ca.skills.length > 0)
      );

    if (hasDetails(fromState)) return fromState as CvAnalysis;
    if (hasDetails(fromReport)) return fromReport as CvAnalysis;
    // Si ninguno tiene detalles, preferir el de Redux para mantener coherencia con analyze-cv
    return (fromState || fromReport) as CvAnalysis | undefined;
  })();

  // Hook de valoración (alias para evitar choque de nombres)
  const uid = report?.userId ?? '';
  const rid = (report as any)?.id ?? '';
  const { rateCv: submitRating } = useCvRating(uid, rid);

  const asStars = (n: number): CvStars => (n < 1 ? 1 : n > 5 ? 5 : Math.round(n)) as CvStars;


  // Debug logging usando la utilidad (comentado para producción)
  // debugState(state, 'ResultadosPage');

  // Generar report si no existe
  useEffect(() => {
    if (!report && personal.softSkills && personal.softSkills.length > 0) {
      dispatch(generateFinalReport());
    }
  }, [report, personal.softSkills, dispatch]);

  // Exponer submitRating (v:number) para el bloque embebido del informe
  useEffect(() => {
    (window as any).__rateCv = (v: number) => submitRating(asStars(v));
    return () => { try { delete (window as any).__rateCv; } catch { /* no-op */ } };
  }, [submitRating]);

  // Estado para el informe IA
  const [iaReport, setIaReport] = useState<string>('');
  const [iaScore, setIaScore] = useState<number | undefined>(undefined);
  const [loadingIa, setLoadingIa] = useState<boolean>(false);
  const [errorIa, setErrorIa] = useState<string>('');
  const fetchSignatureRef = useRef<string>('');
  const isFetchingRef = useRef<boolean>(false);
  const fetchIaReportRef = useRef<() => Promise<void> | null>(null);
  const reportCacheKey = `evaluate_report_v1_${user?.id || 'anon'}`;

  // Restore cached report immediately so the page isn't blank on refresh
  useEffect(() => {
    if (info) return;
    try {
      const cached = sessionStorage.getItem(reportCacheKey);
      if (!cached) return;
      const { data, ts, sig } = JSON.parse(cached) as { data: NewReportSchema; ts: number; sig: string };
      if (Date.now() - ts > 4 * 60 * 60 * 1000) { sessionStorage.removeItem(reportCacheKey); return; }
      setInfo(data);
      if (sig && !fetchSignatureRef.current) fetchSignatureRef.current = sig;
    } catch { /* ignore corrupt cache */ }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [reportCacheKey]);
  const [finalPhrase, setFinalPhrase] = useState<string>('');
  const resolvedJobPreferences = useMemo(
    () =>
      resolveJobPreferences({
        jobPreferences: personal?.jobPreferences as Partial<JobPreference> | string | undefined,
        workMode: personal?.workMode,
        availability: personal?.availability,
        willingToRelocate: personal?.willingToRelocate,
        hasDisabilityCert: personal?.hasDisabilityCert,
      }),
    [
      personal?.jobPreferences,
      personal?.workMode,
      personal?.availability,
      personal?.willingToRelocate,
      personal?.hasDisabilityCert,
    ],
  );

  // === NUEVO: fallback de impresión del radar (SVG → IMG) ===
  const radarBoxRef = useRef<HTMLDivElement>(null);
  const [radarImg, setRadarImg] = useState<string>('');
  useEffect(() => {
    const beforePrint = () => {
      const svg = radarBoxRef.current?.querySelector('svg');
      if (!svg) return;
      const xml = new XMLSerializer().serializeToString(svg);
      const blob = new Blob([xml], { type: 'image/svg+xml;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      setRadarImg(url);
    };
    window.addEventListener('beforeprint', beforePrint);
    return () => window.removeEventListener('beforeprint', beforePrint);
  }, []);

  // Sincronizar soft skills de minijuegos → estado personal (fallback robusto)
  useEffect(() => {
    try {
      const gameSkills = Array.isArray(game?.softSkills) ? game.softSkills : [];
      if (gameSkills.length === 0) return;

      const normalizeName = (value: unknown): string =>
        String(value ?? '').trim().toLowerCase();

      const personalSkills = Array.isArray(personal?.softSkills) ? personal.softSkills : [];
      const currentMap: Record<string, any> = {};
      for (const s of personalSkills) {
        if (!s?.skill) continue;
        const key = normalizeName(s.skill);
        if (!key) continue;
        currentMap[key] = { ...s, skill: String(s.skill).trim() };
      }
      const initialSnapshot = JSON.parse(JSON.stringify(currentMap));

      for (const s of gameSkills) {
        if (!s) continue;
        const score = Math.round(Number((s as any)?.score) || 0);
        const level = (s as any)?.level || (score < 50 ? 'bajo' : score < 75 ? 'medio' : 'alto');
        const conf = typeof (s as any)?.confidence === 'number' && (s as any).confidence <= 1
          ? Math.round((s as any).confidence * 100)
          : Math.round(Number((s as any)?.confidence) || 80);
        const name = String((s as any)?.name || (s as any)?.softSkill || 'Habilidad').trim();
        const key = normalizeName(name);
        if (!key) continue;
        const existing = currentMap[key];
        if (!existing || score > (Number(existing.score) || 0)) {
          currentMap[key] = { ...existing, skill: name, score, level, confidence: conf };
        } else if (existing && !existing.level && level) {
          currentMap[key] = { ...existing, level };
        }
      }

      const mergedList = Object.values(currentMap);
      const changed =
        mergedList.length !== personalSkills.length ||
        mergedList.some((item) => {
          const key = normalizeName((item as any)?.skill);
          const existing = initialSnapshot[key];
          return !existing
            || existing.score !== (item as any)?.score
            || existing.level !== (item as any)?.level
            || existing.confidence !== (item as any)?.confidence;
        });

      if (changed) {
        dispatch(saveSoftSkills(mergedList as any));
      }
    } catch { /* no-op */ }
  }, [game?.softSkills, personal?.softSkills, dispatch]);

  // Llamar al endpoint de IA al cargar la página (después de sincronizar datos)
  useEffect(() => {
    // Esperar a que se resuelva la sesión de autenticación antes del primer fetch,
    // para que el informe se solicite con el X-User-Id correcto desde el principio
    // (evita tener que recargar la página para que el informe aparezca).
    if (authLoading) return undefined;

    const personalJobPreferences = personal?.jobPreferences;
    const personalHasPreferences = Boolean(
      (typeof personalJobPreferences === 'string' && personalJobPreferences.trim().length > 0)
      || (personalJobPreferences
        && typeof personalJobPreferences === 'object'
        && Array.isArray((personalJobPreferences as JobPreference).areas)
        && (personalJobPreferences as JobPreference).areas.some(area => (area ?? '').toString().trim().length > 0)),
    );

    const validSoftSkillsPre = filterValidSoftSkills(personal.softSkills || []);
    const cvAnalysisInitial: CvAnalysis | null = cvAnalysis ? cvAnalysis : null;
    let cvAnalysisPayload: CvAnalysis | null = cvAnalysisInitial;
    const rawCompletedGames = Array.isArray(game?.completedGames) ? game.completedGames : [];
    const completedGamesForRequest = rawCompletedGames.length > 0
      ? rawCompletedGames
      : (Array.isArray(personal.softSkills) && personal.softSkills.length > 0 ? ['softskills-evaluated'] : []);

    const hasSoftSkillsData = validSoftSkillsPre.length > 0;
    const hasJobPreferenceData = personalHasPreferences
      || resolvedJobPreferences.needs.length > 0
      || resolvedJobPreferences.hasDisabilityCert;
    const hasCvStructuredData = Boolean(
      cvAnalysisPayload
      && ([
        cvAnalysisPayload.structure_score,
        cvAnalysisPayload.coherence_score,
        cvAnalysisPayload.key_info_score,
        cvAnalysisPayload.clarity_score,
        cvAnalysisPayload.style_score,
      ].some(score => typeof score === 'number' && score > 0)
        || (Array.isArray((cvAnalysisPayload as any).experience_detailed) && (cvAnalysisPayload as any).experience_detailed.length > 0)
        || (Array.isArray((cvAnalysisPayload as any).education_detailed) && (cvAnalysisPayload as any).education_detailed.length > 0)
        || (Array.isArray((cvAnalysisPayload as any).languages) && (cvAnalysisPayload as any).languages.length > 0)
        || (Array.isArray((cvAnalysisPayload as any).software) && (cvAnalysisPayload as any).software.length > 0)
        || (Array.isArray((cvAnalysisPayload as any).skills) && (cvAnalysisPayload as any).skills.length > 0)));
    const hasCompletedGameData = rawCompletedGames.length > 0;
    const hasMeaningfulData = hasSoftSkillsData || hasCvStructuredData || hasJobPreferenceData || hasCompletedGameData;

    const fetchIaReport = async () => {
      // Guard: prevent concurrent fetches triggered by mid-flight state changes
      if (isFetchingRef.current) return;

      if (!hasMeaningfulData) {
        if (import.meta.env.MODE !== 'production') {
          // eslint-disable-next-line no-console
          console.log('⏭️ DEBUG - Omitiendo fetch del informe IA por falta de datos relevantes');
        }
        return;
      }

      const signature = JSON.stringify({
        softSkills: [...validSoftSkillsPre]
          .map(skill => `${skill.skill}:${Math.round(Number(skill.score) || 0)}`)
          .sort(),
        jobPreferences: {
          areas: [...resolvedJobPreferences.areas].map(area => area.trim()).filter(Boolean).sort(),
          needs: [...resolvedJobPreferences.needs].map(need => need.trim()).filter(Boolean).sort(),
          workMode: personalHasPreferences ? (resolvedJobPreferences.workMode ?? '') : '',
          availability: personalHasPreferences ? (resolvedJobPreferences.availability ?? '') : '',
          willingToRelocate: personalHasPreferences ? resolvedJobPreferences.willingToRelocate : undefined,
          hasDisabilityCert: personalHasPreferences ? resolvedJobPreferences.hasDisabilityCert : undefined,
        },
        completedGames: [...completedGamesForRequest].map(gameId => String(gameId)).sort(),
        // Use only the user-uploaded CV analysis (personal.cvAnalysis) for the signature,
        // NOT the merged cvAnalysis that includes data from the generated report.
        // This prevents a re-fetch loop when setInfo populates info.cv_analysis.
        cv: personal?.cvAnalysis
          ? {
            scores: [
              Number(personal.cvAnalysis.structure_score) || 0,
              Number(personal.cvAnalysis.coherence_score) || 0,
              Number(personal.cvAnalysis.key_info_score) || 0,
              Number(personal.cvAnalysis.clarity_score) || 0,
              Number(personal.cvAnalysis.style_score) || 0,
            ],
            experience: Array.isArray((personal.cvAnalysis as any).experience_detailed)
              ? (personal.cvAnalysis as any).experience_detailed.length
              : 0,
            education: Array.isArray((personal.cvAnalysis as any).education_detailed)
              ? (personal.cvAnalysis as any).education_detailed.length
              : 0,
          }
          : null,
      });

      if (fetchSignatureRef.current === signature) {
        if (import.meta.env.MODE !== 'production') {
          // eslint-disable-next-line no-console
          console.log('⏭️ DEBUG - Saltando fetch IA: la firma de datos no cambió');
        }
        return;
      }
      fetchSignatureRef.current = signature;
      isFetchingRef.current = true;

      setLoadingIa(true);
      setErrorIa('');

      // Asegurar análisis del CV si existe un archivo subido pero no hay análisis
      if (personal?.cvFile && !personal?.cvAnalysis) {
        try {
          const dataUrl = personal.cvFile.fileContent;
          const respBlob = await fetch(dataUrl);
          const blob = await respBlob.blob();
          const form = new FormData();
          const fileName = personal.cvFile.fileName || 'cv.pdf';
          form.append('cv_file', new File([blob], fileName, { type: 'application/pdf' }));
          form.append('game_results', '{}');
          form.append('preferences', '{}');
          const analyzeRes = await fetch(buildApiUrl(API_CONFIG.ENDPOINTS.PDF_ANALYZE), {
            method: 'POST',
            body: form,
          });
          if (analyzeRes.ok) {
            const analysis = await analyzeRes.json();
            cvAnalysisPayload = analysis;
            dispatch(saveCvAnalysis(analysis));
            // Esperar a que Redux se actualice antes de continuar
            await new Promise(resolve => setTimeout(resolve, 120));
          }
        } catch {
          // Error silencioso — el informe se genera igualmente sin datos de CV pre-análisis
        }
      }

      try {
        // SOLUCIÓN: Asegurar que siempre hay datos mínimos para el informe
        // Intentar recuperar nombre desde reporte, estado o CV
        const cvName =
          (cvAnalysisPayload as any)?.contact?.name ||
          (cvAnalysisPayload as any)?.contact?.nombre ||
          (cvAnalysisPayload as any)?.candidate ||
          (cvAnalysisPayload as any)?.cv_structured?.candidate ||
          '';
        const userFullName =
          `${report?.firstName || ''} ${report?.lastName || ''}`.trim() ||
          `${personal?.firstName || ''} ${personal?.lastName || ''}`.trim() ||
          String(cvName || '').trim() ||
          'Usuario';
        const validSoftSkills = validSoftSkillsPre;

        // Si no hay softSkills, proporcionar datos básicos para que el informe se genere
        const normalizeLevel = (value: unknown): 'bajo' | 'medio' | 'alto' => {
          if (typeof value !== 'string') return 'medio';
          const v = value.trim().toLowerCase();
          if (v === 'alto') return 'alto';
          if (v === 'bajo') return 'bajo';
          return 'medio';
        };

        const toPercentInt = (value: unknown): number => {
          // Acepta 0-1 o 0-100. Convierte a entero 0-100 seguro
          const num = Number(value);
          if (Number.isNaN(num)) return 0;
          const perc = num <= 1 ? num * 100 : num;
          return Math.max(0, Math.min(100, Math.round(perc)));
        };

        const softSkillsToSend = validSoftSkills.length > 0 ? validSoftSkills.map((skill) => ({
          skill: skill.skill || 'Habilidad no definida',
          score: Number(skill.score) || 0,
          level: normalizeLevel(skill.level),
          confidence: toPercentInt(skill.confidence),
        })) : [{
          skill: 'Motivación profesional',
          score: 70,
          level: 'medio',
          confidence: 80,
        }];

        const mergeCvDetails = (target: any, source: any): void => {
          if (!source || typeof source !== 'object') return;
          const ensureArray = (val: any) => (Array.isArray(val) ? val : []);
          const stringifyList = (items: any[]): string[] => {
            if (!items) return [];
            const out: string[] = [];
            for (const it of items) {
              if (it === null || it === undefined) continue;
              if (typeof it === 'string') {
                const t = it.trim();
                if (t) out.push(t);
                continue;
              }
              if (typeof it === 'number' || typeof it === 'boolean') {
                out.push(String(it));
                continue;
              }
              if (Array.isArray(it)) {
                out.push(...stringifyList(it));
                continue;
              }
              if (typeof it === 'object') {
                const parts: string[] = [];
                const keys = [
                  'title', 'cargo', 'position', 'role', 'puesto',
                  'company', 'empresa', 'organization', 'organizacion',
                  'period', 'duration', 'start_date', 'fecha_inicio', 'end_date', 'fecha_fin',
                  'description', 'descripcion', 'degree', 'titulo', 'institution', 'institucion', 'school', 'name', 'language', 'idioma', 'level', 'nivel'
                ];
                for (const k of keys) {
                  const v = (it as any)[k];
                  if (v !== null && v !== undefined && String(v).trim()) parts.push(String(v).trim());
                }
                const line = parts.join(' — ').trim();
                if (line) out.push(line);
                continue;
              }
            }
            // Unificar y limpiar duplicados
            const seen = new Set<string>();
            return out.filter((x) => {
              const key = x.toLowerCase();
              if (seen.has(key)) return false;
              seen.add(key);
              return true;
            });
          };

          target.experience_detailed = ensureArray(target.experience_detailed).length
            ? target.experience_detailed
            : ensureArray(source.experience_detailed || source.experience);
          target.education_detailed = ensureArray(target.education_detailed).length
            ? target.education_detailed
            : ensureArray(source.education_detailed || source.education);
          target.languages = ensureArray(target.languages).length
            ? target.languages
            : ensureArray(source.languages);
          target.software = ensureArray(target.software).length
            ? target.software
            : ensureArray(source.software || source.skills || source.tools);
          if (source.cv_details) {
            const t = target.cv_details || { experience: [], education: [], languages: [], tools: [] };
            const s = source.cv_details;
            t.experience = t.experience && t.experience.length ? t.experience : stringifyList(ensureArray(s.experience));
            t.education = t.education && t.education.length ? t.education : stringifyList(ensureArray(s.education));
            t.languages = t.languages && t.languages.length ? t.languages : stringifyList(ensureArray(s.languages));
            t.tools = t.tools && t.tools.length ? t.tools : stringifyList(ensureArray(s.tools || s.software));
            target.cv_details = t;
          } else {
            // Si no hay cv_details en la fuente, generarlos a partir de los arrays detallados
            const t = target.cv_details || { experience: [], education: [], languages: [], tools: [] };
            if (!t.experience?.length) t.experience = stringifyList(target.experience_detailed || target.experience || []);
            if (!t.education?.length) t.education = stringifyList(target.education_detailed || target.education || []);
            if (!t.languages?.length) t.languages = stringifyList(target.languages || []);
            if (!t.tools?.length) t.tools = stringifyList(target.software || target.skills || []);
            target.cv_details = t;
          }
        };

        // Reintentar tomar el cvAnalysis más reciente del estado si se actualizó tras el análisis
        if (!cvAnalysisPayload && personal?.cvAnalysis) {
          cvAnalysisPayload = personal.cvAnalysis as CvAnalysis;
        }
        // Si el cvAnalysis proveniente del informe no tiene detalles, injertar los del estado
        if (cvAnalysisPayload && personal?.cvAnalysis) {
          mergeCvDetails(cvAnalysisPayload as any, personal.cvAnalysis);
        }
        // Fallback seguro para no enviar null al backend
        if (!cvAnalysisPayload) {
          cvAnalysisPayload = {
            structure_score: 0,
            coherence_score: 0,
            key_info_score: 0,
            clarity_score: 0,
            style_score: 0,
            evidence: {
              structure: '',
              coherence: '',
              key_info: '',
              clarity: '',
              style: '',
            },
            corrections: [],
            reordering_suggestions: [],
            experience_detailed: [],
            education_detailed: [],
            languages: [],
            software: [],
            contact: {},
          };
        }

        const jp: JobPreference = resolvedJobPreferences;
        const pickFirstNonEmpty = (...values: Array<unknown>): string => {
          for (const value of values) {
            if (value === null || value === undefined) continue;
            const trimmed = (typeof value === 'string' ? value : String(value)).trim();
            if (trimmed.length > 0) return trimmed;
          }
          return '';
        };
        const jobPrefsAny = personal?.jobPreferences as any;
        const jpResolvedAny = resolvedJobPreferences as any;
        const cvContactLocation = (() => {
          const contact = (cvAnalysisPayload as any)?.contact || (cvAnalysisPayload as any)?.cv_structured?.contact || {};
          const loc = (contact as any)?.location;
          return typeof loc === 'string' ? loc.trim() : '';
        })();
        const preferredLocation = pickFirstNonEmpty(
          jobPrefsAny?.location,
          jpResolvedAny?.location,
          cvContactLocation,
          (report as Record<string, unknown> | undefined)?.['location'],
        );

        const enrichedJobPreferences = {
          ...jp,
          availability: personal?.availability ?? jp.availability,
          startDate: (personal as any)?.startDate ?? (jp as any)?.startDate,
          needs: Array.isArray(jobPrefsAny?.needs)
            ? jobPrefsAny.needs
            : jp.needs,
          accessibilitySettings: (personal as any)?.accessibilitySettings ?? (jp as any)?.accessibilitySettings,
          languages: Array.isArray(jobPrefsAny?.languages)
            ? jobPrefsAny.languages
            : (jp as any)?.languages,
          location: preferredLocation || (jp as any)?.location,
        } as JobPreference & Record<string, unknown>;

        // Datos de contacto normalizados
        // (emailFromCv y phoneFromCv eliminados por no usarse)
        const completedGamesDetailed = completedGamesForRequest.map((g) => String(g)).filter(Boolean);

        // Construye la frase motivacional final (caja azul) a partir de un informe
        // ya normalizado. Se usa tanto al generar un informe nuevo como al cargar
        // uno existente desde /api/report/latest, para que la UI quede completa
        // (iaReport, finalPhrase, etc.) sin necesidad de volver a llamar a la IA.
        const buildFinalPhrase = (normalizedReport: NewReportSchema, fallbackName: string): string => {
          const firstName = (String(normalizedReport.personal_data?.name || fallbackName).split(' ')[0] || 'Tu perfil').trim();
          const normalize = (val: unknown): string => {
            const n = String(val || '').toLowerCase().trim();
            if (!n) return '';
            if (/anal(í|i)tico/.test(n)) return 'pensamiento analítico';
            if (/cr(í|i)tico/.test(n)) return 'pensamiento crítico';
            if (/curiosidad|aprendizaje/.test(n)) return 'curiosidad y aprendizaje';
            if (/resiliencia|flexibilidad/.test(n)) return 'resiliencia y flexibilidad';
            if (/autoconciencia/.test(n)) return 'autoconciencia';
            if (/influencia/.test(n)) return 'influencia social';
            if (/decisiones/.test(n)) return 'toma de decisiones';
            return String(val || 'fortalezas');
          };
          const sorted = [...(normalizedReport.soft_skills || [])].sort((a: any, b: any) => (b?.score ?? 0) - (a?.score ?? 0));
          const s1 = normalize(sorted[0]?.skill);
          const s2 = normalize(sorted[1]?.skill);
          const normalizeMode = (value: unknown): 'remoto' | 'híbrido' | 'presencial' | '' => {
            if (typeof value !== 'string') return '';
            const raw = value.trim();
            if (!raw) return '';
            const lower = raw
              .toLowerCase()
              .normalize('NFD')
              .replace(/[̀-ͯ]/g, '');
            if (/(hibrid|mixt|combin|flexib|dual|semipresenc)/.test(lower)) return 'híbrido';
            if (/(remot|teletrab|home\s*office|desde casa|work from home)/.test(lower)) return 'remoto';
            if (/(presenc|oficina|onsite|en sitio|en-sitio|cara a cara|oficinas)/.test(lower)) return 'presencial';
            return '';
          };

          const jobPreferences = (
            (report?.jobPreferences as (Partial<JobPreference> & Record<string, unknown>) | undefined) ??
            ((report as Record<string, unknown> | undefined)?.['job_preferences'] as (Partial<JobPreference> & Record<string, unknown>) | undefined) ??
            (personal?.jobPreferences as (Partial<JobPreference> & Record<string, unknown>) | undefined)
          );

          const resolvedPersonalPrefs = resolvedJobPreferences;
          const personalHasPrefs = personalHasPreferences || personal?.completed;
          const normalizedWorkEnvironment = normalizeMode(normalizedReport?.ideal_work_environment);

          const preferredMode =
            normalizeMode(jobPreferences?.['workMode']) ||
            normalizeMode(jobPreferences?.['work_mode']) ||
            normalizeMode(jobPreferences?.['preferredMode']) ||
            normalizeMode(jobPreferences?.['preferred_mode']) ||
            normalizeMode(jobPreferences?.['mode']) ||
            (personalHasPrefs ? normalizeMode(resolvedPersonalPrefs.workMode) : '') ||
            normalizedWorkEnvironment;

          const remotePref = (() => {
            if (preferredMode === 'remoto') return 'el trabajo remoto';
            if (preferredMode === 'híbrido') return 'los entornos híbridos';
            if (preferredMode === 'presencial') return 'los entornos presenciales';
            const remoteWork = jobPreferences?.['remoteWork'];
            if (remoteWork === true) return 'el trabajo remoto';
            return 'los entornos presenciales';
          })();
          const rolesArr = Array.isArray(normalizedReport?.suggested_roles) ? normalizedReport.suggested_roles : [];
          const roleName = (r: any) => {
            if (!r) return '';
            if (typeof r === 'string') return r;
            return r?.role || r?.name || r?.title || r?.label || r?.position || r?.jobTitle || '';
          };
          const roleHint = rolesArr.map(roleName).filter(Boolean).slice(0, 2).join(' y ') || 'roles administrativos';
          const improv = Array.isArray(normalizedReport?.improvement_areas) ? normalizedReport.improvement_areas : [];
          const clean = (v: string) => String(v || '').replace(/\s*\((?:\d+%?|\d+\s*\/\s*\d+)\)\s*/g, '').trim();
          const improvementAreas = improv
            .map((a: any) => {
              if (!a) return '';
              if (typeof a === 'string') return clean(a);
              return clean(a?.area || a?.name || '');
            })
            .filter(Boolean)
            .slice(0, 2)
            .join(' y ') || 'tus áreas de mejora';
          const fortalezas = s1 && s2 ? `Aprovecha tu ${s1} y ${s2} para avanzar hacia tus objetivos profesionales.` : s1 ? `Aprovecha tu ${s1} para avanzar hacia tus objetivos profesionales.` : 'Aprovecha tus fortalezas para avanzar hacia tus objetivos profesionales.';
          return `Este informe ha sido elaborado a partir de tus preferencias laborales, los resultados de los minijuegos y tu CV.\n\n${firstName}, tu perfil muestra una base sólida de habilidades y una clara orientación al crecimiento.\n\n${fortalezas} Además, ${remotePref} y ${roleHint} encajan con tus competencias. Continúa desarrollando ${improvementAreas} y mantén la motivación: tu potencial está en constante evolución.`;
        };

        // Try loading an existing saved report before regenerating (saves 30s+ AI call)
        // Skip if: user just uploaded a new CV (they want a fresh report)
        const hasNewCvUpload = Boolean(personal?.cvFile);
        if (user?.id && !hasNewCvUpload && !info) {
          try {
            const latestRes = await fetch(buildApiUrl(API_CONFIG.ENDPOINTS.REPORT_LATEST), {
              headers: { 'X-User-Id': user.id },
              signal: AbortSignal.timeout(8000),
            });
            if (latestRes.ok) {
              const latestData = await latestRes.json();
              if (latestData?.profile_summary || latestData?.summary) {
                const normalized = latestData as NewReportSchema;
                setInfo(normalized);
                // Generar también el markdown y la frase final a partir del informe
                // cacheado: muchas partes de la UI (botón de PDF, secciones de
                // corrección del CV, caja final) están condicionadas a `iaReport`
                // y se quedaban vacías si solo se rellenaba `info`.
                const cachedMarkdown = generateNewFormatReport(normalized);
                setIaReport(cachedMarkdown);
                const cachedScore = pickScore(normalized.employability_score);
                if (cachedScore) setIaScore(cachedScore);
                setFinalPhrase(buildFinalPhrase(normalized, normalized.personal_data?.name || userFullName));
                try {
                  sessionStorage.setItem(reportCacheKey, JSON.stringify({
                    data: normalized, ts: Date.now(), sig: fetchSignatureRef.current,
                  }));
                } catch { /* storage full */ }
                return;
              }
            }
          } catch {
            // Network error or no existing report — fall through to generation
          }
        }

        // Prepare data objects for JSON parts
        const gameResultsData = {
          completedGames: completedGamesDetailed,
          softSkills: softSkillsToSend
        };

        const preferencesData = enrichedJobPreferences;

        // Construct FormData
        const formData = new FormData();
        formData.append("game_results", JSON.stringify(gameResultsData));
        formData.append("preferences", JSON.stringify(preferencesData));

        // Add CV file if available
        if (personal?.cvFile?.fileContent) {
          try {
            const res = await fetch(personal.cvFile.fileContent);
            const blob = await res.blob();
            formData.append("cv_file", blob, personal.cvFile.fileName || "cv.pdf");
          } catch {
            // CV file processing failed — report will be generated without CV
          }
        }

        const primaryUrl = buildApiUrl(API_CONFIG.ENDPOINTS.IA_REPORT);

        // Prepare headers
        const headers: HeadersInit = {};
        if (user?.id) {
          headers['X-User-Id'] = user.id;
        }

        const res = await fetch(primaryUrl, {
          method: 'POST',
          // Content-Type header is set automatically by browser for FormData
          headers: headers,
          body: formData,
          signal: AbortSignal.timeout(180000), // Timeout de 3 minutos
        });

        if (import.meta.env.MODE !== 'production') {
          console.log('🔍 DEBUG - Response status:', res.status);
          console.log('🔍 DEBUG - Response headers:', Object.fromEntries(res.headers.entries()));
        }

        const data = await res.json();
        if (import.meta.env.MODE !== 'production') {
          // eslint-disable-next-line no-console
          console.log('🔍 DEBUG - Respuesta del backend:', data);
          // eslint-disable-next-line no-console
          console.log('🔍 DEBUG - res.ok:', res.ok);
          // eslint-disable-next-line no-console
          console.log('🔍 DEBUG - data exists:', !!data);
          // eslint-disable-next-line no-console
          console.log('🔍 DEBUG - data.summary exists:', !!data?.summary);
          // eslint-disable-next-line no-console
          console.log('🔍 DEBUG - data.summary value:', data?.summary);
          // eslint-disable-next-line no-console
          console.log('🔍 DEBUG - data.recommendations exists:', !!data?.recommendations);
          // eslint-disable-next-line no-console
          console.log('🔍 DEBUG - data.recommendations value:', data?.recommendations);
          // eslint-disable-next-line no-console
          console.log('🔍 DEBUG - Condition result:', res.ok && !!data?.summary);
        }


        // SOLUCIÓN: Cambiar la condición para usar los campos correctos del backend
        // El backend devuelve data.report.resumen_ejecutivo, no data.summary
        if (import.meta.env.MODE !== 'production') {
          console.log('🔍 DEBUG - Validando respuesta del backend:');
          console.log('  - res.ok:', res.ok);
          console.log('  - data exists:', !!data);
          console.log('  - data.report:', data?.report);
          console.log('  - data.report?.resumen_ejecutivo:', data?.report?.resumen_ejecutivo);
          console.log('  - data.employabilityScore:', data?.employabilityScore);
          console.log('  - data.level:', data?.level);
          console.log('  - data.recommendations:', data?.recommendations);
        }

        // NUEVA LÓGICA: Validar que la respuesta tenga la estructura esperada del backend
        const hasValidReport = res.ok && data && (
          // Verificar que exista al menos uno de estos campos requeridos
          (data.report && typeof data.report === 'object') ||
          (typeof data.employabilityScore === 'number') ||
          (typeof (data as { employability_score?: unknown }).employability_score === 'number') ||
          (typeof data.level === 'string') ||
          (Array.isArray((data as any).recommendations)) ||
          // Compatibilidad con respuestas sin 'report' (Azure)
          ((data as any).cv_analysis && typeof (data as any).cv_analysis === 'object') ||
          (Array.isArray((data as any).improvement_areas)) ||
          ((data as any).action_plan && typeof (data as any).action_plan === 'object') ||
          ((data as any).job_search_advice && typeof (data as any).job_search_advice === 'object') ||
          (Array.isArray((data as any).softSkills))
        );

        if (hasValidReport) {
          // Generar informe profesional con el nuevo formato
          const candidateName = String(data?.report?.fullName || userFullName);

          // Datos personales: preferir recomendaciones, luego report.ui y por último contact del CV
          const dpSrc = (data as { recommendations?: { datos_personales?: Record<string, unknown> }; report?: { ui?: { datos_personales?: Record<string, unknown> } } })?.recommendations?.datos_personales
            || (data as { report?: { ui?: { datos_personales?: Record<string, unknown> } } })?.report?.ui?.datos_personales
            || {} as Record<string, unknown>;

          const firstNonEmpty = (...values: Array<unknown>): string => {
            for (const value of values) {
              if (value === null || value === undefined) continue;
              const trimmed = (typeof value === 'string'
                ? value
                : String(value))
                .trim();
              if (trimmed.length > 0) return trimmed;
            }
            return '';
          };

          const firstFromArray = (value: unknown): string => {
            if (!Array.isArray(value)) return '';
            for (const entry of value) {
              const asString = typeof entry === 'string'
                ? entry.trim()
                : String(entry ?? '').trim();
              if (asString) return asString;
            }
            return '';
          };

          const stateFullName = `${personal?.firstName ?? ''} ${personal?.lastName ?? ''}`.trim();
          const reportFullName = `${report?.firstName ?? ''} ${report?.lastName ?? ''}`.trim();
          const cvContact = personal?.cvAnalysis?.contact || report?.cvAnalysis?.contact || {};
          const cvEmail = firstFromArray((cvContact as { emails?: unknown[] }).emails);
          const cvPhone = firstFromArray((cvContact as { phones?: unknown[] }).phones);
          const cvLocation = typeof (cvContact as { location?: unknown }).location === 'string'
            ? String((cvContact as { location?: unknown }).location).trim()
            : '';

          const backendReport = (data as { report?: { fullName?: string; email?: string; phone?: string; location?: string; personal_data?: Record<string, unknown> } }).report;

          const dp: PersonalData = {
            name: firstNonEmpty(
              dpSrc?.['name'],
              backendReport?.personal_data?.['name'],
              backendReport?.fullName,
              reportFullName,
              stateFullName,
              candidateName,
            ) || candidateName,
            location: firstNonEmpty(
              dpSrc?.['location'],
              backendReport?.personal_data?.['location'],
              backendReport?.location,
              cvLocation,
              (personal?.report as Record<string, unknown> | undefined)?.['location'],
              'No consta',
            ) || 'No consta',
            email: firstNonEmpty(
              dpSrc?.['email'],
              backendReport?.personal_data?.['email'],
              backendReport?.email,
              (report as Record<string, unknown> | undefined)?.['email'],
              personal?.email,
              cvEmail,
              'No consta',
            ) || 'No consta',
            phone: firstNonEmpty(
              dpSrc?.['phone'],
              backendReport?.personal_data?.['phone'],
              backendReport?.phone,
              (report as Record<string, unknown> | undefined)?.['phone'],
              personal?.whatsapp,
              cvPhone,
              'No especificado',
            ) || 'No especificado',
            disability_certificate: (dpSrc?.['disability_certificate'] != null)
              ? String(dpSrc['disability_certificate'])
              : firstNonEmpty(
                backendReport?.personal_data?.['disability_certificate'],
                ((report?.jobPreferences as unknown as { hasDisabilityCert?: boolean })?.hasDisabilityCert ?? personal?.hasDisabilityCert)
                  ? 'Sí'
                  : 'No',
              ) || 'No',
          };

          let normalized: NewReportSchema;
          try {
            normalized = convertBackendResponseToNewFormat(data);
            // Merge user-provided personal data when backend values are missing or placeholders
            const isMissing = (val: unknown): boolean => {
              if (val === undefined || val === null) return true;
              if (typeof val === 'string') {
                const trimmed = val.trim();
                return trimmed === '' || trimmed === 'No consta' || trimmed === 'No especificado';
              }
              return false;
            };
            for (const key of Object.keys(dp) as (keyof PersonalData)[]) {
              const backendVal = normalized.personal_data?.[key];
              if (isMissing(backendVal)) {
                normalized.personal_data[key] = dp[key];
              }
            }
            // Completar preferencias laborales con la información del usuario si el backend no las devolvió completas
            const toUnique = (arr: unknown): string[] => {
              if (!Array.isArray(arr)) return [];
              const set = new Set<string>();
              for (const item of arr) {
                const val = String(item ?? '').trim();
                if (val) set.add(val);
              }
              return Array.from(set);
            };
            const mergedPrefs: NormalizedJobPreferences = {
              areas: toUnique(normalized.job_preferences?.areas || []),
              needs: toUnique(normalized.job_preferences?.needs || []),
              preferred_platforms: toUnique(normalized.job_preferences?.preferred_platforms || []),
              location: normalized.job_preferences?.location || '',
              seniority: normalized.job_preferences?.seniority || '',
              work_mode: normalized.job_preferences?.work_mode || '',
              disability_certificate: normalized.job_preferences?.disability_certificate || '',
              availability: normalized.job_preferences?.availability || '',
              willing_to_relocate: normalized.job_preferences?.willing_to_relocate,
            };
            const applyPrefs = (src?: unknown) => {
              const srcAny = src as Record<string, unknown> | undefined;
              if (!srcAny) return;
              if (Array.isArray(srcAny['areas'])) mergedPrefs.areas = toUnique([...mergedPrefs.areas, ...(srcAny['areas'] as unknown[])]);
              if (Array.isArray(srcAny['needs'])) mergedPrefs.needs = toUnique([...mergedPrefs.needs, ...(srcAny['needs'] as unknown[])]);
              if (Array.isArray(srcAny['preferred_platforms'])) mergedPrefs.preferred_platforms = toUnique([...mergedPrefs.preferred_platforms, ...(srcAny['preferred_platforms'] as unknown[])]);
              if (srcAny['location'] && !mergedPrefs.location) mergedPrefs.location = String(srcAny['location']).trim();
              if (srcAny['seniority'] && !mergedPrefs.seniority) mergedPrefs.seniority = String(srcAny['seniority']).trim();
              const wm = (srcAny['work_mode'] || srcAny['workMode']) as unknown;
              if (wm && !mergedPrefs.work_mode) mergedPrefs.work_mode = String(wm).trim();
              if (!mergedPrefs.availability && srcAny['availability']) mergedPrefs.availability = String(srcAny['availability']).trim();
              if (mergedPrefs.willing_to_relocate === undefined && typeof srcAny['willing_to_relocate'] === 'boolean') {
                mergedPrefs.willing_to_relocate = srcAny['willing_to_relocate'] as boolean;
              }
              if (mergedPrefs.willing_to_relocate === undefined && typeof srcAny['willingToRelocate'] === 'boolean') {
                mergedPrefs.willing_to_relocate = srcAny['willingToRelocate'] as boolean;
              }
              if (!mergedPrefs.disability_certificate && (srcAny['disability_certificate'] || srcAny['hasDisabilityCert'])) {
                mergedPrefs.disability_certificate = (srcAny['hasDisabilityCert'] ?? srcAny['disability_certificate']) ? 'Sí' : 'No';
              }
            };
            applyPrefs(normalized.job_preferences);
            applyPrefs(enrichedJobPreferences);
            applyPrefs(resolvedJobPreferences);
            applyPrefs(personal?.jobPreferences);
            normalized.job_preferences = mergedPrefs;

            // Rellenar soft skills, juegos y score si el backend devolvió valores vacíos
            if ((!normalized.soft_skills || normalized.soft_skills.length === 0) && softSkillsToSend.length > 0) {
              normalized.soft_skills = softSkillsToSend;
            }
            if ((!normalized.completed_games || normalized.completed_games.length === 0) && completedGamesDetailed.length > 0) {
              normalized.completed_games = completedGamesDetailed;
            }
            const bestScore = pickScore(iaScore)
              ?? pickScore(data?.employabilityScore)
              ?? pickScore((data as { employability_score?: number })?.employability_score)
              ?? pickScore(report?.employabilityScore)
              ?? computedScore;
            if (!pickScore(normalized.employability_score) && bestScore) {
              normalized.employability_score = bestScore;
            }

            // Completar detalles del CV con el análisis almacenado si faltan campos
            const ensureArray = (value: any): Array<{ title: string; detail: string }> => {
              if (!value) return [];
              if (Array.isArray(value)) {
                return value
                  .map((v) => {
                    if (v === null || v === undefined) return null;
                    if (typeof v === 'object' && !Array.isArray(v)) {
                      const obj = v as Record<string, unknown>;
                      const title =
                        (typeof obj['title'] === 'string' && obj['title']) ||
                        (typeof obj['role'] === 'string' && obj['role']) ||
                        (typeof obj['position'] === 'string' && obj['position']) ||
                        (typeof obj['name'] === 'string' && obj['name']) ||
                        (typeof obj['language'] === 'string' && obj['language']) ||
                        (typeof obj['tool'] === 'string' && obj['tool']) ||
                        (typeof obj['technology'] === 'string' && obj['technology']);
                      const detail =
                        (typeof obj['detail'] === 'string' && obj['detail']) ||
                        (typeof obj['description'] === 'string' && obj['description']);
                      const period =
                        (typeof obj['period'] === 'string' && obj['period']) ||
                        (typeof obj['start_date'] === 'string' && obj['start_date']) ||
                        (typeof obj['end_date'] === 'string' && obj['end_date']) ||
                        (typeof obj['duration'] === 'string' && obj['duration']);
                      const level =
                        (typeof obj['level'] === 'string' && obj['level']) ||
                        (typeof obj['certification'] === 'string' && obj['certification']);
                      return { title: title || detail || '', subtitle: period || '', level: level || '', detail: detail || '' };
                    }
                    const txt = String(v ?? '').trim();
                    return txt ? { title: txt, detail: txt } : null;
                  })
                  .filter((v): v is { title: string; detail: string } => Boolean(v));
              }
              const txt = String(value ?? '').trim();
              return txt ? [{ title: txt, detail: txt }] : [];
            };
            const ensureStringArray = (value: any): string[] => {
              if (!value) return [];
              if (Array.isArray(value)) return value.map((v) => String(v ?? '').trim()).filter(Boolean);
              const txt = String(value ?? '').trim();
              return txt ? [txt] : [];
            };
            if (cvAnalysisPayload) {
              const detailsFromCv = {
                experience: ensureArray((cvAnalysisPayload as any).experience_detailed || (cvAnalysisPayload as any).experience),
                education: ensureArray((cvAnalysisPayload as any).education_detailed || (cvAnalysisPayload as any).education),
                languages: ensureArray((cvAnalysisPayload as any).languages),
                tools: ensureArray((cvAnalysisPayload as any).software || (cvAnalysisPayload as any).skills),
              };
              const existingDetails = normalized.cv_details || { experience: [], education: [], languages: [], tools: [] };
              normalized.cv_details = {
                experience: existingDetails.experience && existingDetails.experience.length ? existingDetails.experience : detailsFromCv.experience,
                education: existingDetails.education && existingDetails.education.length ? existingDetails.education : detailsFromCv.education,
                languages: existingDetails.languages && existingDetails.languages.length ? existingDetails.languages : detailsFromCv.languages,
                tools: existingDetails.tools && existingDetails.tools.length ? existingDetails.tools : detailsFromCv.tools,
              };

              const cvScores = normalized.cv_analysis || {
                structure_score: 0,
                coherence_score: 0,
                key_info_score: 0,
                clarity_score: 0,
                style_score: 0,
                evidence: {
                  structure: '',
                  coherence: '',
                  key_info: '',
                  clarity: '',
                  style: '',
                },
                corrections: [],
                reordering_suggestions: [],
              };
              const pickCvScore = (current: unknown, incoming: unknown): number => {
                const currentNum = Number(current);
                const incomingNum = Number(incoming);
                if (Number.isFinite(currentNum) && currentNum > 0) return Math.round(currentNum);
                if (Number.isFinite(incomingNum) && incomingNum >= 0) return Math.round(incomingNum);
                return 0;
              };
              cvScores.structure_score = pickCvScore(cvScores.structure_score, (cvAnalysisPayload as any).structure_score);
              cvScores.coherence_score = pickCvScore(cvScores.coherence_score, (cvAnalysisPayload as any).coherence_score);
              cvScores.key_info_score = pickCvScore(cvScores.key_info_score, (cvAnalysisPayload as any).key_info_score);
              cvScores.clarity_score = pickCvScore(cvScores.clarity_score, (cvAnalysisPayload as any).clarity_score);
              cvScores.style_score = pickCvScore(cvScores.style_score, (cvAnalysisPayload as any).style_score ?? (cvAnalysisPayload as any).spelling_style_score);
              cvScores.corrections = Array.isArray(cvScores.corrections) && cvScores.corrections.length > 0
                ? cvScores.corrections
                : ensureStringArray((cvAnalysisPayload as any).corrections);
              cvScores.reordering_suggestions = Array.isArray(cvScores.reordering_suggestions) && cvScores.reordering_suggestions.length > 0
                ? cvScores.reordering_suggestions
                : ensureStringArray((cvAnalysisPayload as any).reordering_suggestions);
              normalized.cv_analysis = cvScores;
            }
            setInfo(normalized);
            try {
              sessionStorage.setItem(reportCacheKey, JSON.stringify({
                data: normalized, ts: Date.now(), sig: fetchSignatureRef.current,
              }));
            } catch { /* storage full */ }
          } catch (error) {
            if (import.meta.env.MODE !== 'production') {
              // eslint-disable-next-line no-console
              console.warn('⚠️ Error generando informe:', error);
            }
            setErrorIa('No se pudo generar el informe IA. Intenta nuevamente.');
            setFinalPhrase('');
            return;
          }

          const essentialFilled = normalized.summary && normalized.profile_summary && normalized.personal_data;
          if (!essentialFilled) {
            setErrorIa('El informe recibido está incompleto. Intenta nuevamente.');
            setFinalPhrase('');
            return;
          }

          const markdown = generateNewFormatReport(normalized);
          setIaReport(markdown);
          if (import.meta.env.MODE !== 'production') {
            // eslint-disable-next-line no-console
            console.log('✅ DEBUG - Informe generado exitosamente. Longitud:', markdown.length);
            // eslint-disable-next-line no-console
            console.log('✅ DEBUG - Primeros 200 caracteres:', markdown.substring(0, 200));
          }
          // Frase motivacional final destacada (fuera del markdown principal)
          // Construimos SIEMPRE el mensaje final personalizado para la caja azul
          const phraseSource: NewReportSchema = {
            ...normalized,
            suggested_roles: (normalized.suggested_roles && normalized.suggested_roles.length > 0)
              ? normalized.suggested_roles
              : (Array.isArray((data as any)?.report?.suggested_roles) ? (data as any).report.suggested_roles : []),
            improvement_areas: (normalized.improvement_areas && normalized.improvement_areas.length > 0)
              ? normalized.improvement_areas
              : (Array.isArray((data as any)?.report?.improvement_areas) ? (data as any).report.improvement_areas : []),
          };
          const composed = buildFinalPhrase(phraseSource, dp.name || candidateName);
          setFinalPhrase(composed);
          const employabilityScoreValue =
            typeof data?.employabilityScore === 'number'
              ? data.employabilityScore
              : (data as { employability_score?: number })?.employability_score;
          setIaScore(typeof employabilityScoreValue === 'number' ? employabilityScoreValue : undefined);
          if (import.meta.env.MODE !== 'production') {
            // eslint-disable-next-line no-console
            console.log('✅ DEBUG - Estado iaReport actualizado');
          }
        } else {
          if (import.meta.env.MODE !== 'production') {
            // eslint-disable-next-line no-console
            console.log('❌ DEBUG - Condición falló. Motivos:');
            // eslint-disable-next-line no-console
            console.log('  - res.ok:', res.ok);
            // eslint-disable-next-line no-console
            console.log('  - data:', !!data);
            // eslint-disable-next-line no-console
            console.log('  - data.report:', !!data?.report);
            // eslint-disable-next-line no-console
            console.log('  - data.report?.resumen_ejecutivo:', !!data?.report?.resumen_ejecutivo);
            // eslint-disable-next-line no-console
            console.log('  - data.employabilityScore:', data?.employabilityScore);
            // eslint-disable-next-line no-console
            console.log('  - data.level:', data?.level);
            console.log('  - data completo:', data);
          }

          // NUEVO: Mensaje de error más específico basado en la respuesta
          if (!res.ok) {
            setErrorIa(`Error del servidor: ${res.status} ${res.statusText}`);
          } else if (!data) {
            setErrorIa('No se recibieron datos del servidor');
          } else if (!data.report && !data.employabilityScore && !data.level && !data.recommendations) {
            setErrorIa('La respuesta del servidor no tiene el formato esperado');
          } else {
            setErrorIa('No se pudo generar el informe IA.');
          }
        }
      } catch (err) {
        // console.error('Error en fetchIaReport:', err);
        setFinalPhrase('');
        if (err instanceof Error && err.name === 'TimeoutError') {
          setErrorIa('El informe está tardando más de lo esperado. Se generará un informe básico automáticamente.');
        } else if (err instanceof Error && err.message?.includes('Failed to fetch')) {
          setErrorIa('No se pudo conectar con el servidor. Verifica tu conexión a internet.');
        } else {
          // Fallback robusto: generar un informe básico local y no mostrar banner
          try {
            const fallbackName = `${report?.firstName || ''} ${report?.lastName || ''}`.trim() || 'Usuario';
            const minimal = `# Informe Profesional de Empleabilidad\n\n## Resumen del Perfil\nInforme básico para ${fallbackName}.\n\n---\n*Informe generado automáticamente.*`;
            setIaReport(minimal);
            setErrorIa('');
          } catch {
            // En última instancia, mantener silencio para no bloquear la UI
          }
        }
      } finally {
        setLoadingIa(false);
        isFetchingRef.current = false;
      }
    };
    fetchIaReportRef.current = fetchIaReport;

    // SOLUCIÓN: Ejecutar siempre el informe si hay datos básicos del usuario
    // Verificar tanto personal.softSkills como report?.softSkills
    const hasPersonalSoftSkills = validateSoftSkills(personal.softSkills);
    const hasReportSoftSkills = validateSoftSkills(report?.softSkills || []);
    const hasSoftSkillsCombined = hasPersonalSoftSkills || hasReportSoftSkills;

    // NUEVO: También permitir generar informe si hay datos básicos del usuario
    const hasBasicUserData = (report?.firstName && report?.lastName) ||
      (cvAnalysisPayload) ||
      (report?.jobPreferences) ||
      hasJobPreferenceData;

    if (hasMeaningfulData || hasSoftSkillsCombined || hasBasicUserData) {
      if (import.meta.env.MODE !== 'production') {
        // eslint-disable-next-line no-console
        console.log('✅ CONDICIÓN CUMPLIDA - Ejecutando fetchIaReport');
        // eslint-disable-next-line no-console
        console.log('  • hasPersonalSoftSkills:', hasPersonalSoftSkills);
        // eslint-disable-next-line no-console
        console.log('  • hasReportSoftSkills:', hasReportSoftSkills);
        // eslint-disable-next-line no-console
        console.log('  • hasSoftSkillsCombined:', hasSoftSkillsCombined);
        // eslint-disable-next-line no-console
        console.log('  • hasBasicUserData:', hasBasicUserData);
        // eslint-disable-next-line no-console
        console.log('  • hasMeaningfulData:', hasMeaningfulData);
      }

      const timeoutId = setTimeout(() => {
        fetchIaReport();
      }, 200); // 200ms debería ser suficiente para que Redux se actualice

      return () => clearTimeout(timeoutId);
    }

    if (import.meta.env.MODE !== 'production') {
      // eslint-disable-next-line no-console
      console.log('❌ CONDICIÓN NO CUMPLIDA - No se ejecuta fetchIaReport');
      // eslint-disable-next-line no-console
      console.log('  • hasPersonalSoftSkills:', hasPersonalSoftSkills);
      // eslint-disable-next-line no-console
      console.log('  • hasReportSoftSkills:', hasReportSoftSkills);
      // eslint-disable-next-line no-console
      console.log('  • hasSoftSkillsCombined:', hasSoftSkillsCombined);
      // eslint-disable-next-line no-console
      console.log('  • hasBasicUserData:', hasBasicUserData);
      // eslint-disable-next-line no-console
      console.log('  • hasMeaningfulData:', hasMeaningfulData);
    }
    fetchSignatureRef.current = '';
    return undefined;
  }, [report?.jobPreferences, personal.softSkills, report?.softSkills, personal.jobPreferences, cvAnalysis, game?.completedGames, report?.firstName, report?.lastName, report?.userId, user?.id, authLoading, dispatch]);

  const handleRetry = () => {
    if (loadingIa) return;
    setErrorIa('');
    fetchIaReportRef.current?.();
  };

  // Estado para feedback
  const [feedback, setFeedback] = useState<{ rating: string, comment: string }>({ rating: '', comment: '' });
  const [feedbackSent, setFeedbackSent] = useState(false);
  const [feedbackError, setFeedbackError] = useState('');

const reportRef = useRef<HTMLDivElement>(null);

  const handleDownloadPdf = async () => {
  const element = reportRef.current;

  if (!element) {
    alert('No se ha encontrado el contenido del informe para exportar.');
    return;
  }

  // Oculta elementos que no deben salir en el PDF
  setIsExportingPdf(true);

  // Si la página está desplazada, html2canvas calcula mal la posición del
  // contenido (con scrollX/scrollY forzados a 0) y recorta la parte
  // superior del informe. Volvemos al inicio antes de capturar.
  window.scrollTo(0, 0);

  // Espera a que React actualice la pantalla antes de hacer la captura
  await new Promise((resolve) => setTimeout(resolve, 150));

  // Remove dark mode so brand colors render correctly in the PDF
  const htmlEl = document.documentElement;
  const wasDark = htmlEl.classList.contains('dark');

  if (wasDark) htmlEl.classList.remove('dark');

  element.classList.add('pdf-light-export');

  try {
    await html2pdf()
      .set({
        margin: [8, 6, 8, 6],
        filename: 'informe-empleabilidad.pdf',
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: {
          scale: 2,
          useCORS: true,
          allowTaint: true,
          backgroundColor: '#ffffff',
          logging: false,
          // Force color rendering — prevents greyscale conversion
          removeContainer: true,
          // Avoid capturing from the current scroll offset, which cuts off
          // content above/below the visible viewport when the page is scrolled
          scrollX: 0,
          scrollY: 0,
          windowWidth: document.documentElement.scrollWidth,
        },
        jsPDF: {
          unit: 'mm',
          format: 'a4',
          orientation: 'portrait',
          // eslint-disable-next-line @typescript-eslint/ban-ts-comment
          // @ts-ignore — html2pdf types don't include compress
          compress: false,
        },
        pagebreak: { mode: ['css', 'legacy'] },
      })
      .from(element)
      .save();
  } finally {
    element.classList.remove('pdf-light-export');

    if (wasDark) htmlEl.classList.add('dark');

    // Vuelve a mostrar el botón después de generar el PDF
    setIsExportingPdf(false);
  }
};

  const handleFeedbackSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFeedbackError('');
    try {

      const userId = user?.id || personal?.email || (() => {
        const key = 'evalute-anon-id';
        let id = sessionStorage.getItem(key) || localStorage.getItem(key);
        if (!id) {
          id = `anon-${Date.now()}-${Math.random().toString(36).slice(2)}`;
          try { sessionStorage.setItem(key, id); } catch { /* ignore */ }
          try { localStorage.setItem(key, id); } catch { /* ignore */ }
        }
        return id;
      })();


      const res = await fetch(buildApiUrl(API_CONFIG.ENDPOINTS.IA_FEEDBACK), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-User-Id':userId, },
        body: JSON.stringify({
          informe: iaReport,
          rating: feedback.rating,
          comment: feedback.comment,
          userData: { preferences: report?.jobPreferences, minigames: personal.softSkills, cvAnalysis },
        }),
      });
      if (res.ok) {
        setFeedbackSent(true);
      } else {
        const errorText = await res.text();
        console.error('Error feedback:', res.status, errorText);
        setFeedbackError("No se pudo enviar el feedback. ${res.status}");
      }
    } catch (error){
      console.error('error de conexion al enviar feedback:', console.error);
      setFeedbackError('Error de conexión al enviar feedback.');
    }
  };

  // Eliminado: barra de progreso visual

  // Eliminado: lógica de descarga de PDF

  // 2. Mapa de habilidades (Radar + resumen)
  // Usar useMemo para evitar recalcular en cada render
  const radarDataFromIa = useMemo(() => iaReport ? extractRadarData(iaReport) : [], [iaReport]);

  // Procesamiento de datos del radar extraído en processRadarData.ts
  const softSkillsData = useMemo(() => {
    const normalizeKey = (value: unknown): string =>
      String(value ?? '')
        .trim()
        .toLowerCase();

    // Siempre obtener datos de minijuegos como base
    const personalSkills = filterValidSoftSkills(personal.softSkills || []);
    const gameSkills = Array.isArray(game?.softSkills) ? game.softSkills : [];
    const mappedGame = gameSkills.map((s: any) => {
      const score = Math.round(Number(s?.score) || 0);
      const level = s?.level || (score < 50 ? 'bajo' : score < 75 ? 'medio' : 'alto');
      const conf = typeof s?.confidence === 'number' && s.confidence <= 1
        ? Math.round(s.confidence * 100)
        : Math.round(Number(s?.confidence) || 80);
      const skillName = String(s?.name || s?.softSkill || 'Habilidad').trim();
      return { skill: skillName, score, level, confidence: conf };
    });

    // Crear mapa base con datos de minijuegos
    const byName: Record<string, any> = {};
    for (const s of [...personalSkills, ...mappedGame]) {
      if (!s || !s.skill) continue;
      const trimmedName = String(s.skill).trim();
      if (!trimmedName) continue;
      const key = normalizeKey(trimmedName);
      const existing = byName[key];
      const score = Math.round(Number(s?.score) || 0);
      if (!existing || score > (Number(existing?.score) || 0)) {
        byName[key] = { ...s, skill: trimmedName, score };
      }
    }

    // Si hay datos de IA, combinarlos priorizando la IA pero manteniendo datos de minijuegos faltantes
    if (info?.soft_skills && info.soft_skills.length > 0) {
      for (const iaSkill of info.soft_skills) {
        if (!iaSkill) continue;
        const trimmedName = String(iaSkill.skill ?? '').trim();
        if (!trimmedName) continue;
        const key = normalizeKey(trimmedName);
        const existing = byName[key];
        const iaSkillAny = iaSkill as any;
        const iaScore = Math.max(0, Math.min(100, Math.round(Number(iaSkillAny?.score) || 0)));
        const currentScore = Number(existing?.score) || 0;
        if (!existing || iaScore > currentScore) {
          const level = iaSkillAny?.level ?? existing?.level;
          const confidence = iaSkillAny?.confidence ?? existing?.confidence;
          byName[key] = {
            ...existing,
            ...iaSkillAny,
            skill: trimmedName || existing?.skill,
            score: iaScore,
            ...(level !== undefined ? { level } : {}),
            ...(confidence !== undefined ? { confidence } : {}),
          };
        }
      }
    }

    return Object.values(byName);
  }, [info?.soft_skills, personal.softSkills, game?.softSkills]);
  const computedScore = useMemo<number | undefined>(() => {
    if (!softSkillsData || softSkillsData.length === 0) return undefined;
    const sum = softSkillsData.reduce((acc: number, s: any) => acc + (Number(s?.score) || 0), 0);
    const avg = sum / softSkillsData.length;
    const val = Math.round(avg);
    return val > 0 ? Math.min(100, val) : undefined;
  }, [softSkillsData]);
  const pickScore = (v: unknown): number | undefined => {
    const n = typeof v === 'number' ? v : Number(v);
    if (!Number.isFinite(n)) return undefined;
    const bounded = Math.max(0, Math.min(100, Math.round(n)));
    return bounded > 0 ? bounded : undefined;
  };
  const globalScore = computedScore
    ?? pickScore(info?.employability_score)
    ?? pickScore(report?.employabilityScore)
    ?? pickScore(iaScore);

  // Unificar el reporte que se muestra en pantalla y el que se envía al PDF
  const reportForRender: NewReportSchema | null = useMemo(() => {
    const ensureArray = (value: any): string[] => {
      const seen = new Set<string>();

      const push = (entry: any): void => {
        if (entry === null || entry === undefined) return;

        if (typeof entry === 'string' || typeof entry === 'number' || typeof entry === 'boolean') {
          const t = String(entry).trim();
          if (t) seen.add(t);
          return;
        }

        if (Array.isArray(entry)) {
          entry.forEach(push);
          return;
        }

        if (entry instanceof Set) {
          entry.forEach(push);
          return;
        }

        if (typeof entry === 'object') {
          const preferredKeys = [
            'title', 'subtitle', 'role', 'position', 'cargo', 'puesto',
            'company', 'organization', 'employer', 'empresa', 'organizacion',
            'institution', 'school', 'degree', 'titulo',
            'period', 'start_date', 'end_date', 'duration', 'fecha_inicio', 'fecha_fin',
            'level', 'language', 'name', 'detail', 'description', 'descripcion',
          ];

          const parts: string[] = [];
          for (const key of preferredKeys) {
            const valueForKey = (entry as any)[key];
            if (valueForKey === null || valueForKey === undefined) continue;
            const text = typeof valueForKey === 'string' || typeof valueForKey === 'number' || typeof valueForKey === 'boolean'
              ? String(valueForKey).trim()
              : '';
            if (text) parts.push(text);
          }

          const composed = parts.join(' — ').trim();
          if (composed) {
            seen.add(composed);
            return;
          }
        }

        const fallback = String(entry ?? '').trim();
        if (fallback) seen.add(fallback);
      };

      push(value);
      return Array.from(seen);
    };
    const firstNonEmpty = (...values: Array<unknown>): string => {
      for (const value of values) {
        if (value === null || value === undefined) continue;
        const trimmed = (typeof value === 'string' ? value : String(value)).trim();
        if (trimmed.length > 0) return trimmed;
      }
      return '';
    };

    const base = info ? { ...info } : null;
    if (!base && !personal?.cvAnalysis && softSkillsData.length === 0) return null;

    // Soft skills unificadas
    const unifiedSoftSkills = ((): Array<{ skill: string; score: number; level?: string; confidence?: number }> => {
      const byName: Record<string, any> = {};
      const push = (skill: any) => {
        if (!skill) return;
        const name = String(skill.skill ?? skill.name ?? '').trim();
        if (!name) return;
        const key = name.toLowerCase();
        const score = Math.max(0, Math.min(100, Math.round(Number(skill.score) || 0)));
        const existing = byName[key];
        if (!existing || score > (existing.score || 0)) {
          byName[key] = { skill: name, score, level: skill.level, confidence: skill.confidence };
        }
      };
      (softSkillsData || []).forEach(push);
      (info?.soft_skills || []).forEach(push);
      return Object.values(byName);
    })();

    const cvFromState = (personal?.cvAnalysis as any) || {};
    const cvDetailsFromInfo = (info?.cv_details as any) || {};
    const cvDetailsFromState = (cvFromState as any)?.cv_details || {};
    const cleanList = (items: string[]): string[] => {
      const noise = ['cargo detectado', 'empresa detectada', 'fecha detectada', 'experiencia extraída del cv'];
      const out: string[] = [];
      for (const it of items || []) {
        if (!it) continue;
        const txt = String(it).trim();
        if (!txt) continue;
        const lower = txt.toLowerCase();
        if (noise.some(n => lower.includes(n))) continue;
        out.push(txt);
      }
      return out;
    };

    const mergedCvDetails = {
      experience: cleanList(ensureArray([
        (cvDetailsFromInfo as any).experience_detailed,
        (cvDetailsFromInfo as any).experience,
        (cvFromState as any)?.experience_detailed,
        (cvFromState as any)?.experience,
        (cvDetailsFromState as any).experience
      ])),
      education: cleanList(ensureArray([
        (cvDetailsFromInfo as any).education_detailed,
        (cvDetailsFromInfo as any).education,
        (cvFromState as any)?.education_detailed,
        (cvFromState as any)?.education,
        (cvDetailsFromState as any).education
      ])),
      languages: cleanList(ensureArray([
        (cvDetailsFromInfo as any).languages,
        (cvFromState as any)?.languages,
        (cvDetailsFromState as any).languages
      ])),
      tools: cleanList(ensureArray([
        (cvDetailsFromInfo as any).tools,
        (cvDetailsFromInfo as any).software,
        (cvFromState as any)?.software,
        (cvFromState as any)?.skills,
        (cvDetailsFromState as any).tools
      ])),
    };

    const asCvItems = (list: string[]): Array<{ title: string; detail: string }> =>
      (list || []).map((txt) => ({ title: txt, detail: txt }));

    const mergedCvAnalysis = (() => {
      const scores: any = { ...(info?.cv_analysis || {}) };
      const apply = (key: string, value: unknown) => {
        const current = Number(scores[key]);
        const incoming = Number(value);
        if (!Number.isFinite(current) || current === 0) {
          if (Number.isFinite(incoming) && incoming >= 0) scores[key] = Math.round(incoming);
        }
      };
      apply('structure_score', (cvFromState as any)?.structure_score);
      apply('coherence_score', (cvFromState as any)?.coherence_score);
      apply('key_info_score', (cvFromState as any)?.key_info_score);
      apply('clarity_score', (cvFromState as any)?.clarity_score);
      apply('style_score', (cvFromState as any)?.style_score ?? (cvFromState as any)?.spelling_style_score);

      const mergeList = (dst: any, src: any, key: string) => {
        const current = Array.isArray(dst?.[key]) ? dst[key] : [];
        const incoming = Array.isArray(src?.[key]) ? src[key] : [];
        dst[key] = current.length > 0 ? current : incoming;
      };
      mergeList(scores, cvFromState, 'corrections');
      mergeList(scores, cvFromState, 'reordering_suggestions');
      // Evidencias: usar las del CV si existen; de lo contrario, dejar vacío (no genérico)
      if (!scores.evidence && (cvFromState as any)?.evidence) scores.evidence = (cvFromState as any).evidence;
      if (!scores.evidence && (info?.cv_analysis as any)?.evidence) scores.evidence = (info?.cv_analysis as any).evidence;
      return scores;
    })();

    const cvContact = (cvFromState as any)?.contact || (cvFromState as any)?.cv_structured?.contact || {};
    const personalData = {
      ...(base?.personal_data || {}),
      name: firstNonEmpty(
        base?.personal_data?.name,
        (cvContact as any)?.name,
        (cvContact as any)?.nombre,
        `${personal?.firstName ?? ''} ${personal?.lastName ?? ''}`,
      ),
      location: firstNonEmpty(
        base?.personal_data?.location,
        (cvContact as any)?.location,
        (resolvedJobPreferences as any)?.location,
      ),
      email: firstNonEmpty(base?.personal_data?.email, (cvContact as any)?.emails?.[0], personal?.email),
      phone: firstNonEmpty(base?.personal_data?.phone, (cvContact as any)?.phones?.[0], personal?.whatsapp),
      disability_certificate: firstNonEmpty(base?.personal_data?.disability_certificate, personal?.hasDisabilityCert ? 'Sí' : ''),
    };

    const jobPrefsUnified = (() => {
      const src: any = base?.job_preferences || {};
      const merged = {
        areas: ensureArray(src.areas),
        needs: ensureArray(src.needs),
        preferred_platforms: ensureArray(src.preferred_platforms),
        location: firstNonEmpty(src.location, (resolvedJobPreferences as any).location),
        seniority: firstNonEmpty(src.seniority, (resolvedJobPreferences as any).seniority),
        work_mode: firstNonEmpty(src.work_mode, (resolvedJobPreferences as any).workMode),
        disability_certificate: firstNonEmpty(src.disability_certificate, (resolvedJobPreferences as any).hasDisabilityCert ? 'Sí' : ''),
        availability: firstNonEmpty(src.availability, (resolvedJobPreferences as any).availability),
        willing_to_relocate: src.willing_to_relocate ?? (resolvedJobPreferences as any).willingToRelocate,
      };
      const addArr = (into: string[], values: string[]) => {
        values.forEach((v) => {
          const t = String(v ?? '').trim();
          if (t && !into.includes(t)) into.push(t);
        });
      };
      addArr(merged.areas, ensureArray((resolvedJobPreferences as any).areas));
      addArr(merged.needs, ensureArray((resolvedJobPreferences as any).needs));
      addArr(merged.preferred_platforms, ensureArray((resolvedJobPreferences as any).preferred_platforms));
      return merged;
    })();

    const completedGamesUnified = (() => {
      const set = new Set<string>();
      const push = (arr: any) => {
        if (Array.isArray(arr)) {
          arr.forEach((g) => {
            const val = String(g ?? '').trim();
            // Evitar placeholders numéricos (1,2,3) y cadenas vacías
            if (val && !/^\d+$/.test(val)) set.add(val);
          });
        }
      };
      push(info?.completed_games);
      push(game?.completedGames);
      push(report?.completedGames);
      if (set.size === 0 && unifiedSoftSkills.length > 0) set.add('softskills-evaluated');
      return Array.from(set);
    })();

    const summaryText = base?.summary || base?.profile_summary || '';
    const employabilityScore = globalScore ?? pickScore(base?.employability_score) ?? 0;
    const withEmployabilityScore = (text: string, score?: number): string => {
      if (!text || (!score && score !== 0)) return text;

      const regex = /(puntuaci[oó]n global[^\d]*)(\d{1,3})(\s*\/\s*100)?/i;
      if (regex.test(text)) {
        return text.replace(regex, `$1${score}/100`);
      }

      const trimmed = text.trim();
      const ending = trimmed.endsWith('.') ? '' : '.';
      return `${trimmed}${ending} Puntuación global: ${score}/100`;
    };
    const summaryWithScore = withEmployabilityScore(summaryText, employabilityScore);

    const unified: NewReportSchema = {
      ...(base || {}),
      summary: summaryWithScore,
      profile_summary: base?.profile_summary ? withEmployabilityScore(base.profile_summary, employabilityScore) : summaryWithScore,
      cv_analysis_summary: base?.cv_analysis_summary ? withEmployabilityScore(base.cv_analysis_summary, employabilityScore) : summaryWithScore,
      employability_score: employabilityScore ?? 0,
      personal_data: personalData as any,
      job_preferences: jobPrefsUnified as any,
      soft_skills: unifiedSoftSkills,
      strengths: base?.strengths && base.strengths.length > 0 ? base.strengths : unifiedSoftSkills.map((s) => s.skill).slice(0, 6),
      improvement_areas: base?.improvement_areas || [],
      cv_details: {
        experience: asCvItems(mergedCvDetails.experience),
        education: asCvItems(mergedCvDetails.education),
        languages: asCvItems(mergedCvDetails.languages),
        tools: asCvItems(mergedCvDetails.tools),
      },
      cv_analysis: mergedCvAnalysis as any,
      completed_games: completedGamesUnified,
      job_search_advice: (base?.job_search_advice as any) || { cv_optimization: [], letters_portfolio: [], recommended_platforms: [], networking: [], interview_tips: [] },
      action_plan: base?.action_plan || { short_term: [], medium_term: [], long_term: [] },
      useful_tools: (base?.useful_tools as UsefulTools) || { productivity: [], job_search: [], learning: [], accessibility: [] },
      // Alias para el PDF (pdf_service espera report.tools)
      // eslint-disable-next-line @typescript-eslint/ban-ts-comment
      // @ts-ignore
      tools: (base?.useful_tools as UsefulTools) || { productivity: [], job_search: [], learning: [], accessibility: [] },
      final_message: base?.final_message || (base as any)?.frase_final || finalPhrase,
      ideal_work_environment: base?.ideal_work_environment || '',
      suggested_roles: base?.suggested_roles || [],
    };

    return unified;
  }, [info, personal?.cvAnalysis, personal?.firstName, personal?.lastName, personal?.email, personal?.whatsapp, personal?.hasDisabilityCert, report?.completedGames, softSkillsData, resolvedJobPreferences, game?.completedGames, globalScore, finalPhrase, pickScore]);

  // Mantener sincronizado el markdown de pantalla con el mismo reporte que se envía al PDF
  useEffect(() => {
    if (!reportForRender) return;
    try {
      const md = generateNewFormatReport(reportForRender);
      setIaReport(md);
    } catch {
      // no-op
    }
  }, [reportForRender]);

  // Combinar datos de IA con datos de minijuegos para el radar
  const radarData = useMemo(() => {
    const combined: Array<{ skill?: string; softskill?: string; score: number }> = [];
    if (Array.isArray(softSkillsData)) combined.push(...softSkillsData);
    if (Array.isArray(radarDataFromIa) && radarDataFromIa.length > 0) combined.push(...radarDataFromIa);
    const normalized = processRadarData(combined);
    return normalized;
  }, [softSkillsData, radarDataFromIa]);

  // 1. Portada
  const initials = `${(report?.firstName || '?')[0]}${(report?.lastName || '?')[0]}`.toUpperCase();
  const [isExportingPdf, setIsExportingPdf] = useState(false);
  
  const portada = (
    <div className="report-portada pdf-no-break print-report-section">
      <div className="report-portada-header">
        <img src={logo} alt="Logo EvalúaTE" className="report-portada-logo print-shadow-none" />
        <div className="report-portada-avatar">{initials}</div>
        <div className="report-portada-title">Informe de Empleabilidad</div>
        <div className="report-portada-name">{report?.firstName} {report?.lastName}</div>
        <div className="report-portada-date">{fecha}</div>
        {globalScore != null && (
          <div className="report-portada-score">
            <div className="report-portada-score-label">Puntuación Global</div>
            <div className="report-portada-score-value">
              {globalScore}<span className="report-portada-score-unit">/100</span>
            </div>
          </div>
        )}
      </div>

      {!isExportingPdf && (
        <div className="report-portada-footer print-hidden">
          <button
            onClick={handleDownloadPdf}
            disabled={!iaReport || isExportingPdf}
           className={`px-6 py-3 rounded-lg font-semibold transition-colors flex items-center gap-2 ${!iaReport || isExportingPdf
             ? 'bg-white/20 text-white/50 cursor-not-allowed'
             : 'bg-white text-[#374BA6] hover:bg-[#F0E8D1] dark:bg-[#0D1321] dark:text-[#F2D680] dark:hover:bg-[#1F2937]'
           }`}
          >
            Descargar Informe PDF
          </button>
        </div>
      )} 
    </div>
  );
  // Color de etiquetas del radar según modo (claro/oscuro)
  // Modo claro: etiquetas oscuras para legibilidad contra fondo blanco
  // Modo oscuro: etiquetas blancas para legibilidad contra fondo oscuro
  const [isDarkMode, setIsDarkMode] = useState<boolean>(() => document.documentElement.classList.contains('dark'));
  useEffect(() => {
    const root = document.documentElement;
    const observer = new MutationObserver(() => {
      setIsDarkMode(root.classList.contains('dark'));
    });
    observer.observe(root, { attributes: true, attributeFilter: ['class'] });
    return () => observer.disconnect();
  }, []);
  const radarLabelColor = isDarkMode ? '#FFFFFF' : '#374151';

  const radarMainColor = isDarkMode ? '#F2D680' : '#374BA6';
  const radarBorderColor = isDarkMode ? '#F2D680' : '#374BA6';
  const radarGridColor = isDarkMode ? 'rgba(242, 214, 128, 0.35)' : 'rgba(55, 75, 166, 0.25)';


  const hasAnyRadarValue = useMemo(() => {
    return Array.isArray(radarData) && radarData.some((item: any) => Number(item?.score) > 0);
  }, [radarData]);

  const radar = (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-8 mb-8 print-report-section print-page-break-inside-avoid transition-colors">
      {/* ScoreBadge eliminado */}
      <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-gray-100">Mapa de habilidades</h2>
      <div className="flex flex-col md:flex-row gap-8 items-center">
        <div className="w-full md:w-3/5 h-[26rem] min-h-[26rem]" ref={radarBoxRef}>
          <div className="h-full relative print:hidden">
            {radarData.length > 0 ? (
              <>
                <ResponsiveRadar
                  data={radarData as unknown as Array<Record<string, unknown>>}
                  keys={["score"]}
                  indexBy="softskill"
                  margin={{ top: 50, right: 120, bottom: 50, left: 120 }}
                  maxValue={100}
                  gridLevels={5}
                  theme={{
                    // Asegurar legibilidad de etiquetas en ambos modos
                    text: { fill: radarLabelColor, fontSize: 12 },
                    grid: { line: { stroke: radarGridColor, strokeWidth: 1 } },
                    axis: {
                      ticks: { text: { fill: radarLabelColor, fontSize: 12 } },
                      domain: { line: { stroke: radarGridColor } },
                      legend: { text: { fill: radarLabelColor, fontSize: 12 } },
                    },
                    // Etiquetas del radar (nombres de habilidades)
                    labels: { text: { fill: radarLabelColor, fontSize: 12 } },
                    // Leyendas, en caso de usarse en el futuro
                    legends: { text: { fill: radarLabelColor, fontSize: 12 } },
                    crosshair: { line: { stroke: radarGridColor } },
                  }}
                  borderColor={radarBorderColor}
                  gridLabelOffset={32}
                  dotSize={12}
                  dotColor={radarMainColor}
                  dotBorderWidth={2}
                  dotBorderColor={radarBorderColor}
                  colors={[radarMainColor]}
                  fillOpacity={0.35}
                  blendMode="multiply"
                  animate={true}
                  isInteractive={false}
                  legends={[]}
                />
                {!hasAnyRadarValue && (
                  <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                    <p className="text-gray-500 dark:text-gray-300 text-sm bg-white/60 dark:bg-gray-800/60 px-3 py-1 rounded">
                      Aún no hay datos de habilidades para mostrar
                    </p>
                  </div>
                )}
              </>
            ) : (
              <div className="flex items-center justify-center h-full text-gray-900 dark:text-gray-100">
                <p>No hay datos suficientes para mostrar el gráfico de habilidades</p>
              </div>
            )}
          </div>
          {radarImg && (
            <img src={radarImg} alt="Mapa de habilidades" className="hidden print:block w-full h-[26rem] object-contain" />
          )}
        </div>
        <div className="w-full md:w-1/2 max-h-none">
          <h3 className="font-semibold mb-3 text-gray-900 dark:text-gray-100 text-sm uppercase tracking-wide">Puntuaciones</h3>
          <div className="max-h-none overflow-visible pr-1 space-y-1">
            {radarData.map((item: { softskill: string; score: number }, idx: number) => (
              <div key={idx} className="skill-bar-row">
              <div className="skill-bar-header">
                <span className="skill-bar-label" title={item.softskill}>
                  {item.softskill}
                </span>
                <span className="skill-bar-score">
                  {item.score}%
                </span>
              </div>
            
              <div className="skill-bar-track">
                <div
                  className={`skill-bar-fill ${item.score >= 70 ? 'high' : item.score >= 40 ? 'medium' : 'low'}`}
                  style={{ width: `${item.score}%` }}
                />
              </div>
            </div>
            ))}
          </div>
          <div className="mt-3 pt-2 border-t border-gray-200 dark:border-gray-600">
            <span className="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Puntuación global: </span>
            <span className="text-sm font-bold text-[#166534]">{globalScore ?? '-'}/100</span>
          </div>
        </div>
      </div>
    </div>
  );

  // Ya no se necesitan las secciones hardcodeadas
  // El contenido ahora viene de la IA


  // === NUEVO: función común para renderizar markdown con el mismo estilo ===
  // eslint-disable-next-line @typescript-eslint/no-unused-vars, no-unused-vars
  const renderMarkdown = (content: string) => (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        h1: ({ children, ...props }) => (
          <h1 {...props} className="text-3xl font-bold mb-6 mt-8 pb-2 border-b-2 border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100">
            {children}
          </h1>
        ),
        h2: ({ children, ...props }) => (
          <h2 {...props} className="text-2xl font-semibold mb-4 mt-6 text-gray-900 dark:text-gray-100">
            {children}
          </h2>
        ),
        h3: ({ children, ...props }) => (
          <h3 {...props} className="text-xl font-semibold mb-3 mt-5 text-gray-900 dark:text-gray-100">
            {children}
          </h3>
        ),
        h4: ({ children, ...props }) => (
          <h4 {...props} className="text-lg font-semibold mb-2 mt-4 text-gray-900 dark:text-gray-100">
            {children}
          </h4>
        ),
        ul: ({ children, ...props }) => (
          <ul {...props} className="list-disc list-inside space-y-1 mb-2 text-gray-900 dark:text-gray-100">
            {children}
          </ul>
        ),
        ol: ({ children, ...props }) => (
          <ol {...props} className="list-decimal list-inside space-y-1 mb-2 text-gray-900 dark:text-gray-100">
            {children}
          </ol>
        ),
        li: ({ children, ...props }) => (
          <li {...props} className="leading-relaxed text-gray-900 dark:text-gray-100">
            {children}
          </li>
        ),
        strong: ({ children, ...props }) => (
          <strong {...props} className="font-semibold text-gray-900 dark:text-gray-100">
            {children}
          </strong>
        ),
        em: ({ children, ...props }) => (
          <em {...props} className="italic text-gray-900 dark:text-gray-100">
            {children}
          </em>
        ),
        blockquote: ({ children, ...props }) => (
          <blockquote {...props} className="border-l-4 border-green-600 pl-4 italic text-gray-900 dark:text-gray-100 bg-green-50 dark:bg-green-900/30 py-2 rounded-r">
            {children}
          </blockquote>
        ),
        code: ({ children, ...props }) => (
          <code {...props} className="bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded text-sm font-mono text-gray-900 dark:text-gray-100">
            {children}
          </code>
        ),
        pre: ({ children, ...props }) => {
          // Ocultar el bloque JSON embebido usado solo para extraer radarData
          const toText = (node: any): string => {
            if (node == null) return '';
            if (typeof node === 'string' || typeof node === 'number') return String(node);
            if (Array.isArray(node)) return node.map(toText).join('');
            if (typeof node === 'object' && (node as any)?.props?.children) {
              return toText((node as any).props.children);
            }
            return '';
          };
          const text = toText(children);
          if (/"radarData"\s*:/.test(text)) {
            return null;
          }
          return (
            <pre {...props} className="bg-gray-100 dark:bg-gray-700 p-4 rounded-lg overflow-x-auto text-sm font-mono text-gray-900 dark:text-gray-100 border border-gray-200 dark:border-gray-600">
              {children}
            </pre>
          );
        },
        table: ({ children, ...props }) => (
          <div className="overflow-x-auto mb-4">
            <table {...props} className="min-w-full border-collapse border border-gray-300 dark:border-gray-600">
              {children}
            </table>
          </div>
        ),
        th: ({ children, ...props }) => (
          <th {...props} className="border border-gray-300 dark:border-gray-600 px-4 py-2 bg-gray-50 dark:bg-gray-800 font-semibold text-gray-900 dark:text-gray-100 text-left">
            {children}
          </th>
        ),
        td: ({ children, ...props }) => (
          <td {...props} className="border border-gray-300 dark:border-gray-600 px-4 py-2 text-gray-900 dark:text-gray-100">
            {children}
          </td>
        ),
        a: ({ children, href, ...props }) => (
          <a {...props} href={href} target="_blank" rel="noopener noreferrer" className="text-green-700 dark:text-green-400 hover:text-green-900 dark:hover:text-green-300 underline">
            {children}
          </a>
        ),
        hr: ({ ...props }) => (
          <hr {...props} className="border-t border-gray-300 dark:border-gray-600 my-6" />
        ),
        p: ({ children, ...props }) => {
          const extractText = (node: unknown): string => {
            if (node == null) return '';
            if (typeof node === 'string' || typeof node === 'number') return String(node);
            if (Array.isArray(node)) return node.map(extractText).join('');
            if (typeof node === 'object' && (node as any)?.props?.children) {
              return extractText((node as any).props.children);
            }
            return '';
          };

          const text = extractText(children);
          if (text.includes('★')) {
            if (/(Formato|Claridad|Coherencia|Información clave|Ortografía(?: y estilo)?):\s*[★☆]/.test(text)) {
              const indicators: Array<{ label: string; stars: string }> = [];
              const re = /(Formato|Claridad|Coherencia|Información clave|Ortografía(?: y estilo)?):\s*([★☆]+)/g;
              let m: RegExpExecArray | null;
              // eslint-disable-next-line no-cond-assign
              while ((m = re.exec(text)) !== null) {
                const rawLabel = m[1];
                if (rawLabel && m[2]) {
                  const normLabel = rawLabel.startsWith('Ortografía') ? 'Ortografía' : rawLabel;
                  indicators.push({ label: normLabel, stars: m[2] });
                }
              }
              return (
                <div {...props} className="quality-indicators">
                  <ul className="text-gray-900 dark:text-gray-100 leading-relaxed space-y-1">
                    {indicators.length > 0 ? indicators.map((it, idx) => {
                      const starMatch = it.stars.match(/(★+)(☆*)/);
                      const filledStars = starMatch ? starMatch[1] : '';
                      const emptyStars = starMatch ? starMatch[2] : '';
                      return (
                        <li key={idx} className="flex items-center gap-2">
                          <span className="font-semibold text-gray-900 dark:text-gray-100">{it.label}:</span>
                          <span>
                            <span className="star-filled">{filledStars}</span>
                            <span className="star-empty">
                              {emptyStars}
                            </span>
                          </span>
                        </li>
                      );
                    }) : (
                      <li className="text-gray-900 dark:text-gray-100">{text}</li>
                    )}
                  </ul>
                </div>
              );
            } else {
              const parts = text.split(/((?:★+)(?:☆*))/g);
              return (
                <p {...props} className="text-gray-900 dark:text-gray-100 leading-relaxed mb-4 text-justify">
                  {parts.map((part, index) => {
                    const starMatch = part.match(/(★+)(☆*)/);
                    if (starMatch) {
                      const [, filledStars, emptyStars] = starMatch;
                      if (filledStars && emptyStars) {
                        const filledCount = filledStars.length;
                        const totalCount = filledCount + emptyStars.length;
                        const percentage = (filledCount / totalCount) * 100;
                        let colorClass = 'star-very-poor';
                        if (percentage >= 90) colorClass = 'star-excellent';
                        else if (percentage >= 80) colorClass = 'star-very-good';
                        else if (percentage >= 70) colorClass = 'star-good';
                        else if (percentage >= 60) colorClass = 'star-average';
                        else if (percentage >= 50) colorClass = 'star-regular';
                        else if (percentage >= 40) colorClass = 'star-below-average';
                        else if (percentage >= 30) colorClass = 'star-poor';
                        else colorClass = 'star-very-poor';
                        return (
                          <span key={index}>
                            <span className={`${colorClass} star-filled`}>
                              {filledStars}
                            </span>
                            <span className="star-empty">
                              {emptyStars}
                            </span>
                          </span>
                        );
                      }
                    }
                    return part;
                  })}
                </p>
              );
            }
          }
          return (
            <p {...props} className="text-gray-900 dark:text-gray-100 leading-relaxed mb-4 text-justify">
              {children}
            </p>
          );
        },
      }}
    >
      {content}
    </ReactMarkdown>
  );

  // === NUEVO: dividir el markdown para insertar el análisis justo después de "Áreas de mejora" ===
  // eslint-disable-next-line @typescript-eslint/no-unused-vars, no-unused-vars
  const splitReport = useMemo(() => {
    if (!iaReport) return { before: '', improvements: '', after: '' };

    // 0) Eliminar cualquier sección generada por IA de "Análisis del CV" para evitar duplicados
    const stripCvAnalysisSections = (text: string): string => {
      if (!text) return text;
      // Coincide títulos como: "## 6. Análisis del CV con puntuación 1–5" o "## Análisis del CV (...)"
      const cvAnalysisSection = /(\n|^)#{1,6}\s*(?:\d+\.\s*)?Análisis del CV(?:\s*\([^)]*\))?[\s\S]*?(?=(\n#{1,6}\s)|$)/g;
      return text.replace(cvAnalysisSection, '\n');
    };

    const cleaned = stripCvAnalysisSections(iaReport);

    // 1) Cortar "Áreas de mejora"
    const headerRegex = /(\n|^)#\s*[^\n]*Áreas de mejora[^\n]*\n/;
    const match = cleaned.match(headerRegex);
    if (!match || match.index == null) return { before: '', improvements: '', after: cleaned };
    const headerIndex = match.index;
    const afterHeaderIndex = headerIndex + match[0].length;
    const nextHeader = /\n#[^\n]*/g;
    nextHeader.lastIndex = afterHeaderIndex;
    const nextMatch = nextHeader.exec(cleaned);
    const endIndex = nextMatch ? nextMatch.index : cleaned.length;

    const before = cleaned.slice(0, headerIndex);
    const improvements = cleaned.slice(headerIndex, endIndex);
    let after = cleaned.slice(endIndex);

    // 2) Asegurar de nuevo: eliminar cualquier resto de sección de Análisis del CV
    const analysisHeader = /(\n|^)##\s*\d+\.\s*Análisis del CV con puntuación 1–5[\s\S]*?(?=\n##\s|$)/;
    after = stripCvAnalysisSections(after).replace(analysisHeader, '\n');

    return { before, improvements, after };
  }, [iaReport]);
  void renderMarkdown;
  void splitReport;

  const renderStructuredReport = (data: NewReportSchema) => {
    const pd = data.personal_data || {} as PersonalData;
    const cvx = data.cv_analysis || {} as CvAnalysis;
    const details = data.cv_details || { experience: [], education: [], languages: [], tools: [] };
    const jobPrefs = data.job_preferences as NormalizedJobPreferences;

    // Obtener LinkedIn desde cv_analysis.contact.linkedin o personal.jobPreferences.linkedin
    const linkedInFromCv = (cvx as any)?.contact?.linkedin || (cvx as any)?.cv_structured?.contact?.linkedin;
    const linkedInFromPrefs = (personal?.jobPreferences as any)?.linkedin;
    const linkedIn = linkedInFromCv || linkedInFromPrefs;
    const formatStars = (n?: number) => <StarsGold n={asStars(Number(n ?? 0))} />;
    const renderList = (items?: string[]) => (
      <ul className="list-disc list-inside space-y-1 text-gray-900 dark:text-gray-100">
        {(items || []).filter(Boolean).map((it, idx) => (<li key={idx}>{it}</li>))}
      </ul>
    );
    const formatCvItems = (items?: Array<{ title?: string; subtitle?: string; period?: string; level?: string; detail?: string }>) =>
      (items || []).map((it) => {
        const rawParts = [it.title, it.subtitle, it.period, it.level, it.detail]
          .map((part) => (part || '').trim())
          .filter(Boolean);

        const deduped = rawParts.reduce<string[]>((acc, current) => {
          const normalized = current.toLowerCase();
          if (!acc.some((existing) => existing.toLowerCase() === normalized)) {
            acc.push(current);
          }
          return acc;
        }, []);

        return (deduped.join(' — ') || '').trim();
      }).filter(Boolean);

    return (
      <div className="space-y-0">
        <section className="report-section">
          <h2 className="report-section-title">Resumen ejecutivo</h2>
          <div className="text-gray-700 dark:text-gray-200 leading-relaxed text-justify">
            {renderMarkdown(data.profile_summary || data.summary || '')}
          </div>
        </section>

        <section className="report-section">
          <h2 className="report-section-title">Datos personales</h2>
          <div className="personal-data-grid">
            {[
              ['Nombre', pd.name || 'No consta'],
              ['Ubicación', pd.location || 'No consta'],
              ['Email', pd.email || 'No consta'],
              ['Teléfono', pd.phone || 'No especificado'],
              ['LinkedIn', linkedIn || 'No consta'],
              ['Certificado discapacidad', pd.disability_certificate || 'No especificado'],
            ].map(([label, value]) => (
              <div key={label} className="personal-data-item">
                <span className="personal-data-label">{label}</span>
                <span className="personal-data-value">{value}</span>
              </div>
            ))}
          </div>
        </section>

        <section className="report-section">
          <h2 className="report-section-title">Resumen del CV</h2>
          <div className="text-gray-700 dark:text-gray-200 leading-relaxed text-justify mb-4">
            {renderMarkdown(data.cv_analysis_summary || '')}
          </div>
          <div className="space-y-3">
            {details.experience?.length ? (
              <div>
                <h3 className="text-sm font-bold uppercase tracking-wide text-gray-500 dark:text-gray-400 mb-1.5">Experiencia</h3>
                {renderList(formatCvItems(details.experience))}
              </div>
            ) : null}
            {details.education?.length ? (
              <div>
                <h3 className="text-sm font-bold uppercase tracking-wide text-gray-500 dark:text-gray-400 mb-1.5">Formación</h3>
                {renderList(formatCvItems(details.education))}
              </div>
            ) : null}
            {details.languages?.length ? (
              <div>
                <h3 className="text-sm font-bold uppercase tracking-wide text-gray-500 dark:text-gray-400 mb-1.5">Idiomas</h3>
                {renderList(formatCvItems(details.languages))}
              </div>
            ) : null}
            {details.tools?.length ? (
              <div>
                <h3 className="text-sm font-bold uppercase tracking-wide text-gray-500 dark:text-gray-400 mb-1.5">Herramientas / Software</h3>
                {renderList(formatCvItems(details.tools))}
              </div>
            ) : null}
          </div>
        </section>

        <section className="report-section">
          <h2 className="report-section-title">Fortalezas clave</h2>
          <div className="strength-tags-grid">
            {((data.strengths as string[]) || []).filter(Boolean).map((s, i) => (
              <span key={i} className="strength-tag">{s}</span>
            ))}
          </div>
        </section>

        <section className="report-section">
          <h2 className="report-section-title">Áreas de mejora priorizadas</h2>
          <div className="improvement-cards">
            {(data.improvement_areas || []).map((it, idx) => (
              <div key={idx} className="improvement-card">
                <div className="improvement-area">⚡ {it.area}</div>
                <div className="improvement-reason"> {String(it.reason || '').split('-> Acción:')[0]} </div>
                {(it.suggested_action || String(it.reason || '').includes('-> Acción:')) && (
                  <div className="improvement-action"> → Acción: {it.suggested_action || String(it.reason || '').split('-> Acción:')[1]} </div>
                )}
              </div>
            ))}
          </div>
        </section>

        <section className="report-section print-page-break-inside-avoid">
            <h2 className="report-section-title">Análisis del CV (con puntuación 1–5 por apartado)</h2>

            <div className="cv-score-grid mb-4">
              <div className="cv-score-item">
                <div className="cv-score-label">Formato</div>
                <div className="cv-score-stars">{formatStars(cvx.structure_score ?? 0)}</div>
                <div className="cv-score-number">{cvx.structure_score ?? 0}/5</div>
              </div>
              <div className="cv-score-item">
                <div className="cv-score-label">Claridad</div>
                <div className="cv-score-stars">{formatStars(cvx.clarity_score ?? 0)}</div>
                <div className="cv-score-number">{cvx.clarity_score ?? 0}/5</div>
              </div>
              <div className="cv-score-item">
                <div className="cv-score-label">Coherencia</div>
                <div className="cv-score-stars">{formatStars(cvx.coherence_score ?? 0)}</div>
                <div className="cv-score-number">{cvx.coherence_score ?? 0}/5</div>
              </div>
              <div className="cv-score-item">
                <div className="cv-score-label">Información clave</div>
                <div className="cv-score-stars">{formatStars(cvx.key_info_score ?? 0)}</div>
                <div className="cv-score-number">{cvx.key_info_score ?? 0}/5</div>
              </div>
              <div className="cv-score-item">
                <div className="cv-score-label">Ortografía</div>
                <div className="cv-score-stars">{formatStars(cvx.style_score ?? 0)}</div>
                <div className="cv-score-number">{cvx.style_score ?? 0}/5</div>
              </div>
            </div>

            {/* Observaciones del análisis */}
            {cvx.evidence && (
              <div className="mb-4">
                <p className="font-semibold mb-2 text-gray-900 dark:text-gray-100">Observaciones del análisis:</p>
                <ul className="list-disc list-inside space-y-1 text-gray-900 dark:text-gray-100">
                  {cvx.evidence.structure && (
                    <li className="text-gray-900 dark:text-gray-100"><strong className="font-semibold">Formato:</strong> {cvx.evidence.structure}</li>
                  )}
                  {cvx.evidence.coherence && (
                    <li className="text-gray-900 dark:text-gray-100"><strong className="font-semibold">Coherencia:</strong> {cvx.evidence.coherence}</li>
                  )}
                  {cvx.evidence.key_info && (
                    <li className="text-gray-900 dark:text-gray-100"><strong className="font-semibold">Información clave:</strong> {cvx.evidence.key_info}</li>
                  )}
                  {cvx.evidence.clarity && (
                    <li className="text-gray-900 dark:text-gray-100"><strong className="font-semibold">Claridad:</strong> {cvx.evidence.clarity}</li>
                  )}
                  {cvx.evidence.style && (
                    <li className="text-gray-900 dark:text-gray-100"><strong className="font-semibold">Ortografía y estilo:</strong> {cvx.evidence.style}</li>
                  )}
                </ul>
              </div>
            )}

            {/* Correcciones/Acciones sugeridas */}
            {cvx.corrections && Array.isArray(cvx.corrections) && cvx.corrections.length > 0 && (
              <div className="mb-4">
                <p className="font-semibold mb-2 text-gray-900 dark:text-gray-100">Correcciones/Acciones:</p>
                <ul className="list-disc list-inside space-y-1 text-gray-900 dark:text-gray-100">
                  {cvx.corrections.map((correction, i) => (
                    <li key={i} className={`text-gray-900 dark:text-gray-100 ${i === 0 ? 'mt-0' : ''}`}>{correction}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Reordenación sugerida */}
            {cvx.reordering_suggestions && Array.isArray(cvx.reordering_suggestions) && cvx.reordering_suggestions.length > 0 && (
              <div className="mb-4">
                <p className="font-semibold mb-2 text-gray-900 dark:text-gray-100">Reordenación sugerida:</p>
                <ul className="list-disc list-inside space-y-1 text-gray-900 dark:text-gray-100">
                  {cvx.reordering_suggestions.map((suggestion, i) => (
                    <li key={i} className={`text-gray-900 dark:text-gray-100 ${i === 0 ? 'mt-0' : ''}`}>{suggestion}</li>
                  ))}
                </ul>
              </div>
            )}
          </section>

        <section className="report-section">
          <h2 className="report-section-title">Entornos de trabajo ideales</h2>
          <div className="text-gray-700 dark:text-gray-200 leading-relaxed mb-3">
            {renderMarkdown(data.ideal_work_environment || 'No consta')}
          </div>
          {(jobPrefs?.areas?.length || jobPrefs?.work_mode) && (
            <div className="flex flex-wrap gap-2 mt-2">
              {jobPrefs?.areas?.map((area, i) => (
                <span key={i} className="strength-tag">{area}</span>
              ))}
              {jobPrefs?.work_mode && (
                <span className="strength-tag" style={{ background: '#F0FDF4', color: '#166534', borderColor: '#86efac' }}>
                  {jobPrefs.work_mode}
                </span>
              )}
            </div>
          )}
        </section>

        {(() => {
          // Roles normalizados (reportConfig) + posibles roles adicionales del backend (cv_analysis.suggested_roles / roles con fit_score)
          const rolesFromReport = Array.isArray(data.suggested_roles) ? data.suggested_roles : [];
          const cvxAny = data.cv_analysis as any;
          const cvSuggestedRaw = Array.isArray(cvxAny?.suggested_roles)
            ? cvxAny.suggested_roles
            : Array.isArray(cvxAny?.roles)
              ? cvxAny.roles
              : [];

          const normalizeBackendRole = (r: any) => {
            const name =
              r?.role ||
              r?.name ||
              r?.title ||
              r?.label ||
              r?.position ||
              r?.jobTitle ||
              '';
            const roleName = String(name ?? '').trim();
            if (!roleName) return null;

            const fitScore =
              typeof r?.fit_score === 'number' && !Number.isNaN(r.fit_score)
                ? r.fit_score
                : undefined;

            const matched =
              Array.isArray(r?.matched_skills) && r.matched_skills.length
                ? r.matched_skills.map((x: any) => String(x ?? '').trim()).filter(Boolean)
                : [];

            const fitReasonRaw = String(r?.fit_reason ?? r?.fit_by_skills ?? '').trim();
            const preferenceReasonRaw = String(r?.preference_reason ?? '').trim();

            return {
              role: roleName,
              seniority: String(r?.seniority ?? '').trim(),
              remote_viable:
                typeof r?.remote_viable === 'boolean' ? Boolean(r.remote_viable) : false,
              reason: String(r?.reason ?? '').trim(),
              fit_by_skills: fitReasonRaw || undefined,
              matched_skills: matched.length ? matched : undefined,
              // Campos adicionales solo usados en el frontend para ordenar y desglosar motivos
              fit_score: fitScore,
              preference_reason: preferenceReasonRaw || undefined,
            };
          };

          const backendRoles = cvSuggestedRaw
            .map(normalizeBackendRole)
            .filter((r: any) => r && r.role) as any[];

          // Combinar y desduplicar por nombre de rol y seniority
          const combinedMap = new Map<string, any>();
          const addRole = (r: any) => {
            if (!r || !r.role) return;
            const key = `${r.role}`.toLowerCase() + `|${(r.seniority || '').toLowerCase()}`;
            if (!combinedMap.has(key)) {
              combinedMap.set(key, r);
            }
          };
          rolesFromReport.forEach(addRole);
          backendRoles.forEach(addRole);

          const roles: any[] = Array.from(combinedMap.values());
          if (roles.length === 0) return null;

          const validated = roles.filter((r) => {
            const fitScore =
              typeof (r as any).fit_score === 'number' && !Number.isNaN((r as any).fit_score);
            const hasSkills =
              (r.fit_by_skills && String(r.fit_by_skills).trim()) ||
              (Array.isArray(r.matched_skills) && r.matched_skills.length > 0);
            return fitScore || hasSkills;
          });

          const preferencesOnly = roles.filter((r) => !validated.includes(r));

          const sortedValidated = [...validated].sort((a, b) => {
            const aScore = typeof a.fit_score === 'number' ? a.fit_score : 0;
            const bScore = typeof b.fit_score === 'number' ? b.fit_score : 0;
            if (aScore !== bScore) return bScore - aScore;
            const aCount = a.matched_skills?.length || 0;
            const bCount = b.matched_skills?.length || 0;
            return bCount - aCount;
          });


          const getBadge = (role: any) => {
            const score = typeof role.fit_score === 'number' ? role.fit_score : (role.matched_skills?.length || 0) * 20;
            if (score >= 80) return { cls: 'high', label: 'Muy buen encaje' };
            if (score >= 60) return { cls: 'medium', label: 'Encaje razonable' };
            return { cls: 'low', label: 'Encaje inicial' };
          };

          return (
            <section className="report-section">
              <h2 className="report-section-title">Roles sugeridos</h2>

              {sortedValidated.length > 0 && (
                <div className="mb-4">
                  <p className="text-xs font-bold uppercase tracking-wide text-gray-400 mb-2">Validados por encaje con tu perfil</p>
                  <div className="roles-grid">
                    {sortedValidated.map((role, idx) => {
                      const { cls, label } = getBadge(role);
                      const fitScore = typeof role.fit_score === 'number' ? role.fit_score : 0;
                      return (
                        <div key={`validated-${idx}`} className="role-card">
                          <div className="role-card-header">
                            <div className="role-card-name">{role.role}</div>
                            <span className={`role-card-badge ${cls}`}>{label}</span>
                          </div>
                          {(role.seniority || typeof role.remote_viable === 'boolean') && (
                            <div className="role-card-meta">
                              {role.seniority && <span>{role.seniority}</span>}
                              {typeof role.remote_viable === 'boolean' && (
                                <span>{role.seniority ? ' · ' : ''}{role.remote_viable ? '100% remoto' : 'Presencial/Híbrido'}</span>
                              )}
                            </div>
                          )}
                          {fitScore > 0 && (
                            <div className="role-fit-bar">
                              <div className="role-fit-fill" style={{ width: `${fitScore}%` }} />
                            </div>
                          )}
                          {role.fit_by_skills && (
                            <div className="role-card-reason">{role.fit_by_skills}</div>
                          )}
                          {Array.isArray(role.matched_skills) && role.matched_skills.length > 0 && (
                            <div className="role-card-skills">
                              {role.matched_skills.map((skill: string, si: number) => (
                                <span key={si} className="role-skill-tag">{skill}</span>
                              ))}
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {preferencesOnly.length > 0 && (
                <div>
                  <p className="text-xs font-bold uppercase tracking-wide text-gray-400 mb-2">Según tus preferencias</p>
                  <div className="roles-grid">
                    {preferencesOnly.map((role, idx) => (
                      <div key={`pref-${idx}`} className="role-card">
                        <div className="role-card-header">
                          <div className="role-card-name">{role.role}</div>
                          <span className="role-card-badge low">Por preferencia</span>
                        </div>
                        {(role.seniority || typeof role.remote_viable === 'boolean') && (
                          <div className="role-card-meta">
                            {role.seniority && <span>{role.seniority}</span>}
                            {typeof role.remote_viable === 'boolean' && (
                              <span>{role.seniority ? ' · ' : ''}{role.remote_viable ? '100% remoto' : 'Presencial/Híbrido'}</span>
                            )}
                          </div>
                        )}
                        {role.reason && <div className="role-card-reason">{role.reason}</div>}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </section>
          );
        })()}

        <section className="report-section">
          <h2 className="report-section-title">Plan de acción</h2>
          <div className="plan-timeline">
            <div className="plan-phase short">
              <div className="plan-phase-title">Corto plazo · 0–30 días</div>
              <ul className="plan-phase-list">
                {((data.action_plan?.short_term as string[]) || []).filter(Boolean).map((s, i) => (
                  <li key={i}>{s}</li>
                ))}
              </ul>
            </div>
            <div className="plan-phase medium">
              <div className="plan-phase-title">Medio plazo · 1–3 meses</div>
              <ul className="plan-phase-list">
                {((data.action_plan?.medium_term as string[]) || []).filter(Boolean).map((s, i) => (
                  <li key={i}>{s}</li>
                ))}
              </ul>
            </div>
            <div className="plan-phase long">
              <div className="plan-phase-title">Largo plazo · 3–6+ meses</div>
              <ul className="plan-phase-list">
                {((data.action_plan?.long_term as string[]) || []).filter(Boolean).map((s, i) => (
                  <li key={i}>{s}</li>
                ))}
              </ul>
            </div>
          </div>
        </section>

        <section className="report-section">
          <h2 className="report-section-title">Estrategias de búsqueda de empleo</h2>
          <h3 className="font-semibold text-gray-900 dark:text-gray-100">Optimización del CV</h3>
          {renderList(data.job_search_advice?.cv_optimization as string[])}
          {data.job_search_advice?.letters_portfolio?.length ? (
            <>
              <h3 className="font-semibold text-gray-900 dark:text-gray-100 mt-3">Cartas y portfolio/casos</h3>
              {renderList(data.job_search_advice.letters_portfolio as string[])}
            </>
          ) : null}
          {data.job_search_advice?.recommended_platforms?.length ? (
            <>
              <h3 className="font-semibold text-gray-900 dark:text-gray-100 mt-3">Plataformas</h3>
              {renderList(data.job_search_advice.recommended_platforms as string[])}
            </>
          ) : null}
          {data.job_search_advice?.networking?.length ? (
            <>
              <h3 className="font-semibold text-gray-900 dark:text-gray-100 mt-3">Networking dirigido</h3>
              {renderList(data.job_search_advice.networking as string[])}
            </>
          ) : null}
          {data.job_search_advice?.interview_tips?.length ? (
            <>
              <h3 className="font-semibold text-gray-900 dark:text-gray-100 mt-3">Entrevistas</h3>
              {renderList(data.job_search_advice.interview_tips as string[])}
            </>
          ) : null}
        </section>

        <section className="report-section">
          <h2 className="report-section-title">Resultados de minijuegos</h2>
          {renderList(((data.completed_games as string[]) || []).map(getPrettyGameName))}
        </section>

        <section className="report-section">
          <h2 className="report-section-title">Herramientas útiles</h2>
          <div className="space-y-3">
            {data.useful_tools?.productivity?.length ? (
              <div>
                <h3 className="text-sm font-bold uppercase tracking-wide text-gray-400 mb-1.5">Productividad</h3>
                {renderList(data.useful_tools.productivity as string[])}
              </div>
            ) : null}
            {data.useful_tools?.job_search?.length ? (
              <div>
                <h3 className="text-sm font-bold uppercase tracking-wide text-gray-400 mb-1.5">Búsqueda de empleo</h3>
                {renderList(data.useful_tools.job_search as string[])}
              </div>
            ) : null}
            {data.useful_tools?.learning?.length ? (
              <div>
                <h3 className="text-sm font-bold uppercase tracking-wide text-gray-400 mb-1.5">Aprendizaje</h3>
                {renderList(data.useful_tools.learning as string[])}
              </div>
            ) : null}
            {data.useful_tools?.accessibility?.length ? (
              <div>
                <h3 className="text-sm font-bold uppercase tracking-wide text-gray-400 mb-1.5">Accesibilidad</h3>
                {renderList(data.useful_tools.accessibility as string[])}
              </div>
            ) : null}
          </div>
        </section>

        <section className="report-section" style={{ borderBottom: 'none' }}>
          <h2 className="report-section-title">Mensaje final</h2>
          <div className="final-message-box">
            {renderMarkdown(data.final_message || '')}
          </div>
        </section>
      </div>
    );
  };

  // Renderizado final
  return (
    <section className="max-w-4xl mx-auto p-4 print:p-0 print:max-w-none">

      {/* Mensaje de error (solo si no hay informe generado) */}
      {errorIa && !iaReport && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg shadow-md p-6 mb-8" role="alert">
          <strong className="font-bold text-gray-900 dark:text-gray-100">Aviso.</strong>
          <span className="block sm:inline text-gray-900 dark:text-gray-100"> {errorIa}</span>
          <div className="mt-4">
            <button
              onClick={handleRetry}
              className="bg-green-700 hover:bg-green-800 text-white font-bold py-2 px-4 rounded"
            >
              Reintentar
            </button>
          </div>
        </div>
      )}
      <div ref={reportRef} className="pdf-export-area bg-white dark:bg-[#1e293b]">
        {/* Contenido del informe que no depende de la IA */}
        
        {portada}
        {radar}
        
        <div className="pdf-content-wrapper bg-white rounded-lg shadow-md p-6 md:p-8 mb-8 print:bg-white print:shadow-none print:p-0">
          {/* Informe de la IA y formulario de feedback */}
          {/* Estado iaReport disponible para debug en desarrollo */}

          {/* Estado de carga EXPLÍCITO */}
          {loadingIa && (
            <div className="flex flex-col items-center justify-center p-12 bg-white dark:bg-gray-800 rounded-lg shadow-md mb-8 transition-colors">
             <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-green-600 mb-4"></div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100 animate-pulse">Generando tu Informe de Empleabilidad...</h3>
              <p className="text-gray-600 dark:text-gray-400 mt-2 text-center max-w-md">
               El equipo de Teamworkz está analizando tu perfil, tus resultados de juego y tus preferencias para crear un plan personalizado.
                Esto puede tardar unos segundos.
             </p>
            </div>
          )}

          {/* SOLUCIÓN: Mostrar informe básico si no hay iaReport después de cargar */}
          {!loadingIa && !iaReport && !errorIa && (
            <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded-lg shadow-md p-6 mb-8" role="alert">
              <strong className="font-bold text-gray-900">Informe básico disponible.</strong>
              <span className="block sm:inline text-gray-900"> Tu informe está siendo procesado. Mientras tanto, aquí tienes un resumen de tus resultados.</span>

              <div className="mt-4 bg-white rounded-lg p-4 transition-colors">
                <h3 className="text-lg font-semibold mb-2 text-gray-900">Resumen de Evaluación</h3>
                <p className="text-gray-900"><strong>Nombre:</strong> {report?.firstName} {report?.lastName}</p>
                <p className="text-gray-900"><strong>Puntaje de empleabilidad:</strong> {globalScore ?? info?.employability_score ?? report?.employabilityScore ?? 'Calculando...'}</p>

                <p className="mt-3 text-sm text-gray-900">
                Actualiza esta página en unos segundos para ver el informe completo.
                </p>
              </div>
            </div>
          )}
          
      
          {(reportForRender || info) && renderStructuredReport(reportForRender || info!)}

          {finalPhrase && (
            <div
              className="rounded-xl p-6 my-8 shadow-sm border-2 bg-blue-100 border-blue-200 text-gray-900 print:bg-white print:text-black dark:bg-white dark:border-gray-400 dark:text-black"
              role="note"
            >
              <p className="mb-0 leading-relaxed">
                {finalPhrase}
              </p>
            </div>
        )}
      </div>
    </div>

    {!feedbackSent && (
      <div className="bg-white text-gray-900 rounded-lg shadow-md p-6 mb-8 print-hidden dark:bg-transparent dark:text-white dark:border dark:border-gray-500">
        <form onSubmit={handleFeedbackSubmit}>
          <label className="block mb-2 font-semibold dark:text-white">¿Te resultó útil este informe?</label>
          <div className="flex gap-4 mb-4">
            <label className="flex items-center gap-2 px-3 py-1 rounded-full border border-gray-300 bg-white dark:bg-transparent dark:border-gray-500">                <input className="w-5 h-5" type="radio" name="rating" value="útil" required checked={feedback.rating === 'útil'} onChange={e => setFeedback(f => ({ ...f, rating: e.target.value }))} />
                 <span className="min-w-[3.5rem] text-center text-gray-900 dark:text-white">Útil</span>
            </label>
            <label className="flex items-center gap-2 px-3 py-1 rounded-full border border-gray-300 bg-white dark:bg-transparent dark:border-gray-500">
              <input className="w-5 h-5" type="radio" name="rating" value="no útil" required checked={feedback.rating === 'no útil'} onChange={e => setFeedback(f => ({ ...f, rating: e.target.value }))} />
              <span className="min-w-[5rem] text-center text-gray-900 dark:text-white">No útil</span>
            </label>
          </div>
          <label className="block mb-1 text-gray-900 dark:text-white">¿Algún comentario o sugerencia?</label>
          <textarea className="w-full border rounded p-2 mb-2 bg-white text-gray-900 border-gray-300 dark:bg-transparent dark:text-white dark:border-gray-500" rows={2} value={feedback.comment} onChange={e => setFeedback(f => ({ ...f, comment: e.target.value }))} />
          {feedbackError && <p className="text-red-400 mb-2">{feedbackError}</p>}
           <button type="submit" className="bg-[#374BA6] text-white px-4 py-2 rounded hover:bg-[#5063BA] focus:outline-none focus:ring-4 focus:ring-[#8095F2]">Enviar feedback</button>
        </form>
      </div>
    )}

    {feedbackSent && (
      <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded-lg shadow-md p-6 mb-8 print-hidden" role="alert">
         <p className="font-semibold">¡Gracias por tu feedback!</p>
      </div>
    )}
    
    </section>
  );
};

export default ResultadosPage;
