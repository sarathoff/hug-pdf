import React, { useEffect, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { CheckCircle, Home, Loader2, XCircle } from 'lucide-react';
import { Button } from '../components/ui/button';
import { useAuth } from '../context/AuthContext';
import { supabase } from '../lib/supabaseClient';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PaymentSuccessPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { refreshUser, token } = useAuth();
  const [loading, setLoading] = React.useState(true);
  const [credits, setCredits] = React.useState(0);
  const [plan, setPlan] = React.useState('');
  const [error, setError] = React.useState(null);

  // Prevent duplicate payment processing
  const processedRef = React.useRef(false);

  const handlePaymentSuccess = useCallback(async (planId, userId, sessionId, paymentId, explicitToken = null) => {
    console.log('=== handlePaymentSuccess called ===');
    console.log('Plan:', planId, 'User:', userId, 'Session:', sessionId, 'Payment:', paymentId);

    // Use explicit token if provided (from fallback logic), otherwise use context token
    const useToken = explicitToken || token;
    console.log('Token available for request:', !!useToken);

    try {
      const params = {
        plan: planId,
        user_id: userId
      };

      // Include session_id if available for idempotency
      if (sessionId) {
        params.session_id = sessionId;
      }

      // Include payment_id if available (for one-time payments)
      if (paymentId) {
        params.payment_id = paymentId;
      }

      console.log('Processing payment with params:', params);

      // Make request with or without token
      const headers = {};
      if (useToken) {
        headers['Authorization'] = `Bearer ${useToken}`;
      } else {
        console.warn('Sending request WITHOUT Authorization header (relying on Session ID verification)');
      }

      const response = await axios.post(`${API}/payment/success`, null, {
        params: params,
        headers: headers
      });

      console.log('Payment success response:', response.data);

      setCredits(response.data.credits_added);
      setPlan(response.data.data.plan);

      // Only force refresh if we actually have a session to refresh
      if (refreshUser && useToken) {
        console.log('Refreshing user data...');
        await refreshUser();
        console.log('User data refreshed successfully');
      } else {
        console.log('Skipping user refresh (no active session)');
      }
    } catch (error) {
      console.error('=== Error processing payment ===');
      console.error('Error details:', error);

      const errorMessage = error.response?.data?.detail || error.message || 'Unknown error occurred';

      // Set error state instead of alerting
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [refreshUser, token]);

  useEffect(() => {
    // Prevent multiple executions - only process once per page load
    if (processedRef.current) {
      return;
    }

    const plan = searchParams.get('plan');
    const userId = searchParams.get('user_id');
    const sessionId = searchParams.get('session_id');
    const paymentId = searchParams.get('payment_id');

    if (plan && userId) {
      processedRef.current = true;

      // Wait for token to be available (user might be redirected from payment before auth is ready)
      const processPayment = async () => {
        let activeToken = token;

        // If no token yet, wait a bit for auth to initialize
        if (!activeToken) {
          console.log('Token not available yet, waiting for authentication...');
          // Wait up to 2 seconds for token to be available
          for (let i = 0; i < 4; i++) {
            console.log(`Checking for token... attempt ${i + 1}/4`);
            await new Promise(resolve => setTimeout(resolve, 500));
            const { data: { session } } = await supabase.auth.getSession();
            console.log('Session check result:', session ? 'Session exists' : 'No session');
            if (session?.access_token) {
              console.log('Token now available, processing payment...');
              activeToken = session.access_token;
              break;
            }
          }
        }

        // If still no token but we have a session ID or payment ID, try verifying without auth (Backend supports this now)
        if (!activeToken && (sessionId || paymentId)) {
          console.warn('No authentication token found after waiting. Falling back to Session verification.');
          // Proceed without token - backend will verify using Dodo API and session_id/payment_id
        } else if (!activeToken) {
          // No token and no session ID or payment ID (shouldn't happen here)
          console.error('No authentication token found and no session/payment ID. Cannot verify.');
          setLoading(false);
          alert('Please log in to complete your payment verification.');
          return;
        } else {
          console.log('Token available, processing payment normally...');
        }

        // Token is available or falling back to session verification
        handlePaymentSuccess(plan, userId, sessionId, paymentId, activeToken);
      };

      processPayment();
    }
  }, [searchParams, handlePaymentSuccess, token]);



  // ... useEffect hooks ...

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white flex items-center justify-center p-4">
        <div className="text-center bg-white p-8 rounded-2xl shadow-xl border border-gray-100 max-w-sm w-full">
          <Loader2 className="h-12 w-12 text-blue-600 animate-spin mx-auto mb-4" />
          <h2 className="text-xl font-bold text-gray-900 mb-2">Verifying Payment</h2>
          <p className="text-gray-600">Please wait while we confirm your transaction. This may take a moment...</p>
        </div>
      </div>
    );
  }

  // FAIL STATE UI
  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white flex items-center justify-center px-6">
        <div className="max-w-md w-full text-center">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-red-100 rounded-full mb-6">
            <XCircle className="w-12 h-12 text-red-600" />
          </div>

          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            Payment Failed
          </h1>
          <p className="text-lg text-gray-600 mb-8">
            We couldn't verify your payment.
          </p>

          <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-8 text-left">
            <p className="text-sm text-red-800 font-medium">Error details:</p>
            <p className="text-sm text-red-600 mt-1">{error}</p>
          </div>

          <div className="space-y-3">
            <Button
              onClick={() => navigate('/pricing')}
              className="w-full bg-gray-900 hover:bg-gray-800 text-white py-3 rounded-xl font-medium"
            >
              Try Again
            </Button>
            <Button
              variant="ghost"
              onClick={() => navigate('/')}
              className="w-full"
            >
              Go to Homepage
            </Button>
          </div>
        </div>
      </div>
    );
  }

  // SUCCESS STATE UI (Default)
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white flex items-center justify-center px-6">
      <div className="max-w-md w-full text-center">
        {/* Success Icon */}
        <div className="inline-flex items-center justify-center w-20 h-20 bg-green-100 rounded-full mb-6">
          <CheckCircle className="w-12 h-12 text-green-600" />
        </div>

        {/* Success Message */}
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Payment Successful!
        </h1>
        <p className="text-lg text-gray-600 mb-8">
          Your account has been credited with <span className="font-bold text-blue-600">{credits || 0} credits</span>.
        </p>

        {/* Plan Info */}
        <div className="bg-white rounded-2xl shadow-lg p-6 mb-8">
          <p className="text-sm text-gray-500 mb-2">Active Plan</p>
          <p className="text-2xl font-bold text-gray-900">
            {plan === 'pro' ? 'Pro Plan' : 'Free Plan'}
          </p>
        </div>

        {/* Actions */}
        <div className="space-y-3">
          <Button
            onClick={() => navigate('/')}
            className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white py-3 rounded-xl font-medium"
          >
            Start Creating PDFs
          </Button>
          <Button
            variant="ghost"
            onClick={() => navigate('/')}
            className="w-full flex items-center justify-center gap-2"
          >
            <Home className="w-4 h-4" />
            Go to Homepage
          </Button>
        </div>
      </div>
    </div>
  );
};

export default PaymentSuccessPage;