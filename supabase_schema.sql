-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- 1. Users Table (extends Supabase Auth)
create table public.users (
  id uuid references auth.users not null primary key,
  first_name text,
  last_name text,
  email text unique,
  whatsapp text,
  work_mode text, -- remoto, presencial, híbrido
  availability text, -- mañana, tarde, completa
  start_date text, -- inmediata, 15_días, 1_mes
  willing_to_relocate boolean default false,
  has_disability_cert boolean default false,
  job_preferences jsonb default '{}'::jsonb,
  accessibility_settings jsonb default '{}'::jsonb,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- Enable RLS for users
alter table public.users enable row level security;

create policy "Users can view and edit their own profile"
  on public.users for all
  using (auth.uid() = id);

-- 2. Game Sessions Table
create table public.game_sessions (
  id uuid default uuid_generate_v4() primary key,
  user_id uuid references public.users(id) not null,
  game_id text not null,
  completed boolean default false,
  score integer default 0,
  started_at timestamptz default now(),
  completed_at timestamptz
);

-- Enable RLS for game_sessions
alter table public.game_sessions enable row level security;

create policy "Users can manage their own game sessions"
  on public.game_sessions for all
  using (auth.uid() = user_id);

-- 3. Game Logs Table (Detail)
create table public.game_logs (
  id uuid default uuid_generate_v4() primary key,
  session_id uuid references public.game_sessions(id) not null,
  scene_id text not null,
  selected_option_id text,
  time_spent_ms integer,
  help_used boolean default false,
  adaptations text[],
  skill_impacts jsonb default '{}'::jsonb,
  created_at timestamptz default now()
);

-- Enable RLS for game_logs
alter table public.game_logs enable row level security;

create policy "Users can manage their own game logs"
  on public.game_logs for all
  using (
    exists (
      select 1 from public.game_sessions
      where id = game_logs.session_id and user_id = auth.uid()
    )
  );

-- 4. Soft Skill Results
create table public.soft_skill_results (
  id uuid default uuid_generate_v4() primary key,
  user_id uuid references public.users(id) not null,
  session_id uuid references public.game_sessions(id),
  skill text not null,
  score integer not null,
  level text, -- bajo, medio, alto
  confidence real default 1.0,
  feedback text,
  created_at timestamptz default now()
);

-- Enable RLS for soft_skill_results
alter table public.soft_skill_results enable row level security;

create policy "Users can view their own soft skills"
  on public.soft_skill_results for all
  using (auth.uid() = user_id);

-- 5. CV Analyses
create table public.cv_analyses (
  id uuid default uuid_generate_v4() primary key,
  user_id uuid references public.users(id) not null,
  cv_file_path text, -- Path in Storage
  structure_score integer check (structure_score between 1 and 5),
  coherence_score integer check (coherence_score between 1 and 5),
  key_info_score integer check (key_info_score between 1 and 5),
  clarity_score integer check (clarity_score between 1 and 5),
  style_score integer check (style_score between 1 and 5),
  evidence jsonb default '{}'::jsonb,
  corrections text[],
  reordering_suggestions text[],
  raw_extraction jsonb, -- JSON completo extraído
  created_at timestamptz default now()
);

-- Enable RLS for cv_analyses
alter table public.cv_analyses enable row level security;

create policy "Users can manage their own CV analyses"
  on public.cv_analyses for all
  using (auth.uid() = user_id);

-- 6. Employability Reports
create table public.employability_reports (
  id uuid default uuid_generate_v4() primary key,
  user_id uuid references public.users(id) not null,
  cv_analysis_id uuid references public.cv_analyses(id),
  employability_score integer check (employability_score between 0 and 100),
  level text,
  report_json jsonb not null, -- Full Gemini JSON response
  pdf_url text,
  created_at timestamptz default now()
);

-- Enable RLS for employability_reports
alter table public.employability_reports enable row level security;

create policy "Users can view their own reports"
  on public.employability_reports for all
  using (auth.uid() = user_id);

-- Storage bucket setup (Optional: You might need to create this in the UI first)
-- insert into storage.buckets (id, name, public) values ('cv-uploads', 'cv-uploads', false);

-- Storage Policy
-- create policy "Users can upload their own CVs"
-- on storage.objects for insert
-- with check ( bucket_id = 'cv-uploads' and auth.uid() = owner );

-- create policy "Users can view their own CVs"
-- on storage.objects for select
-- using ( bucket_id = 'cv-uploads' and auth.uid() = owner );
