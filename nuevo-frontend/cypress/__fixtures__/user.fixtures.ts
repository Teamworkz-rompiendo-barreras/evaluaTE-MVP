// nuevo-frontend/cypress/__fixtures__/user.fixtures.ts

export const userFixture = {
  firstName: 'Juan',
  lastName: 'Pérez',
  email: 'juan.perez@example.com',
  whatsapp: '600123456',
  jobPreferences: {
    areas: ['Desarrollo web'],
    needs: ['Horario flexible', 'Acceso remoto'],
    workMode: 'remoto',
    availability: 'mañana',
    willingToRelocate: false,
    hasDisabilityCert: true,
  },
  easyReadingMode: true,
  audioAssistiveMode: false,
  showPictograms: true,
  contrastLevel: "alto",
  fontScale: 120, // Agregado
};