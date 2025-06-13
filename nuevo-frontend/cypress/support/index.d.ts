/// <reference types="cypress" />
import 'cypress-file-upload';

declare global {
  namespace Cypress {
    interface Chainable {
      /**
       * Custom command to attach a file to an `<input type="file">` element.
       * @see https://github.com/abramenal/cypress-file-upload
       */
      attachFile(fileName: string, options?: Partial<{}>): Chainable<JQuery<HTMLElement>>;
    }
  }
}
export {};
