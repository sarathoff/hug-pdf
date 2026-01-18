import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Sparkles, FileText, Briefcase, BarChart3, Receipt, ArrowRight, Search, Book, Lock, X } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const HomePage = () => {
  const [prompt, setPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [mode, setMode] = useState('normal'); // 'normal' | 'research' | 'ebook'
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const navigate = useNavigate();
  const { user } = useAuth();

  // Handle mode change with Pro user validation
  const handleModeChange = (newMode) => {
    // Check if user is Pro for research and ebook modes
    if (newMode === 'research' || newMode === 'ebook') {
      if (!user) {
        navigate('/auth');
        return;
      }
      if (user.plan !== 'pro') {
        setShowUpgradeModal(true);
        return;
      }
    }
    setMode(newMode);
  };

  const handleCreatePDF = () => {
    if (prompt.trim()) {
      if (!user) {
        navigate('/auth');
        return;
      }
      if (user.credits <= 0) {
        navigate('/pricing');
        return;
      }
      setIsGenerating(true);
      // Navigate immediately without splash screen, passing mode
      navigate('/editor', { state: { initialPrompt: prompt, mode: mode } });
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleCreatePDF();
    }
  };

  const examplePrompts = [
    { icon: FileText, text: 'Create a professional resume for a software engineer' },
    { icon: Briefcase, text: 'Write a business proposal for a new marketing campaign' },
    { icon: BarChart3, text: 'Design a project report with executive summary' },
    { icon: Receipt, text: 'Make an invoice template with logo placeholder' }
  ];

  return (
    <div className="relative z-10 w-full">
      <div className="relative z-10 max-w-5xl mx-auto px-4 sm:px-6 py-12 sm:py-20">
        {/* Header */}
        <div className="text-center mb-12 sm:mb-16 space-y-6">
          <Badge variant="secondary" className="mb-4 px-4 py-1.5 text-sm bg-blue-50 text-blue-700 border-blue-100 rounded-full cursor-default hover:bg-blue-50">
            <Sparkles className="w-3.5 h-3.5 mr-2 fill-blue-700" />
            AI-Powered PDF Generation
          </Badge>

          <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold tracking-tight text-gray-900">
            Create Beautiful PDFs
            <span className="block mt-2 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent pb-4">
              in Seconds with AI
            </span>
          </h1>

          <p className="text-base sm:text-lg md:text-xl text-gray-600 max-w-2xl mx-auto leading-relaxed px-4">
            Just describe what you need. Our advanced AI will generate, format, and deliver
            stunning professional PDFs tailored to your needs.
          </p>

          {/* Product Hunt Badge */}
          <div className="flex justify-center mt-6">
            <a
              href="https://www.producthunt.com/products/hugpdf?embed=true&utm_source=badge-featured&utm_medium=badge&utm_campaign=badge-hugpdf"
              target="_blank"
              rel="noopener noreferrer"
              className="transition-transform hover:scale-105 duration-200"
            >
              <img
                alt="HugPDF - Create Beautiful PDFs Using AI - Chat and Create PDFs | Product Hunt"
                width="250"
                height="54"
                src="https://api.producthunt.com/widgets/embed-image/v1/featured.svg?post_id=1064053&theme=light&t=1768729447472"
              />
            </a>
          </div>
        </div>

        {/* Main Input */}
        <Card className="border-0 shadow-2xl bg-white/80 backdrop-blur-xl mb-12 overflow-hidden ring-1 ring-gray-200/50 max-w-2xl mx-auto">
          <CardContent className="p-3 sm:p-5">
            {/* Mode Selector - Segmented Control */}
            <div className="flex justify-center mb-6">
              <div className="bg-gray-100/80 p-1 rounded-xl flex flex-col sm:flex-row relative shadow-inner w-full sm:w-auto">
                {/* Normal Mode */}
                <button
                  onClick={() => handleModeChange('normal')}
                  className={`relative flex items-center justify-center gap-2 px-4 sm:px-6 py-2.5 sm:py-2 rounded-lg text-sm font-medium transition-all duration-200 z-10 ${mode === 'normal'
                    ? 'bg-white text-blue-600 shadow-sm ring-1 ring-black/5'
                    : 'text-gray-500 hover:text-gray-900'
                    }`}
                >
                  <FileText className="w-4 h-4" />
                  <span>Normal</span>
                </button>

                {/* Research Mode */}
                <button
                  onClick={() => handleModeChange('research')}
                  className={`relative flex items-center justify-center gap-2 px-4 sm:px-6 py-2.5 sm:py-2 rounded-lg text-sm font-medium transition-all duration-200 z-10 ${mode === 'research'
                    ? 'bg-white text-purple-600 shadow-sm ring-1 ring-black/5'
                    : 'text-gray-500 hover:text-gray-900'
                    }`}
                >
                  <Search className="w-4 h-4" />
                  <span>Research</span>
                  {(user?.plan !== 'pro' || !user) && <Lock className="w-3 h-3 ml-0.5 opacity-50" />}
                </button>

                {/* E-book Mode */}
                <button
                  onClick={() => handleModeChange('ebook')}
                  className={`relative flex items-center justify-center gap-2 px-4 sm:px-6 py-2.5 sm:py-2 rounded-lg text-sm font-medium transition-all duration-200 z-10 ${mode === 'ebook'
                    ? 'bg-white text-green-600 shadow-sm ring-1 ring-black/5'
                    : 'text-gray-500 hover:text-gray-900'
                    }`}
                >
                  <Book className="w-4 h-4" />
                  <span>E-book</span>
                  {(user?.plan !== 'pro' || !user) && <Lock className="w-3 h-3 ml-0.5 opacity-50" />}
                </button>
              </div>
            </div>

            {/* Mode Description Message */}
            {mode !== 'normal' && (
              <div className="text-center mb-5 -mt-2 animate-in fade-in slide-in-from-top-2 duration-300 px-4">
                <div className={`inline-flex flex-col sm:flex-row items-center gap-1.5 sm:gap-2 px-4 py-1.5 rounded-full text-xs font-medium ${mode === 'research' ? 'bg-purple-100/50 text-purple-700' : 'bg-green-100/50 text-green-700'
                  }`}>
                  {mode === 'research' ? (
                    <>
                      <div className="flex items-center gap-1.5">
                        <Search className="w-3 h-3" />
                        <span>Research mode with citations</span>
                      </div>
                      <span className="hidden sm:inline opacity-30">|</span>
                      <span className="opacity-75 font-semibold">Powered by Perplexity AI</span>
                    </>
                  ) : (
                    <>
                      <Book className="w-3 h-3" />
                      E-book mode creates structured 20+ page documents
                    </>
                  )}
                </div>
              </div>
            )}

            <div className="flex flex-col sm:flex-row items-stretch gap-2 transition-all">
              <div className="flex-1 flex items-center gap-3 px-4 py-3 sm:py-2 bg-white sm:bg-transparent rounded-lg border sm:border-0 border-gray-100">
                <Sparkles className="w-5 h-5 text-blue-500 animate-pulse flex-shrink-0" />
                <input
                  type="text"
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Describe your PDF..."
                  className="flex-1 bg-transparent parse-none outline-none text-gray-900 placeholder-gray-400 text-base sm:text-lg w-full min-w-0"
                />
              </div>
              <Button
                onClick={handleCreatePDF}
                disabled={!prompt.trim() || isGenerating}
                size="lg"
                className="h-12 sm:h-14 px-8 text-base bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-lg rounded-xl transition-all duration-300 transform hover:scale-[1.02] w-full sm:w-auto mt-2 sm:mt-0"
              >
                Generate
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Example Prompts */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-4xl mx-auto px-2">
          {examplePrompts.map((example, index) => {
            const Icon = example.icon;
            return (
              <button
                key={index}
                onClick={() => setPrompt(example.text)}
                className="group flex items-center gap-4 p-4 bg-white/50 hover:bg-white border border-gray-100 hover:border-blue-100 rounded-2xl transition-all duration-300 hover:shadow-lg text-left"
              >
                <div className="p-3 bg-white rounded-xl shadow-sm group-hover:bg-blue-50 group-hover:text-blue-600 transition-colors flex-shrink-0">
                  <Icon className="w-5 h-5 text-gray-500 group-hover:text-blue-600" />
                </div>
                <span className="text-sm sm:text-base text-gray-600 group-hover:text-gray-900 font-medium transition-colors">
                  {example.text}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Upgrade Modal for Pro Features */}
      {showUpgradeModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-[100] p-4 animate-in fade-in duration-200">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 relative transform transition-all scale-100">
            <button
              onClick={() => setShowUpgradeModal(false)}
              className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="text-center">
              <div className="w-16 h-16 bg-gradient-to-r from-purple-100 to-blue-100 rounded-full flex items-center justify-center mx-auto mb-4 ring-4 ring-white shadow-lg">
                <Lock className="w-8 h-8 text-purple-600" />
              </div>

              <h3 className="text-2xl font-bold text-gray-900 mb-2">
                {user ? 'Unlock Pro Features' : 'Login Required'}
              </h3>
              <p className="text-gray-600 mb-6">
                {user
                  ? 'Research Mode and E-book Mode are exclusive features for Pro users. Upgrade to unlock advanced AI capabilities!'
                  : 'Please sign in or create an account to access advanced features like Research Mode and E-book creation.'
                }
              </p>

              <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl p-5 mb-6 border border-purple-100/50">
                <h4 className="font-semibold text-gray-900 mb-3 text-sm uppercase tracking-wider">
                  {user ? 'Pro Features Include:' : 'Advanced Features:'}
                </h4>
                <ul className="text-sm text-gray-700 space-y-2.5 text-left">
                  <li className="flex items-center gap-2.5">
                    <div className="p-1 bg-purple-100 rounded text-purple-600"><Search className="w-3.5 h-3.5" /></div>
                    Research Mode with citations
                  </li>
                  <li className="flex items-center gap-2.5">
                    <div className="p-1 bg-green-100 rounded text-green-600"><Book className="w-3.5 h-3.5" /></div>
                    E-book creation (20+ pages)
                  </li>
                  <li className="flex items-center gap-2.5">
                    <div className="p-1 bg-blue-100 rounded text-blue-600"><FileText className="w-3.5 h-3.5" /></div>
                    50 PDF downloads/month
                  </li>
                </ul>
              </div>

              <div className="flex gap-3">
                <Button
                  variant="outline"
                  onClick={() => setShowUpgradeModal(false)}
                  className="flex-1 border-gray-200 hover:bg-gray-50 text-gray-700"
                >
                  Maybe Later
                </Button>
                <Button
                  onClick={() => {
                    setShowUpgradeModal(false);
                    navigate(user ? '/pricing' : '/auth');
                  }}
                  className="flex-1 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white shadow-lg shadow-blue-500/25"
                >
                  {user ? 'Upgrade to Pro' : 'Login / Sign Up'}
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default HomePage;
