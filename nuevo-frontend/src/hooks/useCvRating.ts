import { useState } from "react";
import { buildApiUrl } from "../config/api";

export type CvStars = 1 | 2 | 3 | 4 | 5;

type UseCvRatingReturn = {
  rateCv: (stars: CvStars) => Promise<void>;
  rating: number | null;
  ratingSaving: boolean;
  ratingError: string | null;
};

export default function useCvRating(userId: string, reportId: string): UseCvRatingReturn {
  const [rating, setRating] = useState<number | null>(null);
  const [ratingSaving, setRatingSaving] = useState<boolean>(false);
  const [ratingError, setRatingError] = useState<string | null>(null);

  const rateCv = async (stars: CvStars) => {
    try {
      setRatingSaving(true);
      setRatingError(null);

      const res = await fetch(buildApiUrl('/api/report/feedback'), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ userId, reportId, rating: stars }),
      });

      const data: unknown = await res.json();
      if (!res.ok) throw new Error((data as { message?: string })?.message || "Error guardando la valoración");

      const newRating = (data as { rating?: number })?.rating;
      if (typeof newRating === "number") setRating(newRating);
    } catch (err: unknown) {
      setRatingError(err instanceof Error ? err.message : "Error desconocido");
    } finally {
      setRatingSaving(false);
    }
  };

  return { rateCv, rating, ratingSaving, ratingError };
}


