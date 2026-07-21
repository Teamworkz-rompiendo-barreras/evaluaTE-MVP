import React, { useState, useEffect, useRef } from 'react';

const COOKIE_KEY = 'cookieConsentGiven';

export default function CookieConsent() {
  const [visible, setVisible] = useState(false);
  const buttonRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!localStorage.getItem(COOKIE_KEY)) {
      setVisible(true);
    }
  }, []);

  useEffect(() => {
    if (visible && buttonRef.current) {
      buttonRef.current.focus();
    }
  }, [visible]);

  const handleAccept = () => {
    localStorage.setItem(COOKIE_KEY, 'true');
    setVisible(false);
  };

  // Focus Trap: Impide que el usuario navegue fuera del modal con teclado
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Tab') {
      e.preventDefault(); 
      buttonRef.current?.focus();
    }
  };

  if (!visible) return null;

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
      role="dialog"
      aria-modal="true"
      aria-labelledby="cookie-title"
      onKeyDown={handleKeyDown}
    >
      <div className="bg-white rounded-lg shadow-xl p-8 m-4 max-w-md w-full mx-auto">
        <div className="text-center mb-6">
          <div className="text-4xl mb-4" aria-hidden="true">🍪</div>
          <h2 id="cookie-title" className="text-2xl font-bold text-gray-800 mb-2">
            Uso de Cookies y Privacidad
          </h2>
        </div>

        <div className="text-gray-700 mb-6 text-sm leading-relaxed">
          <p className="mb-4">Para garantizar la funcionalidad básica necesitamos cookies técnicas para:</p>
          <ul className="list-disc list-inside space-y-2 mb-4 text-sm">
            <li>Mantener tu sesión segura</li>
            <li>Guardar tus ajustes de accesibilidad</li>
          </ul>
        </div>

        <div className="text-center">
          <button
            ref={buttonRef}
            onClick={handleAccept}
            className="bg-[#374BA6] text-white px-8 py-3 rounded-lg font-semibold hover:bg-[#2d3f96] focus:outline-none focus:ring-4 focus:ring-[#8095F2] transition-colors"
          >
            Aceptar y Continuar
          </button>
        </div>
      </div>
    </div>
  );
}