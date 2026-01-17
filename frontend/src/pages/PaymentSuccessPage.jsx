import React, { useEffect, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { CheckCircle, Home } from 'lucide-react';
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

  // Prevent duplicate payment processing
  const processedRef = React.useRef(false);

  const handlePaymentSuccess = useCallback(async (planId, userId, sessionId) => {
    try {
      const params = {
        plan: planId,
        user_id: userId
      };

      // Include session_id if available for idempotency
      if (sessionId) {
        params.session_id = sessionId;
      }

      console.log('Processing payment with params:', params);

      const response = await axios.post(`${API}/payment/success`, null, {
        params: params,
        headers: token ? { Authorization: `Bearer ${token}` } : {}
      });

      console.log('Payment success response:', response.data);

      setCredits(response.data.credits_added);
      setPlan(response.data.plan);

      if (refreshUser) {
        await refreshUser();
      }
    } catch (error) {
      console.error('Error processing payment:', error);

      // Extract detailed error message from backend
      const errorMessage = error.response?.data?.detail || error.message || 'Unknown error occurred';

      alert(`Payment verification failed: ${errorMessage}\n\nPlease contact support if you were charged. Include this session ID: ${sessionId || 'N/A'}`);
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

    if (plan && userId) {
      processedRef.current = true;

      // Wait for token to be available (user might be redirected from payment before auth is ready)
      const processPayment = async () => {
        // If no token yet, wait a bit for auth to initialize
        if (!token) {
          console.log('Token not available yet, waiting for authentication...');
          // Wait up to 3 seconds for token to be available
          for (let i = 0; i < 6; i++) {
            await new Promise(resolve => setTimeout(resolve, 500));
            // Check if token is now available (need to get it from auth context)
            const { data: { session } } = await supabase.auth.getSession();
            if (session?.access_token) {
              console.log('Token now available, processing payment...');
              handlePaymentSuccess(plan, userId, sessionId);
              return;
            }
          }
          // If still no token after 3 seconds, try anyway (might work if user is already logged in)
          console.log('Proceeding without token check...');
        }
        handlePaymentSuccess(plan, userId, sessionId);
      };

      processPayment();
    }
  }, [searchParams, handlePaymentSuccess, token]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Processing your payment...</p>
        </div>
      </div>
    );
  }

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
          Your account has been credited with <span className="font-bold text-blue-600">{credits} credits</span>.
        </p>

        {/* Plan Info */}
        <div className="bg-white rounded-2xl shadow-lg p-6 mb-8">
          <p className="text-sm text-gray-500 mb-2">Active Plan</p>
          <p className="text-2xl font-bold text-gray-900">
            Pro Plan
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