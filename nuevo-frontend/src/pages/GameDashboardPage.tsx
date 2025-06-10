import GameCard from "../components/GameCard";

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
  return (
    <main className="min-h-screen p-6 flex flex-col items-center gap-6">
      <h1 className="text-2xl font-bold">Elige un minijuego</h1>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
        {skills.map((skill, idx) => (
          <GameCard
            key={idx}
            id={idx}
            name={skill}
            locked={idx !== 0}   // sólo desbloqueado el primero
          />
        ))}
      </div>
    </main>
  );
}
