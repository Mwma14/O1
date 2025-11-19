-- Fix RLS policy for orders table
-- Allow anonymous users to SELECT orders after INSERT
-- This is required because Supabase client automatically fetches inserted rows

CREATE POLICY "Anonymous can select orders"
ON public.orders FOR SELECT
TO anon
USING (true);
