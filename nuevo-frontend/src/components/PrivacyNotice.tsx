import { FC, useState, useEffect } from "react";

interface PrivacyNoticeProps {
  onAccept?: () => void;
  onReject?: () => void;
}

export const PrivacyNotice: FC<PrivacyNoticeProps> = ({
  onAccept,
  onReject,
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [isAccepted, setIsAccepted] = useState(false);
  const [showFullText, setShowFullText] = useState(false);

  useEffect(() => {
    // Verificar si ya se ha mostrado el aviso de privacidad
    const hasPrivacyNotice = localStorage.getItem('privacyNoticeAccepted');
    if (!hasPrivacyNotice) {
      setIsVisible(true);
    }
  }, []);

  const handleAccept = () => {
    if (isAccepted) {
      localStorage.setItem('privacyNoticeAccepted', 'true');
      localStorage.setItem('privacyNoticeDate', new Date().toISOString());
      setIsVisible(false);
      onAccept?.();
    }
  };

  const handleReject = () => {
    localStorage.setItem('privacyNoticeAccepted', 'false');
    setIsVisible(false);
    onReject?.();
  };

  if (!isVisible) {
    return null;
  }

  return (
    <div
      role="dialog"
      aria-labelledby="privacy-notice-title"
      aria-describedby="privacy-notice-description"
      aria-modal="true"
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
    >
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full">
        {/* Header */}
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
              <span className="text-blue-600 dark:text-blue-300 text-xl">🔒</span>
            </div>
            <div>
              <h2
                id="privacy-notice-title"
                className="text-xl font-semibold text-gray-900 dark:text-white"
              >
                Política de Privacidad
              </h2>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Ley Orgánica 3/2018 de Protección de Datos Personales
              </p>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          <div className="space-y-4">
            <p
              id="privacy-notice-description"
              className="text-gray-700 dark:text-gray-300 leading-relaxed"
            >
              En cumplimiento de la Ley Orgánica 3/2018, de 5 de diciembre, de Protección de Datos Personales y garantía de los derechos digitales (LOPD), le informamos de que sus datos personales serán tratados para la evaluación de competencias y generación de informes personalizados de empleabilidad.
            </p>

            {/* Checkbox de consentimiento */}
            <div className="flex items-start gap-3">
              <input
                type="checkbox"
                id="privacy-consent"
                checked={isAccepted}
                onChange={(e) => setIsAccepted(e.target.checked)}
                className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="privacy-consent" className="text-sm text-gray-700 dark:text-gray-300">
                Acepto el tratamiento de mis datos personales según la{" "}
                <button
                  type="button"
                  onClick={() => setShowFullText(!showFullText)}
                  className="text-blue-600 dark:text-blue-400 hover:underline"
                >
                  política de privacidad completa
                </button>
              </label>
            </div>

            {/* Texto completo expandible */}
            {showFullText && (
              <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg text-sm text-gray-600 dark:text-gray-300 max-h-60 overflow-y-auto">
                <h4 className="font-medium text-gray-900 dark:text-white mb-2">
                  📋 Finalidades del tratamiento:
                </h4>
                <ul className="space-y-1 mb-4">
                  <li>• Evaluación de competencias y habilidades profesionales</li>
                  <li>• Generación de informes personalizados de empleabilidad</li>
                  <li>• Mejora de nuestros servicios de evaluación</li>
                  <li>• Comunicación sobre resultados y recomendaciones</li>
                </ul>

                <h4 className="font-medium text-gray-900 dark:text-white mb-2">
                  🏢 Responsable del tratamiento:
                </h4>
                <p className="mb-4">
                  EvaluaTE Team - [Dirección de la empresa]<br />
                  Email: privacy@evaluate.com
                </p>

                <h4 className="font-medium text-gray-900 dark:text-white mb-2">
                  ⚖️ Base legal:
                </h4>
                <p className="mb-4">
                  Consentimiento explícito del usuario para el tratamiento de datos con las finalidades especificadas.
                </p>

                <h4 className="font-medium text-gray-900 dark:text-white mb-2">
                  🛡️ Sus derechos:
                </h4>
                <ul className="space-y-1 mb-4">
                  <li>• Acceso, rectificación y supresión de sus datos</li>
                  <li>• Limitación y oposición al tratamiento</li>
                  <li>• Portabilidad de los datos</li>
                  <li>• Retirada del consentimiento en cualquier momento</li>
                  <li>• Presentación de reclamaciones ante la AEPD</li>
                </ul>

                <h4 className="font-medium text-gray-900 dark:text-white mb-2">
                  📅 Conservación:
                </h4>
                <p className="mb-4">
                  Los datos se conservarán durante el tiempo necesario para cumplir con las finalidades para las que fueron recabados y para determinar las posibles responsabilidades que se pudieran derivar de dicha finalidad y del tratamiento de los datos.
                </p>

                <h4 className="font-medium text-gray-900 dark:text-white mb-2">
                  🔗 Cesiones:
                </h4>
                <p>
                  Sus datos no serán cedidos a terceros salvo obligación legal o cuando sea necesario para la prestación del servicio solicitado.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-700/50 rounded-b-lg">
          <div className="flex flex-col sm:flex-row gap-2 justify-end">
            <button
              onClick={handleReject}
              className="px-6 py-2 text-sm border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              Rechazar
            </button>
            
            <button
              onClick={handleAccept}
              disabled={!isAccepted}
              className="px-6 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Aceptar y continuar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}; 