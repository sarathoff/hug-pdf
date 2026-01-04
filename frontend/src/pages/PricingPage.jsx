import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Check, Crown, Zap, ArrowRight, Home } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PricingPage = () => {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(false);
  const { user, token } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchPricing();
  }, []);

  const fetchPricing = async () => {
    try {
      const response = await axios.get(`${API}/pricing`);
      setPlans(response.data.plans);
    } catch (error) {
      console.error('Error fetching pricing:', error);
      // Fallback plans if API fails
      setPlans([
        {
          id: 'pro',
          name: 'Pro Hug Plan',
          price: 19,
          billing: 'monthly',
          credits: 100,
          features: ["Unlimited PDF generations", "Priority AI processing", "Advanced templates", "Remove watermark"]
        },
        {
          id: 'lifetime',
          name: 'Lifetime Hug',
          price: 49,
          billing: 'one-time',
          credits: 500,
          popular: true,
          features: ["Everything in Pro", "Lifetime updates", "Priority support", "Early access"]
        }
      ]);
    }
  };

  const handlePurchase = async (planId) => {
    if (!user) {
      navigate('/auth');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(
        `${API}/payment/create-checkout`,
        { plan: planId },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (response.data.checkout_url) {
        window.location.href = response.data.checkout_url;
      }
    } catch (error) {
      console.error('Error creating checkout:', error);
      alert('Error processing payment. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getPlanIcon = (planId) => {
    return planId === 'lifetime' ? <Crown className="w-8 h-8" /> : <Zap className="w-8 h-8" />;
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <h1 className="text-xl font-semibold text-gray-800">Pricing</h1>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate('/')}
            className="flex items-center gap-2"
          >
            <Home className="w-4 h-4" />
            Home
          </Button>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-16">
        <div className="text-center mb-16">
          <h2 className="text-5xl font-bold mb-6 tracking-tight">
            Simple, Transparent
            <span className="block mt-2 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Pricing
            </span>
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Choose the plan that fits your needs. No hidden fees.
          </p>
          <p className="text-lg text-blue-600 font-medium mt-4">
            New users get 3 free credits to try!
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          {plans.map((plan) => (
            <div
              key={plan.id}
              className={`relative bg-white rounded-2xl shadow-lg p-8 border-2 ${plan.popular
                  ? 'border-purple-500 shadow-purple-200'
                  : 'border-gray-200'
                }`}
            >
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <span className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-4 py-1 rounded-full text-sm font-medium">
                    Most Popular
                  </span>
                </div>
              )}

              <div className={`inline-flex items-center justify-center w-16 h-16 rounded-2xl mb-6 ${plan.popular
                  ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white'
                  : 'bg-gray-100 text-gray-700'
                }`}>
                {getPlanIcon(plan.id)}
              </div>

              <h3 className="text-2xl font-bold text-gray-900 mb-2">{plan.name}</h3>

              <div className="mb-6">
                <span className="text-5xl font-bold text-gray-900">${plan.price}</span>
                {plan.billing === 'monthly' && (
                  <span className="text-gray-600 ml-2">/ month</span>
                )}
                {plan.billing === 'one-time' && (
                  <span className="text-gray-600 ml-2">one-time</span>
                )}
              </div>

              <ul className="space-y-3 mb-8">
                {plan.features.map((feature, index) => (
                  <li key={index} className="flex items-start gap-3">
                    <Check className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-700">{feature}</span>
                  </li>
                ))}
              </ul>

              <Button
                onClick={() => handlePurchase(plan.id)}
                disabled={loading || (user && user.plan === plan.id)}
                className={`w-full py-4 rounded-xl font-medium flex items-center justify-center gap-2 ${plan.popular
                    ? 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white'
                    : 'bg-gray-900 hover:bg-gray-800 text-white'
                  }`}
              >
                {user && user.plan === plan.id ? (
                  'Current Plan'
                ) : (
                  <>
                    {loading ? 'Processing...' : 'Purchase Now'}
                    <ArrowRight className="w-5 h-5" />
                  </>
                )}
              </Button>
            </div>
          ))}
        </div>

        <div className="mt-16 text-center space-y-4">
          <p className="text-gray-600 text-lg">
            Have questions? <button onClick={() => navigate('/contact')} className="text-blue-600 hover:text-blue-700 font-medium">Contact us</button>
          </p>
          <p className="text-sm text-gray-500">
            Secure payments powered by Dodo Payments
          </p>
        </div>
      </div>
    </div>
  );
};

export default PricingPage;
