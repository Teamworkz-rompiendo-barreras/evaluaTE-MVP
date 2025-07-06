import React from 'react';

const TestPage: React.FC = () => {
  console.log('TestPage - Renderizando');

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-6xl">
        <h1 className="text-4xl font-bold text-gray-800 mb-4">
          🎮 EvalúaTE - Minijuegos (TEST)
        </h1>
        <p className="text-lg text-gray-600 mb-6">
          Página de prueba para verificar que funciona
        </p>
        
        <div className="bg-white rounded-lg p-6 shadow-sm">
          <h2 className="text-xl font-semibold mb-4">Información de Prueba</h2>
          <p>Esta es una página de prueba para verificar que el routing funciona.</p>
          <p>Si puedes ver esto, significa que el componente se está renderizando correctamente.</p>
        </div>
      </div>
    </div>
  )
}

export default TestPage 