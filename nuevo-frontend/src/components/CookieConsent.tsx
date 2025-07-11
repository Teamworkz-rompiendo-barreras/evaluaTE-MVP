import React, { useState, useEffect } from 'react';

const COOKIE_KEY = 'cookieConsentGiven';

export default function CookieConsent() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const consent = localStorage.getItem(COOKIE_KEY);
    if (!consent) {
      setVisible(true);
    }
  }, []);

  const handleAccept = () => {
    localStorage.setItem(COOKIE_KEY, 'true');
    setVisible(false);
  };

  if (!visible) return null;

  return (
    <div className="fixed bottom-0 left-0 w-full z-50 flex justify-center items-end pointer-events-none">
      <div className="bg-white border border-gray-300 shadow-lg rounded-t-lg p-4 m-2 max-w-xl w-full flex flex-col md:flex-row md:items-center gap-4 pointer-events-auto animate-fadeIn">
        <div className="flex-1 text-gray-800 text-sm">
          Utilizamos cookies propias y de terceros para mejorar tu experiencia, analizar el uso del sitio y personalizar el contenido. Puedes aceptar para continuar navegando. Consulta nuestra política para más información.
        </div>
        <button
          onClick={handleAccept}
          className="bg-blue-600 text-white px-5 py-2 rounded font-semibold shadow hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-400"
          aria-label="Aceptar el uso de cookies"
        >
          Aceptar
        </button>
      </div>
    </div>
  );
} 