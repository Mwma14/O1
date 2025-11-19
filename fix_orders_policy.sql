-- Fix Row Level Security policy for orders table
-- Run this in your Supabase SQL Editor if you're getting RLS errors

-- First, drop existing policies if they exist
DROP POLICY IF EXISTS "Anyone can create orders" ON orders;
DROP POLICY IF EXISTS "Users can view their own orders" ON orders;
DROP POLICY IF EXISTS "Admins can view all orders" ON orders;
DROP POLICY IF EXISTS "Admins can update orders" ON orders;

-- Create policy to allow anyone to insert orders
CREATE POLICY "Anyone can create orders" ON orders
    FOR INSERT WITH CHECK (true);

-- Create policy to allow users to view their own orders
CREATE POLICY "Users can view their own orders" ON orders
    FOR SELECT USING (
        telegram_user_id IN (
            SELECT telegram_user_id FROM profiles WHERE id = auth.uid()
        )
    );

-- Create policy to allow admins to view all orders
CREATE POLICY "Admins can view all orders" ON orders
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM user_roles
            WHERE user_id = auth.uid() AND role = 'admin'
        )
    );

-- Create policy to allow admins to update orders
CREATE POLICY "Admins can update orders" ON orders
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM user_roles
            WHERE user_id = auth.uid() AND role = 'admin'
        )
    );
