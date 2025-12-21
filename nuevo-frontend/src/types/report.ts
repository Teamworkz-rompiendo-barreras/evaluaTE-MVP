export interface CvEvidence {
  structure: string;
  coherence: string;
  key_info: string;
  clarity: string;
  style: string;
}

export interface CvContact {
  emails?: string[];
  phones?: string[];
  location?: string;
  linkedin?: string;
}

export interface CvItem {
  title?: string;
  subtitle?: string;
  period?: string;
  level?: string;
  detail?: string;
  [key: string]: unknown;
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
  /** Información estructurada adicional devuelta por el analizador */
  contact?: CvContact;
  experience_detailed?: CvItem[];
  education_detailed?: CvItem[];
  software?: CvItem[];
  skills?: CvItem[];
  languages?: CvItem[];
  raw_text?: string;
  [key: string]: unknown;
}
