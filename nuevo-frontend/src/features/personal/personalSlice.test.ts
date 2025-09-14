import test from 'node:test';
import assert from 'node:assert/strict';
import { personalSlice, saveCvAnalysis, saveSoftSkills, generateFinalReport } from './personalSlice.ts';
import type { CvAnalysis } from '@/types/report';

test('saveCvAnalysis stores structured analysis', () => {
  const initialState = personalSlice.getInitialState();
  const analysis: CvAnalysis = {
    structure_score: 3,
    coherence_score: 4,
    key_info_score: 5,
    clarity_score: 4,
    style_score: 3,
    evidence: {
      structure: 'estructura',
      coherence: 'coherencia',
      key_info: 'informacion',
      clarity: 'claridad',
      style: 'estilo',
    },
    corrections: ['Agregar más detalles en experiencia'],
    reordering_suggestions: ['Mover habilidades al inicio'],
    contact: { emails: ['test@example.com'], phones: ['123'] },
    experience_detailed: [{ title: 'Dev', company: 'Acme' }],
    education_detailed: [{ degree: 'Ing', institution: 'Uni' }],
    software: [{ name: 'Excel', level: 'básico' }],
  };
  const state = personalSlice.reducer(initialState, saveCvAnalysis(analysis));
  assert.deepEqual(state.cvAnalysis, analysis);
});

test('generateFinalReport includes CvAnalysis in report', () => {
  let state = personalSlice.getInitialState();
  const analysis: CvAnalysis = {
    structure_score: 5,
    coherence_score: 5,
    key_info_score: 5,
    clarity_score: 5,
    style_score: 5,
    evidence: {
      structure: 'ok',
      coherence: 'ok',
      key_info: 'ok',
      clarity: 'ok',
      style: 'ok',
    },
    corrections: [],
    reordering_suggestions: [],
  };

  state = personalSlice.reducer(state, saveCvAnalysis(analysis));
  state = personalSlice.reducer(state, saveSoftSkills([
    { skill: 'comunicacion', score: 80, level: 'alto', confidence: 90 },
  ]));

  state = personalSlice.reducer(state, generateFinalReport());
  assert.deepEqual(state.report?.cvAnalysis, analysis);
});
