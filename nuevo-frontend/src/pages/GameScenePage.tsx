import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useDispatch } from "react-redux";
import { markComplete } from "../app/store";

interface MCQ {
  question: string;
  options: { id: string; label: string; isCorrect: boolean }[];
}

const sampleMCQs: Record<string, MCQ> = {
  "0": {
    question: "¿Cuál es la capital de España?",
    options: [
      { id: "a", label: "Madrid",    isCorrect: true  },
      { id: "b", label: "Barcelona", isCorrect: false },
      { id: "c", label: "Valencia",  isCorrect: false },
    ],
  },
  // Más escenas (1, 2, …) las añadirás aquí cuando las tengas
};
export default function GameScenePage() {
  const { id = "0" } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const mcq = sampleMCQs[id];
  const [selected, setSelected] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<"correct" | "wrong" | null>(null);

  useEffect(() => {
    if (feedback === "correct") {
      const timer = setTimeout(() => {
       // Despacha la acción para marcar este id como completo
       dispatch(markComplete(Number(id)));
        navigate("/games");
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, [feedback, navigate, dispatch, id]);
 return (
    <main className="p-6 flex flex-col items-center gap-6">
      <h1 className="text-3xl font-bold">
        Minijuego {parseInt(id, 10) + 1}
      </h1>
      <h2 className="text-xl font-semibold">{mcq.question}</h2>
      <div className="flex flex-col gap-4">
        {mcq.options.map((opt) => (
          <button
            key={opt.id}
            onClick={() => {
              if (feedback) return;
              setSelected(opt.id);
              setFeedback(opt.isCorrect ? "correct" : "wrong");
            }}
            className={`px-4 py-2 rounded border ${
              selected === opt.id
                ? feedback === "correct"
                  ? "bg-green-200"
                  : "bg-red-200"
                : "hover:bg-gray-100"
            }`}
          >
            {opt.label}
          </button>
        ))}
      </div>

      {feedback === "correct" && (
        <p className="mt-4 text-green-700">¡Correcto! Volviendo al tablero…</p>
      )}
      {feedback === "wrong" && (
        <p className="mt-4 text-red-700">Incorrecto. Inténtalo de nuevo.</p>
      )}
    </main>
  );
}
