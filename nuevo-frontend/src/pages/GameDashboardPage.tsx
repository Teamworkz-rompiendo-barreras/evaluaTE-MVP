import GameCard from "../components/GameCard";
import { useSelector } from "react-redux";
import type { RootState } from "../app/store";

const skills = [
  "Comunicación",
  "Trabajo en equipo",
  "Autonomía",
  "Gestión del tiempo",
  "Flexibilidad",
  "Pensamiento crítico",
  "Resolución de problemas",
  "Creatividad",
  "Empatía",
  "Liderazgo",
];

export default function GameDashboardPage() {
  const completed = useSelector((state: RootState) => state.progress.completed);
  return (
        <main className="min-h-screen p-6 flex flex-col items-center gap-6">
       <h1 className="text-2xl font-bold">Elige un minijuego</h1>
 
       <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
    
        {skills.map((skill, idx) => {
          const locked = idx !== 0 && !completed[idx - 1];
          // idx=0 desbloqueado; idx>0 desbloqueado si el anterior está complete
          return (
            <GameCard
              key={idx}
              id={idx}
              name={skill}
              locked={locked}
            />
          );
        })}
       </div>
     </main>
   );
}
