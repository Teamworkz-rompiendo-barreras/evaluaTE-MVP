import test from 'node:test';
import assert from 'node:assert/strict';
import { personalSlice, saveCvAnalysis } from './personalSlice.ts';
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
  };
  const state = personalSlice.reducer(initialState, saveCvAnalysis(analysis));
  assert.deepEqual(state.cvAnalysis, analysis);
});
