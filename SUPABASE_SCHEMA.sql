-- ⚠️ WARNING: THIS WILL DELETE EXISTING DATA IN THESE TABLES
-- We need to do this to fix the "uuid vs text" type mismatch error

drop table if exists public.users cascade;
drop table if exists public.sessions cascade;
drop table if exists public.payment_sessions cascade;
drop table if exists public.status_checks cascade;

-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- USERS TABLE
create table public.users (
  id uuid default uuid_generate_v4() primary key,
  user_id uuid references auth.users not null unique,
  email text,
  credits int default 3,
  plan text default 'free',
  ppt_count int default 0,
  early_adopter boolean default false,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  updated_at timestamp with time zone default timezone('utc'::text, now())
);

-- Enable RLS for users
alter table public.users enable row level security;

-- Users policies
create policy "Users can view their own data" on public.users
  for select using (auth.uid() = user_id);

create policy "Users can insert their own data" on public.users
  for insert with check (auth.uid() = user_id);
  
create policy "Users can update their own data" on public.users
  for update using (auth.uid() = user_id);

-- SESSIONS TABLE
create table public.sessions (
  session_id text primary key,
  user_id uuid references auth.users,
  messages jsonb default '[]'::jsonb,
  current_html text,
  current_latex text,
  mode text default 'normal',
  title text,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

alter table public.sessions enable row level security;

-- Allow all access for sessions (simplified for development)
create policy "Enable all access for sessions" on public.sessions
  for all using (true) with check (true);

-- PAYMENT_SESSIONS TABLE
create table public.payment_sessions (
  session_id text primary key,
  user_id uuid references auth.users,
  plan text,
  credits_added int,
  processed_at timestamp with time zone
);

alter table public.payment_sessions enable row level security;

-- Allow all access for payment_sessions (simplified)
create policy "Enable all access for payment sessions" on public.payment_sessions
  for all using (true) with check (true);

-- STATUS_CHECKS TABLE
create table public.status_checks (
  id text primary key,
  client_name text,
  timestamp timestamp with time zone
);

alter table public.status_checks enable row level security;

create policy "Enable all access for status checks" on public.status_checks
  for all using (true) with check (true);
