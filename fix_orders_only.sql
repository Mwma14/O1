-- Simple fix for orders table RLS policy
-- This will allow the bot to create orders

-- Drop and recreate the "Anyone can create orders" policy
DROP POLICY IF EXISTS "Anyone can create orders" ON orders;

CREATE POLICY "Anyone can create orders" ON orders
    FOR INSERT WITH CHECK (true);
