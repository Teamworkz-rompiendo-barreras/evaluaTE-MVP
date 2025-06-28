// src/setupTests.ts
import '@testing-library/jest-dom/extend-expect'
import { server } from '@/mocks/server.ts'

beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())