-- Migration: Add missing columns and tables
-- Run this in your Supabase SQL Editor

-- Add ppt_count column to users table if it doesn't exist
ALTER TABLE public.users 
ADD COLUMN IF NOT EXISTS ppt_count int DEFAULT 0;

-- Add mode column to sessions table if it doesn't exist
ALTER TABLE public.sessions 
ADD COLUMN IF NOT EXISTS mode text DEFAULT 'normal';

-- Add title column to sessions table if it doesn't exist
ALTER TABLE public.sessions 
ADD COLUMN IF NOT EXISTS title text;

-- Add user_id column to sessions table if it doesn't exist
ALTER TABLE public.sessions 
ADD COLUMN IF NOT EXISTS user_id uuid REFERENCES auth.users;

-- Create messages table if it doesn't exist
CREATE TABLE IF NOT EXISTS public.messages (
  id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
  session_id text REFERENCES public.sessions(session_id) ON DELETE CASCADE,
  role text NOT NULL,
  content text NOT NULL,
  created_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Enable RLS for messages
ALTER TABLE public.messages ENABLE ROW LEVEL SECURITY;

-- Allow all access for messages (simplified for development)
DROP POLICY IF EXISTS "Enable all access for messages" ON public.messages;
CREATE POLICY "Enable all access for messages" ON public.messages
  FOR ALL USING (true) WITH CHECK (true);

-- Update existing users to have ppt_count = 0 if NULL
UPDATE public.users 
SET ppt_count = 0 
WHERE ppt_count IS NULL;

-- Update existing sessions to have mode = 'normal' if NULL
UPDATE public.sessions 
SET mode = 'normal' 
WHERE mode IS NULL;
