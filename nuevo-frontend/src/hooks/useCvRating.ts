import { useCallback, useState } from 'react';

type FeedbackPayload = {
  userId: string;
  reportId: string;
  rating: number;
  comment?: string;
  createdAt?: string;
};

export default function useCvRating(userId?: string, reportId?: string) {
  const [rating, setRating] = useState<number | null>(null);
  const [ratingSaving, setRatingSaving] = useState(false);
  const [ratingError, setRatingError] = useState<string | null>(null);

  const rateCv = useCallback(
    async (value: number, comment?: string) => {
      if (!userId || !reportId) {
        setRatingError('Falta userId o reportId');
        return;
      }
      setRatingSaving(true);
      setRatingError(null);
      setRating(value);
      try {
        const payload: FeedbackPayload = {
          userId,
          reportId,
          rating: value,
          comment,
          createdAt: new Date().toISOString(),
        };
        const base = (import.meta as any).env?.VITE_API_URL || '';
        const url = `${base}/api/report/feedback`;
        const res = await fetch(url, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
      } catch (e: any) {
        setRatingError(e?.message || 'Error al guardar la valoración');
        setRating(null);
      } finally {
        setRatingSaving(false);
      }
    },
    [userId, reportId]
  );

  return { rateCv, rating, ratingSaving, ratingError };
}


