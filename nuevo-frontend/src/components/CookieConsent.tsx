import { FC, useState, useEffect } from "react";

interface CookieConsentProps {
  onAccept?: () => void;
  onReject?: () => void;
  onSettings?: () => void;
}

export const CookieConsent: FC<CookieConsentProps> = ({
  onAccept,
  onReject,
  onSettings,
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  useEffect(() => {
    // Verificar si ya se ha mostrado el consentimiento
    const hasConsent = localStorage.getItem('cookieConsent');
    if (!hasConsent) {
      setIsVisible(true);
    }
  }, []);

  const handleAccept = () => {
    localStorage.setItem('cookieConsent', 'accepted');
    setIsVisible(false);
    onAccept?.();
  };

  const handleReject = () => {
    localStorage.setItem('cookieConsent', 'rejected');
    setIsVisible(false);
    onReject?.();
  };

  const handleSettings = () => {
    setIsExpanded(!isExpanded);
    onSettings?.();
  };

  if (!isVisible) {
    return null;
  }

  return (
    <div
      role="dialog"
      aria-labelledby="cookie-consent-title"
      aria-describedby="cookie-consent-description"
      className="fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 shadow-lg z-50 p-4"
    >
      <div className="max-w-4xl mx-auto">
        <div className="flex flex-col lg:flex-row items-start lg:items-center gap-4">
          {/* Contenido principal */}
          <div className="flex-1">
            <h2
              id="cookie-consent-title"
              className="text-lg font-semibold text-gray-900 dark:text-white mb-2"
            >
              🍪 Política de Cookies
            </h2>
            <p
              id="cookie-consent-description"
              className="text-sm text-gray-600 dark:text-gray-300 mb-3"
            >
              Utilizamos cookies para mejorar tu experiencia en nuestra plataforma. 
              Algunas cookies son necesarias para el funcionamiento básico del sitio.
            </p>
            
            {/* Información expandible */}
            {isExpanded && (
              <div className="mt-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <h3 className="font-medium text-gray-900 dark:text-white mb-2">
                  Tipos de cookies que utilizamos:
                </h3>
                <ul className="text-sm text-gray-600 dark:text-gray-300 space-y-1">
                  <li>• <strong>Cookies esenciales:</strong> Necesarias para el funcionamiento básico</li>
                  <li>• <strong>Cookies de rendimiento:</strong> Nos ayudan a mejorar la experiencia</li>
                  <li>• <strong>Cookies de funcionalidad:</strong> Recuerdan tus preferencias</li>
                  <li>• <strong>Cookies de análisis:</strong> Nos permiten entender cómo usas el sitio</li>
                </ul>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                  Puedes cambiar tus preferencias en cualquier momento desde la configuración.
                </p>
              </div>
            )}
          </div>

          {/* Botones de acción */}
          <div className="flex flex-col sm:flex-row gap-2 w-full lg:w-auto">
            <button
              onClick={handleSettings}
              className="px-4 py-2 text-sm text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-white transition-colors"
              aria-expanded={isExpanded}
            >
              {isExpanded ? "Ocultar detalles" : "Ver detalles"}
            </button>
            
            <button
              onClick={handleReject}
              className="px-4 py-2 text-sm border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              Rechazar
            </button>
            
            <button
              onClick={handleAccept}
              className="px-4 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              Aceptar todas
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}; 