import React, { useEffect, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { CheckCircle, Home } from 'lucide-react';
import { Button } from '../components/ui/button';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PaymentSuccessPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { refreshUser } = useAuth();
  const [loading, setLoading] = React.useState(true);
  const [credits, setCredits] = React.useState(0);
  const [plan, setPlan] = React.useState('');

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

      const response = await axios.post(`${API}/payment/success`, null, {
        params: params
      });

      setCredits(response.data.credits_added);
      setPlan(response.data.plan);

      if (refreshUser) {
        await refreshUser();
      }
    } catch (error) {
      console.error('Error processing payment:', error);
    } finally {
      setLoading(false);
    }
  }, [refreshUser]);

  useEffect(() => {
    const plan = searchParams.get('plan');
    const userId = searchParams.get('user_id');
    const sessionId = searchParams.get('session_id');

    if (plan && userId) {
      handlePaymentSuccess(plan, userId, sessionId);
    }
  }, [searchParams, handlePaymentSuccess]);

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
            {plan === 'lifetime' ? 'Lifetime Access' : 'Pro Monthly'}
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