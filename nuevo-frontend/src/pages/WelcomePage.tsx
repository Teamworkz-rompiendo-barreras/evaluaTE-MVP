import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import type { RootState } from '@/app/store';

const WelcomePage: React.FC = () => {
  const navigate = useNavigate();
  const personal = useSelector((state: RootState) => state.personal);
  const game = useSelector((state: RootState) => state.game);

  // El useEffect ha sido eliminado porque no realiza ninguna acción

  const handleStart = () => {
    localStorage.setItem('welcomeSeen', 'true');
    navigate('/games');
  };

  return (
    <div style={{ maxWidth: 600, margin: '0 auto', padding: 32, textAlign: 'center' }}>
      <h1>¡Bienvenido/a a tu primera semana en “IntegraPro”!</h1>
      <p style={{ marginTop: 24, marginBottom: 24 }}>
        Una empresa que apuesta por el talento y la diversidad. Durante estos días, vivirás distintas situaciones laborales reales que pondrán a prueba tus habilidades. No hay respuestas incorrectas: solo formas diferentes de enfrentarse al día a día. Reflexiona, responde con sinceridad y avanza a tu ritmo.<br /><br />
        ¡Empezamos!
      </p>
      <button onClick={handleStart} style={{ padding: '12px 32px', fontSize: 18, borderRadius: 8, background: '#374BA6', color: '#fff', border: 'none', cursor: 'pointer' }}>
        Comenzar
      </button>
      {/* Bloque de depuración solo visible en desarrollo */}
      {process.env.NODE_ENV !== 'production' && (
        <div style={{ marginTop: 32, textAlign: 'left', background: '#f5f5f5', padding: 16, borderRadius: 8, fontSize: 14 }}>
          <strong>Depuración (solo desarrollo):</strong>
          <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
            {JSON.stringify({ personal, game }, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};

export default WelcomePage; 