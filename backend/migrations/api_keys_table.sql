-- Migration: Create API Keys tables for developer API access
-- Run this in your Supabase SQL Editor

-- API KEYS TABLE
CREATE TABLE IF NOT EXISTS public.api_keys (
  id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id uuid REFERENCES auth.users NOT NULL,
  name text NOT NULL,
  key_hash text NOT NULL UNIQUE,          -- SHA-256 hash of the API key (never store plaintext)
  key_prefix text NOT NULL,               -- First 8 chars + "..." for display only
  tier text DEFAULT 'free' NOT NULL,      -- 'free', 'pro', 'enterprise'
  is_active boolean DEFAULT true NOT NULL,
  created_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL,
  last_used_at timestamp with time zone,
  requests_count integer DEFAULT 0 NOT NULL,
  requests_limit integer DEFAULT 1000 NOT NULL
);

-- Index for fast lookups by hash
CREATE INDEX IF NOT EXISTS api_keys_key_hash_idx ON public.api_keys (key_hash);
-- Index for listing user's keys
CREATE INDEX IF NOT EXISTS api_keys_user_id_idx ON public.api_keys (user_id);

-- Enable RLS
ALTER TABLE public.api_keys ENABLE ROW LEVEL SECURITY;

-- Only the service role (admin) can read/write api_keys (backend uses service role key)
-- Users access their keys only through the backend API, not directly via Supabase client
CREATE POLICY "Service role can manage all api_keys" ON public.api_keys
  FOR ALL USING (true) WITH CHECK (true);


-- API USAGE TABLE (for analytics/tracking)
CREATE TABLE IF NOT EXISTS public.api_usage (
  id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
  api_key_id uuid REFERENCES public.api_keys(id) ON DELETE CASCADE NOT NULL,
  endpoint text NOT NULL,
  status_code integer NOT NULL,
  created_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE INDEX IF NOT EXISTS api_usage_key_id_idx ON public.api_usage (api_key_id);

ALTER TABLE public.api_usage ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role can manage all api_usage" ON public.api_usage
  FOR ALL USING (true) WITH CHECK (true);


-- RPC function to safely increment request count
CREATE OR REPLACE FUNCTION increment_api_key_requests(key_id uuid)
RETURNS void AS $$
BEGIN
  UPDATE public.api_keys
  SET requests_count = requests_count + 1
  WHERE id = key_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
