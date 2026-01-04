-- Add current_latex column to sessions table in Supabase

-- Run this SQL in your Supabase SQL Editor:

ALTER TABLE sessions 
ADD COLUMN current_latex TEXT;

-- Optional: Add an index if you'll be querying by this field
-- CREATE INDEX idx_sessions_latex ON sessions(current_latex);
