// src/types/vitest-globals.d.ts
export const test: (name: string, fn: () => void | Promise<void>) => void;
export const describe: (name: string, fn: () => void) => void;
export const expect: (actual: unknown) => {
  toBe: (expected: unknown) => void;
  toEqual: (expected: unknown) => void;
  toBeTruthy: () => void;
  toBeFalsy: () => void;
};