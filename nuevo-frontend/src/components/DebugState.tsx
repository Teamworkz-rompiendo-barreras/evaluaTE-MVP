import React from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '../app/store';

const DebugState: React.FC = () => {
  const personal = useSelector((state: RootState) => state.personal);
  const game = useSelector((state: RootState) => state.game);

  const hasContactData = Boolean(personal.firstName && personal.lastName);
  const hasPreferences = personal?.jobPreferences && (
    typeof personal.jobPreferences === 'string' 
      ? personal.jobPreferences.trim() !== ''
      : personal.jobPreferences.areas && personal.jobPreferences.areas.length > 0
  );
  const hasPersonalData = hasContactData && hasPreferences;

  return (
    <div className="fixed top-4 left-4 bg-black text-white p-4 rounded-lg text-xs max-w-md z-50">
      <h3 className="font-bold mb-2">🔍 DEBUG STATE</h3>
      
      <div className="space-y-2">
        <div>
          <strong>Contact Data:</strong> {hasContactData ? '✅' : '❌'}
          <br />
          firstName: {'"'}{personal.firstName}{'"'}
          <br />
          lastName: {'"'}{personal.lastName}{'"'}
        </div>
        
        <div>
          <strong>Preferences:</strong> {hasPreferences ? '✅' : '❌'}
          <br />
          jobPreferences type: {typeof personal.jobPreferences}
          <br />
          jobPreferences value: {JSON.stringify(personal.jobPreferences)}
        </div>
        
        <div>
          <strong>Personal Data Complete:</strong> {hasPersonalData ? '✅' : '❌'}
        </div>
        
        <div>
          <strong>Completed Games:</strong> {game.completedGames.length}
        </div>
        
        <div>
          <strong>Current Route:</strong> {window.location.pathname}
        </div>
      </div>
    </div>
  );
};

export default DebugState; 