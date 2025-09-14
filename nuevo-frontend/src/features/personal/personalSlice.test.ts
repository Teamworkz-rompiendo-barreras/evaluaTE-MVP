import test from 'node:test';
import assert from 'node:assert/strict';
import { personalSlice, saveCvAnalysis, saveSoftSkills, generateFinalReport, addSceneDecision } from './personalSlice.ts';
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

test('addSceneDecision persists decisions in logs', () => {
  const initialState = personalSlice.getInitialState();
  const decision1: UserDecision = {
    sceneId: 1,
    stepIndex: 0,
    optionText: 'Option A',
    isCorrect: true,
    skillImpacts: { test: 0.8 },
    timestamp: new Date().toISOString(),
    userAgent: 'node-test',
    screenResolution: '1920x1080',
  };

  let state = personalSlice.reducer(initialState, addSceneDecision(decision1));
  assert.equal(state.logs.length, 1);
  assert.deepEqual(state.logs[0].decisions, [decision1]);

  const decision2: UserDecision = {
    ...decision1,
    stepIndex: 1,
    optionText: 'Option B',
    isCorrect: false,
    skillImpacts: { test: 0.5 },
  };

  state = personalSlice.reducer(state, addSceneDecision(decision2));
  assert.equal(state.logs.length, 1);
  assert.deepEqual(state.logs[0].decisions, [decision1, decision2]);
});
