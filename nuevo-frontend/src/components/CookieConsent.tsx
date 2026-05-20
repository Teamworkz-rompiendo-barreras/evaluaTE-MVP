import { useState, useEffect } from 'react';

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
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white rounded-lg shadow-xl p-8 m-4 max-w-md w-full mx-auto">
        {/* Icono de cookies */}
        <div className="text-center mb-6">
          <div className="text-4xl mb-4">🍪</div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">
            Uso de Cookies
          </h2>
        </div>

        {/* Contenido */}
        <div className="text-gray-700 mb-6 text-sm leading-relaxed">
          <p className="mb-4">
            Utilizamos cookies propias y de terceros para:
          </p>
          <ul className="list-disc list-inside space-y-2 mb-4 text-sm">
            <li>Mejorar tu experiencia de navegación</li>
            <li>Analizar el uso del sitio web</li>
            <li>Personalizar el contenido y publicidad</li>
            <li>Proporcionar funcionalidades de redes sociales</li>
          </ul>
          <p className="text-xs text-gray-600">
            Al hacer clic en &quot;Aceptar&quot;, consientes el uso de todas las cookies. 
            Puedes consultar nuestra política de cookies para más información.
          </p>
        </div>

        {/* Botón de aceptar */}
        <div className="text-center">
          <button
            onClick={handleAccept}
            className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold shadow-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2 transition-colors duration-200"
            aria-label="Aceptar el uso de cookies"
          >
            Aceptar Cookies
          </button>
        </div>
      </div>
    </div>
  );
} 