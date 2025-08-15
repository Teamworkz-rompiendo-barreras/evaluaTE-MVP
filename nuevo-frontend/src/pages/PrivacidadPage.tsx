import React from 'react';
import { Link } from 'react-router-dom';

const PrivacidadPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-4xl mx-auto p-6">
        {/* Header */}
        <div className="mb-8">
          <Link 
            to="/register/contact" 
            className="inline-flex items-center text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 mb-4"
          >
            ← Volver a Datos Personales
          </Link>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">
            Política de Privacidad
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            Última actualización: {new Date().toLocaleDateString('es-ES')}
          </p>
        </div>

        {/* Contenido */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-8 space-y-6">
          
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
              1. Información del Responsable
            </h2>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              <strong>Teamworkz - Rompiendo Barreras</strong><br />
              Aplicación web de evaluación de habilidades blandas y empleabilidad<br />
              Contacto: hola@teamworkz.co
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
              2. Datos Personales que Recopilamos
            </h2>
            <div className="space-y-3">
              <p className="text-gray-700 dark:text-gray-300">
                Recopilamos únicamente los datos personales que nos proporcionas voluntariamente:
              </p>
              <ul className="list-disc list-inside text-gray-700 dark:text-gray-300 space-y-2 ml-4">
                <li><strong>Nombre y apellidos:</strong> Para personalizar tu experiencia y generar informes</li>
                <li><strong>Email (opcional):</strong> Para contactar si es necesario</li>
                <li><strong>WhatsApp (opcional):</strong> Para contacto directo si es necesario</li>
                <li><strong>Respuestas a los minijuegos:</strong> Para evaluar tus habilidades blandas</li>
                <li><strong>Resultados de evaluación:</strong> Para generar tu informe personalizado</li>
              </ul>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
              3. Finalidad del Tratamiento
            </h2>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              Utilizamos tus datos personales exclusivamente para:
            </p>
            <ul className="list-disc list-inside text-gray-700 dark:text-gray-300 space-y-2 ml-4">
              <li>Proporcionarte una evaluación personalizada de tus habilidades blandas</li>
              <li>Generar informes de empleabilidad adaptados a tu perfil</li>
              <li>Mejorar la funcionalidad y experiencia de usuario de la aplicación</li>
              <li>Responder a consultas o solicitudes que puedas realizar</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
              4. Base Legal
            </h2>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              El tratamiento de tus datos se basa en:
            </p>
            <ul className="list-disc list-inside text-gray-700 dark:text-gray-300 space-y-2 ml-4">
              <li><strong>Consentimiento explícito:</strong> Que nos otorgas al marcar la casilla correspondiente</li>
              <li><strong>Interés legítimo:</strong> Para mejorar nuestros servicios y la experiencia del usuario</li>
              <li><strong>Cumplimiento de obligaciones legales:</strong> Cuando sea necesario por ley</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
              5. Conservación de Datos
            </h2>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              Tus datos personales se conservarán únicamente durante el tiempo necesario para cumplir con las finalidades descritas, 
              o hasta que revoques tu consentimiento. En ningún caso se conservarán por más de 2 años desde la última interacción.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
              6. Compartición de Datos
            </h2>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              <strong>No vendemos, alquilamos ni compartimos tus datos personales con terceros</strong>, excepto en los siguientes casos:
            </p>
            <ul className="list-disc list-inside text-gray-700 dark:text-gray-300 space-y-2 ml-4">
              <li>Cuando sea necesario para proporcionar el servicio solicitado</li>
              <li>Cuando lo requiera la ley o una autoridad competente</li>
              <li>Con proveedores de servicios que nos ayudan a operar la aplicación (solo con garantías de seguridad)</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
              7. Seguridad de Datos
            </h2>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              Implementamos medidas técnicas y organizativas apropiadas para proteger tus datos personales contra:
            </p>
            <ul className="list-disc list-inside text-gray-700 dark:text-gray-300 space-y-2 ml-4">
              <li>Acceso no autorizado o alteración</li>
              <li>Divulgación accidental o ilícita</li>
              <li>Destrucción o pérdida accidental</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
              8. Tus Derechos
            </h2>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              Tienes derecho a:
            </p>
            <ul className="list-disc list-inside text-gray-700 dark:text-gray-300 space-y-2 ml-4">
              <li><strong>Acceso:</strong> Conocer qué datos tenemos sobre ti</li>
              <li><strong>Rectificación:</strong> Corregir datos inexactos o incompletos</li>
              <li><strong>Supresión:</strong> Solicitar la eliminación de tus datos</li>
              <li><strong>Portabilidad:</strong> Recibir tus datos en formato estructurado</li>
              <li><strong>Limitación:</strong> Restringir el tratamiento de tus datos</li>
              <li><strong>Oposición:</strong> Oponerte al tratamiento de tus datos</li>
              <li><strong>Revocación:</strong> Retirar tu consentimiento en cualquier momento</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
              9. Ejercicio de Derechos
            </h2>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              Para ejercer cualquiera de estos derechos, puedes contactarnos a través de:
            </p>
            <ul className="list-disc list-inside text-gray-700 dark:text-gray-300 space-y-2 ml-4">
                          <li><strong>Email:</strong> hola@teamworkz.co</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
              10. Cookies y Tecnologías Similares
            </h2>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              Utilizamos cookies técnicas necesarias para el funcionamiento de la aplicación. 
              No utilizamos cookies de seguimiento ni publicitarias. Puedes configurar tu navegador 
              para rechazar cookies, aunque esto puede afectar la funcionalidad de la aplicación.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
              11. Menores de Edad
            </h2>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              Nuestros servicios no están dirigidos a menores de 16 años. Si eres menor de edad, 
              necesitarás el consentimiento de tus padres o tutores legales para utilizar la aplicación.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
              12. Cambios en la Política
            </h2>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              Nos reservamos el derecho de modificar esta política de privacidad. 
              Cualquier cambio será notificado a través de la aplicación o por email. 
              El uso continuado de la aplicación tras los cambios constituye aceptación de la nueva política.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
              13. Contacto
            </h2>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              Si tienes alguna pregunta sobre esta política de privacidad o el tratamiento de tus datos, 
              no dudes en contactarnos:
            </p>
            <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg mt-4">
              <p className="text-gray-700 dark:text-gray-300">
                <strong>Teamworkz - Rompiendo Barreras</strong><br />
                Email: hola@teamworkz.co
              </p>
            </div>
          </section>

          <div className="border-t pt-6 mt-8">
            <p className="text-sm text-gray-500 dark:text-gray-400 text-center">
              Esta política de privacidad cumple con el Reglamento General de Protección de Datos (RGPD) 
              y la Ley Orgánica de Protección de Datos Personales y garantía de derechos digitales (LOPDGDD).
            </p>
          </div>
        </div>

        {/* Botón de volver */}
        <div className="mt-8 text-center">
          <Link 
            to="/datos-personales" 
            className="btn-primary px-8 py-3 text-lg font-semibold"
          >
            Volver a Datos Personales
          </Link>
        </div>
      </div>
    </div>
  );
};

export default PrivacidadPage;
