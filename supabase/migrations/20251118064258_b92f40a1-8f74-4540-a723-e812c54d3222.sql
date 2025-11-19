-- Fix search_path for functions
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION public.generate_order_string()
RETURNS TEXT
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  order_date TEXT;
  order_count INTEGER;
  order_num TEXT;
BEGIN
  order_date := TO_CHAR(NOW(), 'YYYYMMDD');
  
  SELECT COUNT(*) + 1 INTO order_count
  FROM public.orders
  WHERE order_string LIKE 'ORD-' || order_date || '%';
  
  order_num := LPAD(order_count::TEXT, 3, '0');
  
  RETURN 'ORD-' || order_date || '-' || order_num;
END;
$$;