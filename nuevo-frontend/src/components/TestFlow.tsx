import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { RootState } from '../app/store';
import { saveContact, savePreferences, setPersonalCompleted } from '../features/personal/personalSlice';

const TestFlow: React.FC = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const personal = useSelector((state: RootState) => state.personal);

  const testCompleteFlow = () => {
    // Paso 1: Simular datos de contacto
    // console.log('1. Guardando datos de contacto...');
    dispatch(saveContact({
      firstName: 'Test',
      lastName: 'User',
      email: 'test@test.com',
      whatsapp: '123456789'
    }));
    
    // console.log('Estado después de saveContact:', personal);
    
    // Paso 2: Simular preferencias
    // console.log('2. Guardando preferencias...');
    const jobPrefObj = {
      areas: ['Desarrollo web'],
      needs: [],
      workMode: 'remoto' as const,
      availability: 'completa' as const,
      willingToRelocate: false,
      hasDisabilityCert: false,
    };
    
    dispatch(savePreferences({
      jobPreferences: jobPrefObj,
      workMode: 'remoto',
      availability: 'completa',
      startDate: 'inmediata',
      willingToRelocate: false,
      hasDisabilityCert: false,
    }));
    
    dispatch(setPersonalCompleted(true));
    
    // console.log('Estado después de savePreferences:', personal);
    
    // Paso 3: Navegar al dashboard
    // console.log('3. Navegando a /games...');
    navigate('/games');
  };

  const testNavigation = () => {
    // console.log('=== TEST DE NAVEGACIÓN ===');
    // console.log('Navegando a /game/decision-making...');
    navigate('/game/decision-making');
  };

  const clearState = () => {
    // console.log('=== LIMPIANDO ESTADO ===');
    // Aquí podrías dispatch una acción para resetear el estado
    window.location.reload();
  };

  return (
    <div className="fixed top-4 right-4 bg-yellow-500 text-black p-4 rounded-lg text-xs max-w-md z-50">
      <h3 className="font-bold mb-2">🧪 TEST FLOW</h3>
      
      <div className="space-y-2">
        <button
          onClick={testCompleteFlow}
          className="w-full bg-green-600 text-white p-2 rounded text-xs"
        >
          Test Flujo Completo
        </button>
        
        <button
          onClick={testNavigation}
          className="w-full bg-blue-600 text-white p-2 rounded text-xs"
        >
          Test Navegación
        </button>
        
        <button
          onClick={clearState}
          className="w-full bg-red-600 text-white p-2 rounded text-xs"
        >
          Limpiar Estado
        </button>
      </div>
      
      <div className="mt-2 text-xs">
        <div>firstName: "{personal.firstName}"</div>
        <div>lastName: "{personal.lastName}"</div>
        <div>completed: {personal.completed ? 'true' : 'false'}</div>
        <div>jobPreferences: {JSON.stringify(personal.jobPreferences)}</div>
      </div>
    </div>
  );
};

export default TestFlow; 