export interface CvEvidence {
  structure: string;
  coherence: string;
  key_info: string;
  clarity: string;
  style: string;
}

export interface CvAnalysis {
  structure_score: number;
  coherence_score: number;
  key_info_score: number;
  clarity_score: number;
  style_score: number;
  evidence: CvEvidence;
  corrections: string[];
  reordering_suggestions: string[];
  observations: string[];
  actions: string[];
}
