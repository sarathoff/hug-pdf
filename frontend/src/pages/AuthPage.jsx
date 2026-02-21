import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Loader2, Mail, Lock, AlertCircle, FileText, Sparkles, ArrowRight, CheckCircle2 } from 'lucide-react';

const AuthPage = () => {
    const [isLogin, setIsLogin] = useState(true);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [googleLoading, setGoogleLoading] = useState(false);
    const { login, register, loginWithGoogle } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            if (isLogin) {
                await login(email, password);
                navigate('/');
            } else {
                await register(email, password);
                setError('Please check your email to verify your account, then login.');
                setIsLogin(true);
            }
        } catch (err) {
            setError(err.message || err.response?.data?.detail || 'An error occurred');
        } finally {
            setLoading(false);
        }
    };

    const handleGoogleSignIn = async () => {
        setError('');
        setGoogleLoading(true);
        try {
            await loginWithGoogle();
        } catch (err) {
            setError(err.message || 'Failed to sign in with Google');
            setGoogleLoading(false);
        }
    };

    const perks = [
        '3 free PDF credits on sign-up',
        'Gemini AI-powered generation',
        'Professional LaTeX quality',
        'No design skills required',
    ];

    return (
        <div className="min-h-screen flex">
            {/* Left Panel — Dark branding panel (hidden on mobile) */}
            <div className="hidden lg:flex lg:w-[45%] xl:w-[40%] flex-col bg-slate-900 relative overflow-hidden">
                {/* Background decorations */}
                <div className="absolute top-0 right-0 w-80 h-80 bg-violet-600/20 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 pointer-events-none" />
                <div className="absolute bottom-0 left-0 w-64 h-64 bg-blue-600/15 rounded-full blur-3xl translate-y-1/2 -translate-x-1/2 pointer-events-none" />

                <div className="relative z-10 flex flex-col h-full p-10 xl:p-12">
                    {/* Logo */}
                    <Link to="/" className="flex items-center gap-2.5 mb-auto">
                        <img src="/logo.png" alt="HugPDF" className="h-8 w-8 object-contain" />
                        <span className="font-bold text-white text-lg">HugPDF</span>
                    </Link>

                    {/* Main content */}
                    <div className="my-auto space-y-8">
                        <div className="space-y-3">
                            <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-violet-500/20 border border-violet-500/30 rounded-full text-violet-300 text-xs font-medium">
                                <Sparkles className="w-3.5 h-3.5" />
                                AI Document Generator
                            </div>
                            <h2 className="text-3xl xl:text-4xl font-bold text-white leading-tight">
                                Professional PDFs from simple prompts.
                            </h2>
                            <p className="text-slate-400 leading-relaxed">
                                Join thousands of students, researchers, and professionals creating stunning documents in seconds.
                            </p>
                        </div>

                        {/* Perks list */}
                        <ul className="space-y-3">
                            {perks.map((perk, i) => (
                                <li key={i} className="flex items-center gap-3">
                                    <div className="p-0.5 rounded-full bg-violet-500/30 shrink-0">
                                        <CheckCircle2 className="w-4 h-4 text-violet-400" />
                                    </div>
                                    <span className="text-slate-300 text-sm">{perk}</span>
                                </li>
                            ))}
                        </ul>

                        {/* Testimonial quote */}
                        <div className="p-5 bg-white/5 border border-white/10 rounded-xl">
                            <p className="text-slate-300 text-sm leading-relaxed italic mb-3">
                                "HugPDF saved me hours every week. My research papers now look completely professional without touching LaTeX directly."
                            </p>
                            <div className="flex items-center gap-2">
                                <div className="w-8 h-8 rounded-full bg-violet-500/30 flex items-center justify-center text-violet-300 text-xs font-bold">
                                    AK
                                </div>
                                <div>
                                    <p className="text-white text-xs font-semibold">Aditya K.</p>
                                    <p className="text-slate-500 text-xs">PhD Student, IIT Delhi</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Bottom text */}
                    <p className="text-slate-600 text-xs mt-auto pt-8">
                        &copy; 2026 HugPDF Contributors. MIT Licensed.
                    </p>
                </div>
            </div>

            {/* Right Panel — Auth form */}
            <div className="flex-1 flex flex-col items-center justify-center bg-white px-4 sm:px-8 py-12">
                {/* Mobile logo */}
                <div className="lg:hidden mb-8">
                    <Link to="/" className="flex items-center gap-2.5">
                        <img src="/logo.png" alt="HugPDF" className="h-8 w-8 object-contain" />
                        <span className="font-bold text-slate-900 text-lg">HugPDF</span>
                    </Link>
                </div>

                <div className="w-full max-w-sm">
                    {/* Heading */}
                    <div className="mb-8 space-y-1">
                        <h1 className="text-2xl font-bold text-slate-900">
                            {isLogin ? 'Welcome back' : 'Create your account'}
                        </h1>
                        <p className="text-sm text-slate-500">
                            {isLogin
                                ? 'Sign in to your HugPDF account to continue.'
                                : 'Get 3 free credits. No card required.'}
                        </p>
                    </div>

                    {/* Google OAuth */}
                    <Button
                        variant="outline"
                        className="w-full h-11 border-slate-200 bg-white hover:bg-slate-50 text-slate-700 font-medium rounded-xl mb-5 shadow-sm"
                        onClick={handleGoogleSignIn}
                        disabled={loading || googleLoading}
                    >
                        {googleLoading ? (
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        ) : (
                            <svg className="mr-2 h-4 w-4" aria-hidden="true" focusable="false" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 488 512">
                                <path fill="currentColor" d="M488 261.8C488 403.3 391.1 504 248 504 110.8 504 0 393.2 0 256S110.8 8 248 8c66.8 0 123 24.5 166.3 64.9l-67.5 64.9C258.5 52.6 94.3 116.6 94.3 256c0 86.5 69.1 156.6 153.7 156.6 98.2 0 135-70.4 140.8-106.9H248v-85.3h236.1c2.3 12.7 3.9 24.9 3.9 41.4z"></path>
                            </svg>
                        )}
                        Continue with Google
                    </Button>

                    {/* Divider */}
                    <div className="relative mb-5">
                        <div className="absolute inset-0 flex items-center">
                            <div className="w-full border-t border-slate-200" />
                        </div>
                        <div className="relative flex justify-center text-xs">
                            <span className="bg-white px-3 text-slate-400 font-medium">or continue with email</span>
                        </div>
                    </div>

                    {/* Error */}
                    {error && (
                        <Alert variant={error.includes('verify') ? 'default' : 'destructive'} className="mb-5 rounded-xl">
                            <AlertCircle className="h-4 w-4" />
                            <AlertDescription className="text-sm">{error}</AlertDescription>
                        </Alert>
                    )}

                    {/* Form */}
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="space-y-1.5">
                            <Label htmlFor="email" className="text-sm font-medium text-slate-700">Email</Label>
                            <div className="relative">
                                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                                <Input
                                    id="email"
                                    type="email"
                                    placeholder="you@example.com"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                    className="pl-9 h-11 border-slate-200 bg-slate-50 focus:bg-white focus:border-violet-400 rounded-xl"
                                />
                            </div>
                        </div>

                        <div className="space-y-1.5">
                            <Label htmlFor="password" className="text-sm font-medium text-slate-700">Password</Label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                                <Input
                                    id="password"
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    required
                                    className="pl-9 h-11 border-slate-200 bg-slate-50 focus:bg-white focus:border-violet-400 rounded-xl"
                                    placeholder="••••••••"
                                    minLength={6}
                                />
                            </div>
                        </div>

                        <Button
                            type="submit"
                            className="w-full h-11 bg-violet-600 hover:bg-violet-700 text-white font-semibold rounded-xl shadow-sm shadow-violet-500/20 transition-all mt-1"
                            disabled={loading || googleLoading}
                        >
                            {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                            {isLogin ? 'Sign In' : 'Create Account'}
                            {!loading && <ArrowRight className="ml-2 h-4 w-4" />}
                        </Button>
                    </form>

                    {/* Toggle */}
                    <p className="text-sm text-center text-slate-500 mt-6">
                        {isLogin ? "Don't have an account? " : "Already have an account? "}
                        <button
                            onClick={() => {
                                setIsLogin(!isLogin);
                                setError('');
                            }}
                            className="text-violet-600 hover:text-violet-700 font-semibold hover:underline transition-colors"
                        >
                            {isLogin ? 'Sign up for free' : 'Sign in'}
                        </button>
                    </p>

                    {/* Legal */}
                    <p className="text-xs text-slate-400 text-center mt-4 leading-relaxed">
                        By continuing, you agree to our{' '}
                        <Link to="/terms" className="hover:underline">Terms of Service</Link>
                        {' '}and{' '}
                        <Link to="/privacy" className="hover:underline">Privacy Policy</Link>.
                    </p>
                </div>
            </div>
        </div>
    );
};

export default AuthPage;
