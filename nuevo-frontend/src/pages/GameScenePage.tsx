// src/pages/GameScenePage.tsx
import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useAppDispatch } from '../app/hooks';
import { games } from '../data/games';
// IMPORTACIÓN CORREGIDA: Utilizamos la acción exacta declarada en gameSlice.ts
import { updateGameProgress } from '../features/games/gameSlice';
import { useGameController } from '../features/games/useGameController';

const GameScenePage: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const { gameId } = useParams<{ gameId: string }>(); 
  
  const { currentGame, currentScene, completeScene, gameProgress, accessibility } = useGameController();
  
  const [isInitializing, setIsInitializing] = useState(true);
  const [selectedOptionId, setSelectedOptionId] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    
    const initGame = async () => {
      if (!gameId) {
        if (isMounted) setIsInitializing(false);
        return;
      }

      setIsInitializing(true);
      
      try {
        const targetGame = games.find(g => String(g.id) === String(gameId));
        
        if (targetGame) {
          // PAYLOAD CORREGIDO: Enviamos exactamente la estructura que espera tu reducer
          dispatch(updateGameProgress({ currentGameId: String(targetGame.id) }));
        } else {
          console.error(`Juego con ID ${gameId} no encontrado en la base de datos.`);
        }
      } finally {
        setTimeout(() => {
          if (isMounted) setIsInitializing(false);
        }, 250);
      }
    };

    initGame();
    
    return () => { isMounted = false; };
  }, [gameId, dispatch]);

  useEffect(() => {
    setSelectedOptionId(null);
  }, [currentScene]);

  // ESTADO DE CARGA ACCESIBLE
  if (isInitializing) {
    return (
      <div 
        className="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-gray-900" 
        aria-live="polite" 
        aria-busy="true"
      >
        <div className="animate-spin rounded-full h-12 w-12 border-t-4 border-b-4 border-[#374BA6] dark:border-[#8095F2]"></div>
        <span className="sr-only">Cargando escenario del minijuego...</span>
      </div>
    );
  }

  // ESTADO DE ERROR ACCESIBLE
  if (!currentGame || !currentScene) {
    return (
      <div 
        className="min-h-screen flex flex-col items-center justify-center p-6 bg-gray-50 dark:bg-gray-900 text-center"
        role="alert"
        aria-live="assertive"
      >
        <h1 className="text-2xl font-bold mb-4 text-gray-800 dark:text-white">
          El minijuego no está disponible
        </h1>
        <p className="mb-8 text-gray-600 dark:text-gray-300">
          No hemos podido cargar la información de esta prueba. Vuelve al panel e inténtalo de nuevo.
        </p>
        <button 
          onClick={() => navigate('/games')} 
          className="bg-[#374BA6] text-white px-6 py-3 rounded-lg font-semibold shadow hover:bg-[#2d3f96] focus:outline-none focus:ring-4 focus:ring-[#8095F2] transition-colors"
        >
          Volver al Dashboard
        </button>
      </div>
    );
  }

  const handleOptionClick = (optionId: string) => {
    if (selectedOptionId !== null) return;
    
    setSelectedOptionId(optionId);

    if (optionId === 'volver-menu') {
      navigate('/games');
      return;
    }

    setTimeout(() => {
      completeScene(optionId);
      if (currentScene.id === 'game-complete') {
        navigate('/games');
      }
    }, 600);
  };

  const renderOptionContent = (rawText: string) => {
    const emojiRegex = /([\u2700-\u27BF]|[\uE000-\uF8FF]|\uD83C[\uDC00-\uDFFF]|\uD83D[\uDC00-\uDFFF]|[\u2011-\u26FF]|\uD83E[\uDD10-\uDDFF])/g;
    const textWithoutEmoji = rawText.replace(emojiRegex, '').trim();
    const emojis = rawText.match(emojiRegex)?.join('') || '';

    return (
      <div className="flex items-center justify-between w-full">
        <span className="font-medium text-left">{textWithoutEmoji}</span>
        {emojis && (
          <span className="text-2xl ml-4" aria-hidden="true">{emojis}</span>
        )}
      </div>
    );
  };

  const isHighContrast = ['alto', 'muy-alto'].includes(accessibility?.contrastLevel as string);

  return (
    <div 
      className={`min-h-screen pb-12 pt-6 px-4 sm:px-6 lg:px-8 transition-colors duration-300 ${
        isHighContrast ? 'bg-black text-white' : 'bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100'
      }`}
      style={{ fontSize: `${accessibility?.fontScale || 100}%` }}
    >
      <div className="max-w-3xl mx-auto">
        {/* Barra de progreso */}
        <div className="mb-8" aria-label={`Progreso del juego: escena ${gameProgress.current} de ${gameProgress.total}`}>
          <div className="flex justify-between text-sm font-medium mb-2">
            <span className={isHighContrast ? 'text-white' : 'text-gray-600 dark:text-gray-400'}>{currentGame.title}</span>
            <span className={isHighContrast ? 'text-white' : 'text-[#374BA6] dark:text-[#8095F2]'}>{gameProgress.current} / {gameProgress.total}</span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5 overflow-hidden" aria-hidden="true">
            <div 
              className={`${isHighContrast ? 'bg-white' : 'bg-[#374BA6] dark:bg-[#8095F2]'} h-2.5 rounded-full transition-all duration-500 ease-out`}
              style={{ width: `${gameProgress.percentage}%` }}
            ></div>
          </div>
        </div>

        {/* Contenido de la escena */}
        <div className={`rounded-xl shadow-lg p-6 md:p-8 mb-8 border ${isHighContrast ? 'bg-black border-white' : 'bg-white border-gray-100 dark:bg-gray-800 dark:border-gray-700'}`}>
          <h2 className={`text-2xl md:text-3xl font-bold mb-4 ${isHighContrast ? 'text-white' : 'text-[#374BA6] dark:text-[#8095F2]'}`}>
            {currentScene.title}
          </h2>
          <p className={`text-lg mb-8 leading-relaxed ${isHighContrast ? 'text-white' : 'text-gray-700 dark:text-gray-300'}`}>
            {currentScene.description}
          </p>

          <div className="space-y-4" role="group" aria-label="Opciones de respuesta">
            {(currentScene.options || []).map((option: any) => {
              const isSelected = selectedOptionId === option.id;
              const isLocked = selectedOptionId !== null && !isSelected;

              return (
                <button
                  key={option.id}
                  type="button"
                  disabled={selectedOptionId !== null}
                  onClick={() => handleOptionClick(option.id)}
                  className={`w-full p-5 rounded-xl border-2 text-lg transition-all duration-200 focus:outline-none focus:ring-4 focus:ring-[#8095F2] flex items-center ${
                    isSelected
                      ? 'border-[#374BA6] bg-blue-50 text-[#374BA6] dark:bg-blue-900/30 dark:border-[#8095F2] dark:text-[#8095F2] shadow-md transform scale-[1.01]'
                      : isLocked
                      ? 'border-gray-200 bg-gray-50 text-gray-400 opacity-60 cursor-not-allowed dark:border-gray-700 dark:bg-gray-800 dark:text-gray-500'
                      : 'border-gray-300 bg-white hover:border-[#374BA6] hover:bg-gray-50 dark:bg-gray-800 dark:border-gray-600 dark:hover:border-[#8095F2] cursor-pointer shadow-sm hover:shadow'
                  } ${
                    isHighContrast ? '!border-white !bg-black !text-white hover:!bg-gray-900' : ''
                  }`}
                  aria-pressed={isSelected}
                >
                  {renderOptionContent(option.text)}
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default GameScenePage;