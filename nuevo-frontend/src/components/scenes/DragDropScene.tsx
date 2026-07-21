import React, { useState, useEffect } from 'react';
import { GameScene, DragDropItem, DragDropZone } from '../../types/game';

interface DragDropSceneProps {
  scene: GameScene;
  onComplete: (selectedOptionId?: string) => void;
  onHelpRequest: () => void;
  onAdaptation: (adaptation: string) => void;
  accessibility: {
    contrastLevel: 'normal' | 'high';
    fontScale: number;
    audioEnabled: boolean;
    visualHelp: boolean;
    timeExtensions: boolean;
  };
}

const DragDropScene: React.FC<DragDropSceneProps> = ({
  scene,
  onComplete,
  accessibility
}) => {
  // Estados para la lógica "Select-and-Place" (Accesible)
  const [selectedItem, setSelectedItem] = useState<DragDropItem | null>(null);
  const [itemPositions, setItemPositions] = useState<Record<string, string>>({});
  const [placedItems, setPlacedItems] = useState<DragDropItem[]>([]);
  const [isCompleted, setIsCompleted] = useState(false);
  const [isCorrect, setIsCorrect] = useState<boolean | null>(null);
  
  // Estado para tecnologías de asistencia
  const [announcement, setAnnouncement] = useState<string>('');

  const dragDropConfig = scene.dragDropConfig;

  // Limpieza segura del anuncio (Fija el error TS7030)
  useEffect(() => {
    if (!announcement) return; 
    
    const timer = setTimeout(() => setAnnouncement(''), 3000);
    return () => clearTimeout(timer);
  }, [announcement]);

  if (!dragDropConfig) return <div role="alert">Error: Configuración de escena no encontrada.</div>;

  const handleSelectOrigin = (item: DragDropItem) => {
    if (isCompleted) return;
    setSelectedItem(item);
    setAnnouncement(`Elemento seleccionado: ${item.text || 'Sin texto'}. Usa el tabulador para elegir la zona de destino.`);
  };

  const handlePlaceToZone = (zone: DragDropZone) => {
    if (isCompleted || !selectedItem) return;

    const newPlacedItems = [...placedItems, selectedItem];
    setPlacedItems(newPlacedItems);

    const newPositions = { ...itemPositions, [selectedItem.id]: zone.id };
    setItemPositions(newPositions);
    
    setAnnouncement(`Elemento ${selectedItem.text || 'Sin texto'} colocado correctamente en la zona ${zone.title}.`);
    setSelectedItem(null); 

    const allItemsPlaced = dragDropConfig.items.length === newPlacedItems.length;

    if (allItemsPlaced) {
      setIsCompleted(true);
      
      let isOrderCorrect = true;
      if (dragDropConfig.correctOrder) {
        const placedOrderIds = newPlacedItems.map(item => item.id);
        isOrderCorrect = JSON.stringify(placedOrderIds) === JSON.stringify(dragDropConfig.correctOrder);
      }
      
      setIsCorrect(isOrderCorrect);
      setAnnouncement(isOrderCorrect ? '¡Orden correcto! Evaluación completada.' : 'Evaluación completada. El orden no es el esperado.');

      setTimeout(() => {
        onComplete(undefined);
      }, 3000);
    }
  };

  const getItemsInZone = (zoneId: string) => {
    return placedItems.filter(item => itemPositions[item.id] === zoneId);
  };

  const availableItems = () => {
    const placedItemIds = placedItems.map(item => item.id);
    return dragDropConfig.items.filter(item => !placedItemIds.includes(item.id));
  };

  return (
    <div className="drag-drop-scene" aria-labelledby="drag-drop-title">
      <h2 id="drag-drop-title" className="sr-only">Minijuego de asociar elementos</h2>
      
      <div aria-live="polite" aria-atomic="true" className="sr-only">
        {announcement}
      </div>

      <section className="available-items mb-8" aria-labelledby="available-items-title">
        <h3 id="available-items-title" className="text-lg font-semibold mb-3">Elementos disponibles:</h3>
        
        {availableItems().length === 0 ? (
          <p className="text-gray-500 italic">Todos los elementos han sido colocados.</p>
        ) : (
          <div className="flex flex-wrap gap-3">
            {availableItems().map((item) => {
              const isSelected = selectedItem?.id === item.id;
              return (
                <button
                  key={item.id}
                  type="button"
                  disabled={isCompleted}
                  onClick={() => handleSelectOrigin(item)}
                  aria-pressed={isSelected}
                  className={`flex items-center space-x-2 p-3 border-2 rounded-lg transition-all focus:outline-none focus:ring-4 focus:ring-blue-600 ${
                    isCompleted ? 'cursor-not-allowed opacity-60 bg-gray-200 border-gray-300' : 'cursor-pointer'
                  } ${
                    isSelected 
                      ? 'border-blue-600 bg-blue-100 ring-2 ring-blue-500 shadow-md transform scale-105' 
                      : 'border-gray-400 hover:border-blue-400'
                  } ${
                    accessibility.contrastLevel === 'high' ? 'bg-white border-black text-black font-bold' : 'bg-gray-50'
                  }`}
                  style={{ fontSize: `${accessibility.fontScale}%` }}
                >
                  {item.icon && <span aria-hidden="true" className="text-xl">{item.icon}</span>}
                  <span className="font-medium">{item.text}</span>
                </button>
              );
            })}
          </div>
        )}
      </section>

      <section className="drop-zones" aria-labelledby="zones-title">
        <h3 id="zones-title" className="text-lg font-semibold mb-3">Organiza los elementos:</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {dragDropConfig.targetZones.map((zone) => {
            const zoneItems = getItemsInZone(zone.id);
            const isSelectableTarget = selectedItem !== null && !isCompleted;

            return (
              <div
                key={zone.id}
                className={`flex flex-col p-4 border-2 rounded-lg min-h-[12rem] transition-colors ${
                  isSelectableTarget ? 'border-blue-400 bg-blue-50' : 'border-gray-300 bg-gray-50'
                } ${accessibility.contrastLevel === 'high' ? 'bg-white border-black' : ''}`}
              >
                <h4 id={`zone-${zone.id}`} className="font-semibold mb-4 text-center border-b-2 pb-2">
                  {zone.title}
                </h4>

                <ul aria-labelledby={`zone-${zone.id}`} className="flex-grow space-y-2 mb-4">
                  {zoneItems.map((item) => (
                    <li
                      key={item.id}
                      className={`flex items-center space-x-2 p-2 border rounded ${
                        accessibility.contrastLevel === 'high' ? 'bg-white border-black' : 'bg-green-100 border-green-300'
                      }`}
                    >
                      {item.icon && <span aria-hidden="true">{item.icon}</span>}
                      <span className="text-sm">{item.text}</span>
                    </li>
                  ))}
                  {zoneItems.length === 0 && (
                    <li className="text-gray-400 text-sm text-center italic" aria-hidden="true">Vacío</li>
                  )}
                </ul>

                {!isCompleted && (
                  <button
                    type="button"
                    disabled={!selectedItem}
                    onClick={() => handlePlaceToZone(zone)}
                    className={`w-full py-2 px-4 rounded font-medium transition-all focus:outline-none focus:ring-4 focus:ring-blue-600 ${
                      selectedItem 
                        ? 'bg-blue-600 text-white hover:bg-blue-700 cursor-pointer shadow-sm' 
                        : 'bg-gray-200 text-gray-500 cursor-not-allowed opacity-70'
                    }`}
                    aria-label={selectedItem ? `Mover elemento a la zona ${zone.title}` : `Zona ${zone.title} esperando selección`}
                  >
                    {selectedItem ? 'Colocar aquí' : 'Esperando elemento...'}
                  </button>
                )}
              </div>
            );
          })}
        </div>
      </section>

      {isCompleted && isCorrect !== null && (
        <div 
          role="status"
          className={`mt-6 p-4 border-2 rounded-lg text-center transition-all duration-500 ${
            isCorrect ? 'bg-green-100 border-green-500' : 'bg-red-100 border-red-500'
          }`}
        >
          <p className={`font-bold text-lg ${isCorrect ? 'text-green-800' : 'text-red-800'}`}>
            {isCorrect ? '✓ ¡Orden correcto! Buen trabajo.' : '✗ El orden no es el correcto.'}
          </p>
        </div>
      )}

      {accessibility.visualHelp && (
        <div className="mt-6 p-4 bg-blue-100 border-l-4 border-blue-500 rounded text-blue-900" role="note">
          <p className="text-sm font-medium">
            <strong>Instrucciones:</strong> Selecciona un elemento haciendo clic y luego pulsa el botón "Colocar aquí" en la zona de destino.
          </p>
        </div>
      )}
    </div>
  );
};

export default DragDropScene;