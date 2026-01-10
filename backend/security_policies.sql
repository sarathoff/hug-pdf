-- RLS Security Hardening for HugPDF
-- Run this script in the Supabase SQL Editor to secure your tables.

-- ==============================================================================
-- 1. PAYMENT SESSIONS TABLE
-- Remove the overly permissive policy that allows public access
-- ==============================================================================

DROP POLICY IF EXISTS "Enable all access for payment sessions" ON public.payment_sessions;

-- Create restrictive policies for payment_sessions
-- Only the backend (service_role) needs full access. 
-- Authenticated users generally don't need to query this table directly for this app, 
-- but if they do, they should only see their own sessions.

-- Allow authenticated users to SELECT their own payment sessions
CREATE POLICY "payment_sessions_select_own" ON public.payment_sessions
  FOR SELECT
  TO authenticated
  USING ((SELECT auth.uid())::uuid = user_id);

-- Note: We DO NOT add INSERT/UPDATE/DELETE policies for authenticated users.
-- All modifications must be done via the backend (Server-side creation) using the Service Role.


-- ==============================================================================
-- 2. USERS TABLE
-- Enforce strict ownership policies
-- ==============================================================================

-- Allow authenticated users to SELECT their own user row
CREATE POLICY "users_select_own" ON public.users
  FOR SELECT
  TO authenticated
  USING ((SELECT auth.uid())::uuid = user_id);

-- Allow authenticated users to UPDATE their own user row
-- (excluding credits/plan which should only be updated by backend)
-- Note: Supabase RLS is row-level, not column-level. 
-- Ideally, move sensitive columns to a separate table or use a stored procedure.
-- For now, we allow updates but enforce ownership.
CREATE POLICY "users_update_own" ON public.users
  FOR UPDATE
  TO authenticated
  USING ((SELECT auth.uid())::uuid = user_id)
  WITH CHECK ((SELECT auth.uid())::uuid = user_id);

-- Allow authenticated users to DELETE their own user row
CREATE POLICY "users_delete_own" ON public.users
  FOR DELETE
  TO authenticated
  USING ((SELECT auth.uid())::uuid = user_id);

-- IMPORTANT: NO INSERT POLICY FOR AUTHENTICATED USERS
-- Clients cannot create user records directly. 
-- User records must be created by the backend (server.py) upon successful authentication check.
