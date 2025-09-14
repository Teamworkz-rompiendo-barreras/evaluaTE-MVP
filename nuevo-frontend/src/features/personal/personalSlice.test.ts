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
import type { UserDecision } from '@/types/skills';

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

test('addSceneDecision stores decisions in state.logs', () => {
  let state = personalSlice.getInitialState();
  const decision: UserDecision = {
    sceneId: 1,
    stepIndex: 0,
    optionText: 'Opción A',
    isCorrect: true,
    skillImpacts: { 'Opción A': 0.8 },
    timestamp: '2024-01-01T00:00:00Z',
    userAgent: 'test',
    screenResolution: '1920x1080',
  };
  state = personalSlice.reducer(state, addSceneDecision(decision));
  assert.equal(state.logs.length, 1);
  assert.deepEqual(state.logs[0].decisions[0], decision);
});

test('addSceneDecision appends to existing scene log', () => {
  let state = personalSlice.getInitialState();
  const decision1: UserDecision = {
    sceneId: 1,
    stepIndex: 0,
    optionText: 'Opción A',
    isCorrect: true,
    skillImpacts: { 'Opción A': 0.8 },
    timestamp: '2024-01-01T00:00:00Z',
    userAgent: 'test',
    screenResolution: '1920x1080',
  };
  const decision2: UserDecision = {
    sceneId: 1,
    stepIndex: 1,
    optionText: 'Opción B',
    isCorrect: false,
    skillImpacts: { 'Opción B': 0.5 },
    timestamp: '2024-01-01T00:01:00Z',
    userAgent: 'test',
    screenResolution: '1920x1080',
  };
  state = personalSlice.reducer(state, addSceneDecision(decision1));
  state = personalSlice.reducer(state, addSceneDecision(decision2));
  assert.equal(state.logs.length, 1);
  assert.equal(state.logs[0].decisions.length, 2);
});
