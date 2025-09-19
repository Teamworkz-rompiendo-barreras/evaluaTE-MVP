import test from 'node:test';
import assert from 'node:assert/strict';
import {
  personalSlice,
  saveCvAnalysis,
  saveSoftSkills,
  generateFinalReport,
  addSceneDecision,
} from './personalSlice.ts';
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

test('addSceneDecision creates a new log entry', () => {
  let state = personalSlice.getInitialState();

  const decision = {
    sceneId: 1,
    stepIndex: 0,
    optionText: 'test',
    isCorrect: true,
    skillImpacts: { test: 0.8 },
    timestamp: '2023-01-01T00:00:00Z',
    userAgent: 'jest',
    screenResolution: '800x600',
  };

  state = personalSlice.reducer(state, addSceneDecision(decision));
  assert.equal(state.logs.length, 1);

  const firstLog = state.logs[0];
  assert(firstLog);
  assert.equal(firstLog.decisions.length, 1);
});

test('addSceneDecision appends to existing log', () => {
  let state = personalSlice.getInitialState();

  const decision1 = {
    sceneId: 2,
    stepIndex: 0,
    optionText: 'first',
    isCorrect: true,
    skillImpacts: { first: 0.5 },
    timestamp: '2023-01-01T00:00:00Z',
    userAgent: 'jest',
    screenResolution: '800x600',
  };

  const decision2 = {
    sceneId: 2,
    stepIndex: 1,
    optionText: 'second',
    isCorrect: false,
    skillImpacts: { second: 0.2 },
    timestamp: '2023-01-01T00:00:01Z',
    userAgent: 'jest',
    screenResolution: '800x600',
  };

  state = personalSlice.reducer(state, addSceneDecision(decision1));
  state = personalSlice.reducer(state, addSceneDecision(decision2));
  assert.equal(state.logs.length, 1);

  const firstLog = state.logs[0];
  assert(firstLog);
  assert.equal(firstLog.decisions.length, 2);
});
