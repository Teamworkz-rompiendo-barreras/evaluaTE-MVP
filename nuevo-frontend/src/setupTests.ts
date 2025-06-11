/// <reference types="vitest" />
/// <reference types="@testing-library/jest-dom" />

import '@testing-library/jest-dom';               // 1) Carga los matchers
import matchers from '@testing-library/jest-dom/matchers';
import { expect } from 'vitest';

// 2) Registra los matchers de jest-dom en Vitest
expect.extend(matchers);
