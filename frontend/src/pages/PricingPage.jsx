import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { Separator } from '../components/ui/separator';
import { Check, Zap, ArrowRight, Shield, Loader2, Crown, Star } from 'lucide-react';
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
          id: 'credit_topup',
          name: 'Credit Top-Up',
          price: 20,
          billing: 'one-time',
          credits: 100,
          popular: true,
          features: ['100 Credits added instantly', 'Generate up to 100 PDFs', 'Research & E-book modes unlocked', 'Credits never expire', 'One-time payment — no subscription']
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
    <div className="min-h-screen bg-slate-50">
      {/* Page header */}
      <div className="bg-white border-b border-slate-100 py-16 px-4">
        <div className="max-w-3xl mx-auto text-center space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-violet-50 border border-violet-200 rounded-full text-xs font-semibold text-violet-700 uppercase tracking-wider">
            <Star className="w-3.5 h-3.5" />
            Simple pricing
          </div>
          <h1 className="text-4xl sm:text-5xl font-bold tracking-tight text-slate-900">
            Simple, Transparent Pricing
          </h1>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto">
            Perfect for research paper writers, resume creators, and digital marketers creating professional e-books.
          </p>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-16">
        {/* Free tier highlight */}
        <div className="mb-10 p-6 bg-emerald-50 border border-emerald-200 rounded-2xl max-w-2xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-emerald-100 text-emerald-700 rounded-full text-sm font-medium mb-3">
            <Zap className="w-4 h-4" />
            Free Forever
          </div>
          <h3 className="text-xl font-bold text-slate-900 mb-2">Start with 3 free credits</h3>
          <p className="text-slate-600 text-sm">No credit card required. Sign up and get 3 PDFs to try all features.</p>
          {!user && (
            <Button
              onClick={() => navigate('/auth')}
              className="mt-4 h-10 px-6 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold rounded-lg shadow-sm"
            >
              Get started free
              <ArrowRight className="ml-2 w-4 h-4" />
            </Button>
          )}
        </div>

        {/* Paid Plans */}
        <div className="grid grid-cols-1 gap-6 max-w-2xl mx-auto">
          {plans.map((plan) => (
            <div
              key={plan.id}
              className={`relative bg-white rounded-2xl border-2 transition-all duration-300 ${plan.popular
                ? 'border-violet-500 shadow-xl shadow-violet-500/10'
                : 'border-slate-200 hover:border-slate-300 shadow-sm hover:shadow-md'
                }`}
            >
              {plan.popular && (
                <div className="absolute -top-3.5 left-1/2 -translate-x-1/2">
                  <div className="inline-flex items-center gap-1.5 px-4 py-1 bg-violet-600 text-white text-xs font-bold rounded-full shadow-lg">
                    <Crown className="w-3.5 h-3.5" />
                    Most Popular
                  </div>
                </div>
              )}

              <div className="p-7">
                {/* Plan header */}
                <div className="flex items-start justify-between mb-6">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <div className={`p-2 rounded-lg ${plan.popular ? 'bg-violet-100' : 'bg-slate-100'}`}>
                        <Zap className={`w-4 h-4 ${plan.popular ? 'text-violet-600' : 'text-slate-500'}`} />
                      </div>
                      <h3 className="text-xl font-bold text-slate-900">{plan.name}</h3>
                    </div>
                    <p className="text-sm text-slate-500 mt-1">
                      {plan.description || "Perfect for researchers, creators, and marketers"}
                    </p>
                  </div>
                  <span className="inline-flex items-center px-2.5 py-1 bg-slate-100 text-slate-600 text-xs font-medium rounded-full uppercase tracking-wide">
                    {plan.billing}
                  </span>
                </div>

                {/* Price */}
                <div className="flex items-baseline gap-1.5 mb-6">
                  <span className="text-5xl font-bold text-slate-900">${plan.price}</span>
                  <span className="text-slate-400 font-medium text-sm">
                    / {plan.billing === 'monthly' ? 'month' : 'one-time'}
                  </span>
                </div>

                <Separator className="mb-6" />

                {/* Features */}
                <ul className="space-y-3 mb-7">
                  {plan.features.map((feature, index) => (
                    <li key={index} className="flex items-start gap-3 text-sm text-slate-600">
                      <div className="mt-0.5 rounded-full bg-emerald-100 p-0.5 shrink-0">
                        <Check className="w-3.5 h-3.5 text-emerald-600" />
                      </div>
                      {feature}
                    </li>
                  ))}
                </ul>

                {/* CTA */}
                <Button
                  onClick={() => handlePurchase(plan.id)}
                  disabled={loading || (user && user.plan === plan.id)}
                  className={`w-full h-12 text-base font-semibold rounded-xl transition-all ${plan.popular
                    ? 'bg-violet-600 hover:bg-violet-700 text-white shadow-lg shadow-violet-500/20'
                    : 'bg-slate-900 hover:bg-slate-800 text-white'
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
              </div>
            </div>
          ))}
        </div>

        {/* Trust badge */}
        <div className="mt-10 text-center">
          <div className="inline-flex items-center gap-2 text-slate-500 bg-white border border-slate-200 px-4 py-2.5 rounded-full text-sm shadow-sm">
            <Shield className="w-4 h-4 text-slate-400" />
            <span>Secure payments powered by Dodo Payments</span>
          </div>
        </div>

        {/* FAQ or value props */}
        <div className="mt-16 grid sm:grid-cols-3 gap-6 text-center">
          {[
            { title: 'No subscription', desc: 'Pay once, use forever. Credits never expire.' },
            { title: 'Instant access', desc: 'Credits are added to your account immediately after payment.' },
            { title: 'Cancel anytime', desc: 'No commitment, no hidden fees. Simple as that.' },
          ].map((item, i) => (
            <div key={i} className="p-5 bg-white rounded-xl border border-slate-200 shadow-sm">
              <h4 className="font-semibold text-slate-900 mb-1.5">{item.title}</h4>
              <p className="text-sm text-slate-500">{item.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default PricingPage;
