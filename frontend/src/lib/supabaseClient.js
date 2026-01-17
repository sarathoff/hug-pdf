import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.REACT_APP_SUPABASE_URL;
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
    console.error('Missing Supabase environment variables');
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
    auth: {
        autoRefreshToken: true,
        persistSession: true,
        detectSessionInUrl: true,
        storage: window.localStorage,
        flowType: 'pkce', // Use PKCE flow for better security and session persistence
        debug: process.env.NODE_ENV === 'development', // Enable debug logging in development
    },
});

// Debug: Log when session changes
if (process.env.NODE_ENV === 'development') {
    supabase.auth.onAuthStateChange((event, session) => {
        console.log('🔐 Auth state changed:', event, session ? 'Session exists' : 'No session');
        if (event === 'SIGNED_OUT') {
            console.warn('⚠️ User was signed out!');
        }
    });
}
