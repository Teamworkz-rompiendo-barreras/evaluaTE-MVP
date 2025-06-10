import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useDispatch } from "react-redux";
import { markComplete } from "../app/store";
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
    <main className="flex items-center justify-center min-h-screen">
      <h2 className="text-xl font-semibold">Minijuego en construcción…</h2>
    </main>
  );
}
