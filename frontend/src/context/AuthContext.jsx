import React, { createContext, useState, useContext, useEffect, useCallback, useRef } from 'react';
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
  const [initialized, setInitialized] = useState(false);
  const authStateListenerRef = useRef(null);
  const tokenRefreshTimeoutRef = useRef(null);

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
    if (!supabaseUser) return null;

    try {
      // Check if user exists in our users table
      const { data: existingUser, error: selectError } = await supabase
        .from('users')
        .select('*')
        .eq('user_id', supabaseUser.id)
        .maybeSingle();

      if (selectError) {
        console.error('Error fetching user:', selectError);
        throw selectError;
      }

      if (!existingUser) {
        console.log('User not found in DB, creating new user record...');
        // Create new user with 3 free credits
        const { error: insertError } = await supabase
          .from('users')
          .insert({
            user_id: supabaseUser.id,
            email: supabaseUser.email,
            credits: 3,
            plan: 'free',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          });

        if (insertError) {
          console.error('Error creating user:', insertError);
          throw insertError;
        }

        console.log('New user created successfully');
        return {
          user_id: supabaseUser.id,
          email: supabaseUser.email,
          credits: 3,
          plan: 'free',
          early_adopter: false,
        };
      }

      console.log('User found in DB:', existingUser.email);
      return existingUser;
    } catch (error) {
      console.error('Error syncing user to backend:', error);
      // Fallback: Return basic user info to prevent logout on temporary DB issues
      return {
        user_id: supabaseUser.id,
        email: supabaseUser.email,
        credits: 0,
        plan: 'free',
        error: true
      };
    }
  }, []);

  // Initialize session on mount
  useEffect(() => {
    let isMounted = true;

    const initializeAuth = async () => {
      try {
        console.log('🔐 Initializing authentication...');

        // CRITICAL: Check for OAuth callback in URL hash
        // Google OAuth redirects with: #access_token=...&refresh_token=...
        const hash = window.location.hash;
        if (hash && hash.includes('access_token')) {
          console.log('🔗 OAuth callback detected in URL, processing...');
          // Supabase will automatically detect and process this
          // Give it a moment to process
          await new Promise(resolve => setTimeout(resolve, 500));
          // Clean up URL
          window.history.replaceState(null, '', window.location.pathname);
        }

        // Get session from localStorage (Supabase handles this automatically)
        const { data: { session }, error } = await supabase.auth.getSession();

        if (error) {
          console.error('Error getting session:', error);
          // Don't throw - just continue without session
        }

        if (isMounted) {
          if (session?.user) {
            console.log('✅ Session found, syncing user data...');
            setSession(session);
            // Optimistic update to prevent "flicker" of logged out state
            setUser({
              user_id: session.user.id,
              email: session.user.email,
              credits: 0, // Will update shortly
              plan: 'free',
              loading: true
            });
            
            const userData = await syncUserToBackend(session.user);
            if (isMounted && userData) {
              setUser(userData);
            }
          } else {
            console.log('ℹ️ No existing session found');
          }
          setInitialized(true);
          setLoading(false);
        }
      } catch (error) {
        console.error('Error initializing auth:', error);
        if (isMounted) {
          setInitialized(true);
          setLoading(false);
        }
      }
    };

    initializeAuth();

    return () => {
      isMounted = false;
    };
  }, [syncUserToBackend]);

  // Listen for auth state changes (login, logout, token refresh)
  useEffect(() => {
    if (!initialized) return;

    console.log('🔐 Setting up auth state listener...');

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (event, newSession) => {
      console.log('🔐 Auth state change event:', event);

      // Handle different auth events
      switch (event) {
        case 'SIGNED_IN':
          console.log('✅ User signed in:', newSession?.user?.email);
          setSession(newSession);
          if (newSession?.user) {
            const userData = await syncUserToBackend(newSession.user);
            setUser(userData);
          }
          break;

        case 'SIGNED_OUT':
          // Only handle sign out if we're fully initialized
          // This prevents spurious sign-outs during page load
          if (initialized) {
            console.log('👋 User signed out');
            setSession(null);
            setUser(null);
          }
          break;

        case 'TOKEN_REFRESHED':
          console.log('🔄 Token refreshed successfully');
          setSession(newSession);
          break;

        case 'USER_UPDATED':
          console.log('👤 User updated');
          setSession(newSession);
          if (newSession?.user) {
            const userData = await syncUserToBackend(newSession.user);
            setUser(userData);
          }
          break;

        default:
          // For other events, just update session if it exists
          if (newSession) {
            setSession(newSession);
          }
      }
    });

    authStateListenerRef.current = subscription;

    return () => {
      console.log('🔐 Cleaning up auth state listener');
      subscription.unsubscribe();
    };
  }, [initialized, syncUserToBackend]);

  // Automatic token refresh with improved error handling
  useEffect(() => {
    if (!session?.expires_at) return;

    // Clear any existing timeout
    if (tokenRefreshTimeoutRef.current) {
      clearTimeout(tokenRefreshTimeoutRef.current);
    }

    const expiresAt = session.expires_at; // Unix timestamp in seconds
    const now = Math.floor(Date.now() / 1000);
    const expiresIn = expiresAt - now;

    // Refresh 5 minutes before expiration
    const refreshIn = Math.max(0, (expiresIn - 300) * 1000);

    console.log(`⏰ Token expires in ${expiresIn} seconds. Scheduling refresh in ${refreshIn / 1000} seconds.`);

    tokenRefreshTimeoutRef.current = setTimeout(async () => {
      console.log('🔄 Attempting token refresh...');
      try {
        const { data, error } = await supabase.auth.refreshSession();

        if (error) {
          console.error('❌ Token refresh failed:', error);

          // Only logout on critical authentication errors
          const criticalErrors = ['invalid_grant', 'invalid_token', 'refresh_token_not_found'];
          const isCriticalError = criticalErrors.some(err =>
            error.message?.toLowerCase().includes(err) ||
            error.status === 401
          );

          if (isCriticalError) {
            console.warn('⚠️ Critical auth error detected, logging out user');
            await supabase.auth.signOut();
          } else {
            console.warn('⚠️ Token refresh failed but keeping user logged in (likely network issue)');
            // Session will be retried on next scheduled refresh or API call
          }
        } else if (data?.session) {
          console.log('✅ Token refreshed successfully');
          setSession(data.session);
        }
      } catch (err) {
        console.error('❌ Token refresh error:', err);
        // Don't logout on network errors - keep user logged in
        console.warn('⚠️ Keeping user logged in despite refresh error');
      }
    }, refreshIn);

    return () => {
      if (tokenRefreshTimeoutRef.current) {
        clearTimeout(tokenRefreshTimeoutRef.current);
      }
    };
  }, [session?.expires_at]);

  // Validate session on page visibility change (user returns to tab)
  useEffect(() => {
    const handleVisibilityChange = async () => {
      if (document.visibilityState === 'visible' && session) {
        console.log('👁️ Page visible, validating session...');
        try {
          const { data: { session: currentSession }, error } = await supabase.auth.getSession();

          if (error) {
            console.error('Error validating session:', error);
            return;
          }

          if (!currentSession && session) {
            // Session was lost while tab was hidden
            console.warn('⚠️ Session lost while tab was hidden');
            setSession(null);
            setUser(null);
          } else if (currentSession && !session) {
            // Session was restored
            console.log('✅ Session restored');
            setSession(currentSession);
            if (currentSession.user) {
              const userData = await syncUserToBackend(currentSession.user);
              setUser(userData);
            }
          }
        } catch (err) {
          console.error('Error in visibility change handler:', err);
        }
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, [session, syncUserToBackend]);

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
    console.log('👋 Logging out user...');
    try {
      await supabase.auth.signOut();
      setSession(null);
      setUser(null);
      console.log('✅ Logout successful');
    } catch (error) {
      console.error('Error during logout:', error);
      // Force local logout even if API call fails
      setSession(null);
      setUser(null);
    }
  }, []);

  const refreshUser = async () => {
    try {
      const { data: { session: currentSession } } = await supabase.auth.getSession();
      if (!currentSession?.access_token) {
        console.warn('No session available for user refresh');
        return;
      }

      // Call backend API to get fresh user data
      const response = await axios.get(`${API}/auth/me`, {
        headers: { Authorization: `Bearer ${currentSession.access_token}` }
      });

      if (response.data) {
        console.log('✅ User data refreshed:', response.data);
        setUser(response.data);
      }
    } catch (error) {
      console.error('Failed to refresh user:', error);
      // Don't logout on refresh failure - just log the error
    }
  };

  const getToken = async () => {
    try {
      const { data: { session: currentSession } } = await supabase.auth.getSession();
      return currentSession?.access_token || null;
    } catch (error) {
      console.error('Error getting token:', error);
      return null;
    }
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