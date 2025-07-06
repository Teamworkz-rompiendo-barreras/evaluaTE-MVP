/// <reference types="cypress" />
import 'cypress-file-upload'

/* eslint-disable */
declare global {
  namespace Cypress {
    interface Chainable<Subject> {
      /**
       * Custom command to clear storage and handle modals
       * @example cy.clearStorageAndHandleModals()
       */
      clearStorageAndHandleModals(): Chainable<void>

      /**
       * Custom command to simulate user login and fill personal data.
       * @example cy.login()
       */
      login(): Chainable<void>

      /**
       * Custom command to complete preferences step
       * @example cy.completePreferences()
       */
      completePreferences(): Chainable<void>

      /**
       * Custom command to attach file with metadata (name, type, encoding).
       * @see https://github.com/abramenal/cypress-file-upload 
       * @example cy.attachFile('cv.pdf')
       */
      attachFile(
        fileName: string,
        options?: {
          subjectType?: 'input' | 'drag-n-drop'
          mimeType?: string
          encoding?: string
          force?: boolean
          allowEmpty?: boolean
        }
      ): Chainable<JQuery<HTMLElement>>

      /**
       * Navega al dashboard de minijuegos tras login
       * @example cy.startGame()
       */
      startGame(): Chainable<void>

      /**
       * Completa una escena gamificada
       * @param sceneId - ID de la escena a completar
       * @example cy.completeScene(1)
       */
      completeScene(sceneId: number): Chainable<void>

      /**
       * Valida que el informe final esté completo
       * @example cy.validateFinalReport()
       */
      validateFinalReport(): Chainable<void>
    }
  }
}

export {}