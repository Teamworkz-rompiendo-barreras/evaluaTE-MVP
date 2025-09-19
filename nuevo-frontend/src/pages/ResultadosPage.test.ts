import test from 'node:test';
import assert from 'node:assert/strict';
import { resolveJobPreferences } from '../utils/jobPreferences.ts';

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
