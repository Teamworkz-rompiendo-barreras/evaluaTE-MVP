import { Link } from "react-router-dom";

interface GameCardProps {
  id: number;
  name: string;
  locked: boolean;
}

export default function GameCard({ id, name, locked }: GameCardProps) {
  return (
    <Link
      to={locked ? "#" : `/games/${id}`}
      className={`flex flex-col items-center justify-center p-4 rounded-xl w-32 h-32
                  text-center border transition
                  ${locked ? "opacity-40 cursor-not-allowed"
                           : "hover:scale-105 bg-white shadow"}`}
      aria-disabled={locked}
    >
      <div className="text-4xl mb-2">{locked ? "🔒" : "🎮"}</div>
      <span className="text-sm font-medium">{name}</span>
    </Link>
  );
}
