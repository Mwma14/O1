-- Proper RLS setup for orders table
-- This allows anyone (including the bot) to create orders

-- Make sure RLS is enabled
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

-- Drop all existing policies
DROP POLICY IF EXISTS "Anyone can create orders" ON orders;
DROP POLICY IF EXISTS "Users can view their own orders" ON orders;
DROP POLICY IF EXISTS "Admins can view all orders" ON orders;
DROP POLICY IF EXISTS "Admins can update orders" ON orders;

-- Create a simple policy that allows ALL operations for service/anon role
CREATE POLICY "Allow anonymous inserts" ON orders
    FOR INSERT 
    TO anon, authenticated
    WITH CHECK (true);

-- Allow users to view their own orders
CREATE POLICY "Users view own orders" ON orders
    FOR SELECT
    TO authenticated
    USING (
        telegram_user_id IN (
            SELECT telegram_user_id FROM profiles WHERE id = auth.uid()
        )
    );

-- Allow admins to view all orders
CREATE POLICY "Admins view all orders" ON orders
    FOR SELECT
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM user_roles
            WHERE user_id = auth.uid() AND role = 'admin'
        )
    );

-- Allow admins to update orders
CREATE POLICY "Admins update orders" ON orders
    FOR UPDATE
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM user_roles
            WHERE user_id = auth.uid() AND role = 'admin'
        )
    );
