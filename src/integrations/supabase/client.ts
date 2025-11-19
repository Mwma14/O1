import { createClient } from '@supabase/supabase-js';
import type { Database } from './types';

const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL || "https://dwaxejcqvtkeavngwrzk.supabase.co";
const SUPABASE_PUBLISHABLE_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY || "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR3YXhlamNxdnRrZWF2bmd3cnprIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjM0NDY2NTIsImV4cCI6MjA3OTAyMjY1Mn0.o5kO7P4lpnQU8brNliTORSYBZPOwdt8anp9RvuCM6Uo";

// Import the supabase client like this:
// import { supabase } from "@/integrations/supabase/client";

export const supabase = createClient<Database>(SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY, {
  auth: {
    storage: localStorage,
    persistSession: true,
    autoRefreshToken: true,
  }
});