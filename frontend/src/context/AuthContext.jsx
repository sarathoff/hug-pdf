import React, { createContext, useState, useContext, useEffect, useCallback } from 'react';
import { supabase } from '../lib/supabaseClient';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchUserData = useCallback(async (userId) => {
    try {
      // Fetch user credits and plan from backend
      const { data, error } = await supabase
        .from('users')
        .select('*')
        .eq('user_id', userId)
        .single();

      if (error) throw error;
      return data;
    } catch (error) {
      console.error('Error fetching user data:', error);
      return null;
    }
  }, []);

  const syncUserToBackend = useCallback(async (supabaseUser) => {
    try {
      // Check if user exists in our users table
      const { data: existingUser } = await supabase
        .from('users')
        .select('*')
        .eq('user_id', supabaseUser.id)
        .single();

      if (!existingUser) {
        // Create new user with 3 free credits
        const { error } = await supabase
          .from('users')
          .insert({
            user_id: supabaseUser.id,
            email: supabaseUser.email,
            credits: 3,
            plan: 'free',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          });

        if (error) throw error;

        return {
          user_id: supabaseUser.id,
          email: supabaseUser.email,
          credits: 3,
          plan: 'free',
          early_adopter: false,
        };
      }

      return existingUser;
    } catch (error) {
      console.error('Error syncing user to backend:', error);
      // Fallback: If backend sync fails (e.g. network), return basic user info from session
      // This prevents "auto-logout" when DB is unreachable but session is valid
      return {
        user_id: supabaseUser.id,
        email: supabaseUser.email,
        credits: 0, // Assume 0 until sync works, better than logout
        plan: 'free',
        error: true
      };
    }
  }, []);

  useEffect(() => {
    // Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      if (session?.user) {
        syncUserToBackend(session.user).then((userData) => {
          setUser(userData);
          setLoading(false);
        });
      } else {
        setLoading(false);
      }
    });

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (event, session) => {
      console.log('🔐 AuthContext: Auth state change event:', event);
      console.log('Session data:', session ? 'Session exists' : 'No session');

      setSession(session);
      if (session?.user) {
        console.log('User authenticated:', session.user.email);
        const userData = await syncUserToBackend(session.user);
        setUser(userData);
      } else {
        console.warn('No session - user will be set to null');
        setUser(null);
      }
      setLoading(false);
    });

    return () => subscription.unsubscribe();
  }, [syncUserToBackend]);

  // Real-time subscription for user data (updates credits instantly)
  useEffect(() => {
    if (!user?.user_id) return;

    let channel;

    try {
      channel = supabase
        .channel('public:users')
        .on(
          'postgres_changes',
          {
            event: 'UPDATE',
            schema: 'public',
            table: 'users',
            filter: `user_id=eq.${user.user_id}`,
          },
          (payload) => {
            console.log('Realtime user update:', payload);
            setUser((prev) => ({ ...prev, ...payload.new }));
          }
        )
        .subscribe((status, err) => {
          if (err) {
            console.error('Realtime subscription error:', err);
          } else {
            console.log('Realtime subscription status:', status);
          }
        });
    } catch (error) {
      console.error('Error setting up realtime subscription:', error);
    }

    return () => {
      if (channel) {
        supabase.removeChannel(channel).catch(err => {
          console.warn('Error removing channel:', err);
        });
      }
    };
  }, [user?.user_id]);

  // Automatic token refresh
  useEffect(() => {
    if (!session) return;

    const setupTokenRefresh = () => {
      const expiresAt = session.expires_at; // Unix timestamp in seconds
      if (!expiresAt) return;

      const now = Math.floor(Date.now() / 1000); // Current time in seconds
      const expiresIn = expiresAt - now; // Time until expiration in seconds

      // Refresh 5 minutes (300 seconds) before expiration
      const refreshIn = Math.max(0, (expiresIn - 300) * 1000); // Convert to milliseconds

      console.log(`Token expires in ${expiresIn} seconds. Refreshing in ${refreshIn / 1000} seconds.`);

      const timeoutId = setTimeout(async () => {
        console.log('Refreshing token...');
        try {
          const { data, error } = await supabase.auth.refreshSession();
          if (error) {
            console.error('Token refresh failed:', error);

            // Only log out on critical auth errors, not network issues
            // Check if it's an auth error (invalid_grant, etc.) vs network error
            if (error.message?.includes('invalid') || error.message?.includes('expired')) {
              console.warn('Critical auth error, logging out user');
              await supabase.auth.signOut();
              setSession(null);
              setUser(null);
            } else {
              console.warn('Token refresh failed but keeping user logged in. Will retry on next attempt.');
              // Don't log out - user can continue using the app
              // The next API call will trigger a new refresh attempt
            }
          } else {
            console.log('Token refreshed successfully');
            setSession(data.session);
          }
        } catch (err) {
          console.error('Token refresh error:', err);
          // Don't automatically log out on network errors
          console.warn('Token refresh error, but keeping user logged in');
        }
      }, refreshIn);

      return () => clearTimeout(timeoutId);
    };

    const cleanup = setupTokenRefresh();
    return cleanup;
  }, [session]);

  const register = async (email, password) => {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        emailRedirectTo: `${window.location.origin}/auth`,
      },
    });

    if (error) throw error;
    return data;
  };

  const login = async (email, password) => {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    if (error) throw error;
    return data;
  };

  const loginWithGoogle = async () => {
    const { data, error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: `${window.location.origin}/`,
        queryParams: {
          access_type: 'offline',
          prompt: 'consent',
        },
      },
    });

    if (error) throw error;
    return data;
  };

  const logout = useCallback(async () => {
    await supabase.auth.signOut();
    setSession(null);
    setUser(null);
  }, []);

  const refreshUser = async () => {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session?.access_token) return;

      // Call backend API to get fresh user data (bypasses RLS)
      const response = await axios.get(`${API}/auth/me`, {
        headers: { Authorization: `Bearer ${session.access_token}` }
      });

      if (response.data) {
        console.log('User data refreshed:', response.data);
        setUser(response.data);
      }
    } catch (error) {
      console.error('Failed to refresh user:', error);
    }
  };

  const getToken = async () => {
    const { data: { session } } = await supabase.auth.getSession();
    return session?.access_token || null;
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        session,
        token: session?.access_token,
        loading,
        register,
        login,
        loginWithGoogle,
        logout,
        refreshUser,
        getToken,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};