import test from 'node:test';
import assert from 'node:assert/strict';
import { resolveJobPreferences } from '../utils/jobPreferences.ts';
import { processRadarData } from './processRadarData.ts';

const basePersonal = {
  workMode: undefined,
  availability: undefined,
  willingToRelocate: undefined,
  hasDisabilityCert: undefined,
};

test('resolveJobPreferences normalizes string input', () => {
  const jp = resolveJobPreferences({ ...basePersonal, jobPreferences: 'Tecnología' });
  assert.deepEqual(jp, {
    areas: ['Tecnología'],
    needs: [],
    workMode: 'remoto',
    availability: 'completa',
    willingToRelocate: false,
    hasDisabilityCert: false,
  });
});

test('resolveJobPreferences merges object input with defaults', () => {
  const jp = resolveJobPreferences({
    ...basePersonal,
    jobPreferences: { areas: ['Salud'] },
    workMode: 'híbrido',
    hasDisabilityCert: true,
  });
  assert.deepEqual(jp, {
    areas: ['Salud'],
    needs: [],
    workMode: 'híbrido',
    availability: 'completa',
    willingToRelocate: false,
    hasDisabilityCert: true,
  });
});

test('processRadarData keeps unknown skills alongside canonical ones', () => {
  const radar = processRadarData([
    { skill: 'Creatividad', score: 70 },
    { skill: 'Innovación', score: 80 },
    { softskill: 'adaptabilidad', score: 60 },
  ]);

  const creativity = radar.find(item => item.softskill === 'Creatividad');
  assert.equal(creativity?.score, 70);

  const resilience = radar.find(item => item.softskill === 'Resiliencia y flexibilidad');
  assert.equal(resilience?.score, 60);

  const innovation = radar.find(item => item.softskill === 'Innovación');
  assert.ok(innovation, 'La habilidad desconocida debe conservarse en el resultado');
  assert.equal(innovation?.score, 80);

  assert.ok(radar.length > 10, 'El radar debe incluir habilidades adicionales además de las canónicas');
});
