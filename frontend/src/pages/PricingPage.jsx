import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Separator } from '../components/ui/separator';
import { Check, Crown, Zap, ArrowRight, Shield, Loader2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

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
      // Fallback plans
      setPlans([
        {
          id: 'pro',
          name: 'Pro Hug Plan',
          price: 19,
          billing: 'monthly',
          credits: 100,
          features: ["Unlimited PDF generations", "Priority AI processing", "Advanced templates", "Remove watermark", "Commercial license"]
        },
        {
          id: 'lifetime',
          name: 'Lifetime Hug',
          price: 49,
          billing: 'one-time',
          credits: 500,
          popular: true,
          features: ["Everything in Pro", "Lifetime updates", "Priority support", "Early access to new features", "No recurring fees"]
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

  return (
    <div className="relative w-full h-full">
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 py-16 sm:py-24">
        <div className="text-center mb-16 space-y-4">
          <h2 className="text-4xl sm:text-5xl font-bold tracking-tight text-gray-900">
            Simple, Transparent
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600 ml-2">
              Pricing
            </span>
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Choose the perfect plan for your needs. Always know what you'll pay.
          </p>
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-50 text-blue-700 rounded-full text-sm font-medium border border-blue-100 cursor-default">
            <Zap className="w-4 h-4" />
            New users get 3 free credits to start!
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl mx-auto">
          {plans.map((plan) => (
            <Card
              key={plan.id}
              className={`relative border-2 transition-all duration-300 hover:shadow-xl ${plan.popular
                  ? 'border-purple-500 shadow-purple-100 scale-105 z-10'
                  : 'border-gray-100 hover:border-gray-200'
                }`}
            >
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <Badge className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 px-4 py-1 text-sm shadow-lg border-0">
                    Most Popular
                  </Badge>
                </div>
              )}

              <CardHeader>
                <div className="flex justify-between items-start mb-4">
                  <div className={`p-3 rounded-2xl ${plan.popular ? 'bg-purple-50 text-purple-600' : 'bg-gray-100 text-gray-600'
                    }`}>
                    {plan.id === 'lifetime' ? <Crown className="w-6 h-6" /> : <Zap className="w-6 h-6" />}
                  </div>
                  <Badge variant="outline" className="uppercase text-xs tracking-wider">
                    {plan.billing === 'one-time' ? 'One-time payment' : 'Monthly billing'}
                  </Badge>
                </div>
                <CardTitle className="text-2xl font-bold">{plan.name}</CardTitle>
                <CardDescription>Perfect for {plan.id === 'lifetime' ? 'power users' : 'professionals'}</CardDescription>
              </CardHeader>

              <CardContent className="space-y-6">
                <div className="flex items-baseline gap-1">
                  <span className="text-5xl font-bold text-gray-900">${plan.price}</span>
                  <span className="text-gray-500 font-medium">/{plan.billing === 'one-time' ? 'life' : 'mo'}</span>
                </div>

                <Separator />

                <ul className="space-y-3">
                  {plan.features.map((feature, index) => (
                    <li key={index} className="flex items-start gap-3 text-sm text-gray-600">
                      <div className="mt-0.5 rounded-full bg-green-100 p-0.5">
                        <Check className="w-3.5 h-3.5 text-green-600" />
                      </div>
                      {feature}
                    </li>
                  ))}
                </ul>
              </CardContent>

              <CardFooter>
                <Button
                  onClick={() => handlePurchase(plan.id)}
                  disabled={loading || (user && user.plan === plan.id)}
                  className={`w-full h-12 text-base font-medium shadow-lg transition-all ${plan.popular
                      ? 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white'
                      : 'bg-gray-900 hover:bg-gray-800 text-white'
                    }`}
                >
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Processing...
                    </>
                  ) : (user && user.plan === plan.id) ? (
                    'Current Plan'
                  ) : (
                    <>
                      Get Started
                      <ArrowRight className="ml-2 h-4 w-4" />
                    </>
                  )}
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>

        <div className="mt-16 text-center">
          <div className="inline-flex items-center gap-2 text-gray-500 bg-gray-50 px-4 py-2 rounded-full text-sm">
            <Shield className="w-4 h-4" />
            <span>Secure payments powered by Dodo Payments</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PricingPage;
