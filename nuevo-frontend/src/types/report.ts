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

export interface CvExperienceItem {
  title?: string;
  company?: string;
  start_date?: string;
  end_date?: string;
  description?: string;
  [key: string]: unknown;
}

export interface CvEducationItem {
  degree?: string;
  institution?: string;
  start_date?: string;
  end_date?: string;
  [key: string]: unknown;
}

export interface CvSoftwareItem {
  name: string;
  level?: string;
  [key: string]: unknown;
}

export interface CvLanguage {
  name: string;
  level?: string;
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
  experience_detailed?: CvExperienceItem[];
  education_detailed?: CvEducationItem[];
  software?: CvSoftwareItem[];
  skills?: CvSoftwareItem[];
  languages?: CvLanguage[];
  raw_text?: string;
  [key: string]: unknown;
}
