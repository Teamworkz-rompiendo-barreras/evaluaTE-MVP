import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Flujo E2E Teamworkz: Evaluador IA + Accesibilidad', () => {

  test('El candidato anónimo navega y sube el CV sin barreras WCAG 2.2 AA', async ({ page }) => {
    // 1. Carga inicial
    await page.goto('http://localhost:3005');

    // 2. Gestión de cookies y Datos Personales
    await page.getByRole('button', { name: 'Aceptar y continuar' }).click();
    await expect(page.getByRole('dialog')).not.toBeVisible();

    await page.getByLabel('Nombre').fill('Candidato');
    await page.getByLabel('Apellidos').fill('Prueba');
    await page.getByLabel('Email (opcional)').fill('candidato@teamworkz.com');
    await page.getByLabel(/política de privacidad/i).check();
    await page.getByRole('button', { name: 'Siguiente' }).click();

    // 3. Preferencias Laborales
    await expect(page.getByRole('heading', { name: 'Paso 2 de 2' })).toBeVisible();
    await page.getByLabel(/Qué tipo de trabajo/i).fill('Desarrollo Web');
    await page.getByLabel(/modalidad/i).selectOption('remoto');
    await page.getByLabel(/disponibilidad horaria/i).selectOption('completa');
    await page.getByLabel(/Cuándo puedes incorporarte/i).selectOption('inmediata');
    await page.getByLabel(/certificado de discapacidad/i).check();
    await page.getByRole('button', { name: 'Continuar a los minijuegos' }).click();

    // 4. Panel de Minijuegos (Modo QA activo)
    await page.waitForURL('**/games', { timeout: 10000 });
    await page.getByRole('button', { name: 'QA: Completar Juegos' }).click();
    await page.getByRole('button', { name: /Ir a adjuntar currículum/i }).click();

    // 5. Subir el CV y llamar a la Inteligencia Artificial
    await expect(page.getByRole('heading', { name: /Sube tu CV/i })).toBeVisible();
    await page.locator('input[type="file"]').setInputFiles('tests/prueba.pdf');
    await page.getByRole('button', { name: 'Subir y continuar' }).click();

    // 6. Validación de Destino y Renderizado de Resultados
    // Ajustado para absorber la latencia de la IA sin falsos negativos
    await page.waitForURL('**/resultados', { timeout: 30000 });
    
    // CORRECCIÓN: Uso de getByText como fallback semántico
    await expect(page.getByText(/Informe de Empleabilidad/i).first()).toBeVisible();

    // 7. Auditoría final de Accesibilidad (Motor Axe-Core)
    const analisisInforme = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag22aa'])
      .analyze();
      
    expect(analisisInforme.violations).toEqual([]);
  });
});