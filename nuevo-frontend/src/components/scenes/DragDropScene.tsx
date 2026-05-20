import React, { useState } from 'react';
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
  onHelpRequest: _onHelpRequest,
  onAdaptation: _onAdaptation,
  accessibility
}) => {
  const [draggedItem, setDraggedItem] = useState<DragDropItem | null>(null);
  const [itemPositions, setItemPositions] = useState<Record<string, string>>({});
  const [placedItems, setPlacedItems] = useState<DragDropItem[]>([]);
  const [isCompleted, setIsCompleted] = useState(false);
  const [isCorrect, setIsCorrect] = useState<boolean | null>(null);

  const dragDropConfig = scene.dragDropConfig;
  if (!dragDropConfig) return <div>Configuración de arrastrar y soltar no encontrada</div>;

  const handleDragStart = (e: React.DragEvent, item: DragDropItem) => {
    setDraggedItem(item);
    e.dataTransfer.setData('text/plain', item.id);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };

  const handleDrop = (e: React.DragEvent, zone: DragDropZone) => {
    e.preventDefault();
    if (isCompleted || !draggedItem) return;

    const newPlacedItems = [...placedItems, draggedItem];
    setPlacedItems(newPlacedItems);

    const itemId = draggedItem.id;
    const newPositions = { ...itemPositions, [itemId]: zone.id };
    setItemPositions(newPositions);
    setDraggedItem(null);

    const allItemsPlaced = dragDropConfig.items.length === newPlacedItems.length;

    if (allItemsPlaced) {
      setIsCompleted(true);

      if (dragDropConfig.correctOrder) {
        const placedOrderIds = newPlacedItems.map(item => item.id);
        const isOrderCorrect = JSON.stringify(placedOrderIds) === JSON.stringify(dragDropConfig.correctOrder);
        setIsCorrect(isOrderCorrect);
      } else {
        setIsCorrect(true);
      }

      setTimeout(() => {
        onComplete(undefined);
      }, 2500);
    }
  };

  const handleDragEnd = () => {
    setDraggedItem(null);
  };

  const getItemsInZone = (zoneId: string) => {
      return placedItems.filter(item => itemPositions[item.id] === zoneId);
  };

  const availableItems = () => {
    const placedItemIds = placedItems.map(item => item.id);
    return dragDropConfig.items.filter(item => !placedItemIds.includes(item.id));
  };

  return (
    <div className="drag-drop-scene">
      <div className="available-items mb-6">
        <h3 className="text-lg font-semibold mb-3">Elementos disponibles:</h3>
        <div className="flex flex-wrap gap-3">
          {availableItems().map((item) => (
            <div
              key={item.id}
              draggable={!isCompleted}
              onDragStart={(e) => handleDragStart(e, item)}
              onDragEnd={handleDragEnd}
              className={`draggable-item p-3 border-2 border-dashed border-gray-400 rounded-lg transition-colors ${
                isCompleted ? 'cursor-not-allowed opacity-60' : 'cursor-move hover:border-blue-400'
              } ${
                draggedItem?.id === item.id ? 'opacity-50' : ''
              } ${
                accessibility.contrastLevel === 'high'
                  ? 'bg-white border-black'
                  : 'bg-gray-100'
              }`}
              style={{ fontSize: `${accessibility.fontScale}%` }}
            >
              <div className="flex items-center space-x-2">
                {item.icon && <span>{item.icon}</span>}
                <span className="font-medium">{item.text}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="drop-zones">
        <h3 className="text-lg font-semibold mb-3">Organiza los elementos:</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {dragDropConfig.targetZones.map((zone) => (
            <div
              key={zone.id}
              onDragOver={handleDragOver}
              onDrop={(e) => handleDrop(e, zone)}
              className={`drop-zone p-4 border-2 border-dashed border-gray-300 rounded-lg min-h-32 ${
                draggedItem && !isCompleted ? 'border-blue-400 bg-blue-50' : ''
              } ${
                accessibility.contrastLevel === 'high'
                  ? 'bg-white border-black'
                  : 'bg-gray-50'
              }`}
            >
              <h4 className="font-semibold mb-2 text-center">{zone.title}</h4>

              <div className="space-y-2">
                {getItemsInZone(zone.id).map((item) => (
                  <div
                    key={item.id}
                    className={`placed-item p-2 border rounded ${
                      accessibility.contrastLevel === 'high'
                        ? 'bg-white border-black'
                        : 'bg-green-100 border-green-300'
                    }`}
                  >
                    <div className="flex items-center space-x-2">
                      {item.icon && <span>{item.icon}</span>}
                      <span className="text-sm">{item.text}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {isCompleted && isCorrect !== null && (
        <div className={`mt-4 p-4 border rounded text-center transition-all duration-500 ${
            isCorrect ? 'bg-green-100 border-green-300' : 'bg-red-100 border-red-300'
          }`}>
          <p className={`font-semibold ${
              isCorrect ? 'text-green-800' : 'text-red-800'
            }`}>
            {isCorrect ? '¡Orden correcto! Buen trabajo.' : 'El orden no es el correcto.'}
          </p>
        </div>
      )}

      {accessibility.visualHelp && (
        <div className="mt-4 p-3 bg-blue-100 border border-blue-300 rounded">
          <p className="text-blue-800 text-sm">
            💡 Arrastra los elementos a las zonas correspondientes para organizarlos.
          </p>
        </div>
      )}
    </div>
  );
};

export default DragDropScene;
