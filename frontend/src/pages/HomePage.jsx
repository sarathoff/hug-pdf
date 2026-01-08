import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Sparkles, FileText, Briefcase, BarChart3, Receipt, ArrowRight } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const HomePage = () => {
  const [prompt, setPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const navigate = useNavigate();
  const { user } = useAuth();

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
      // Navigate immediately without splash screen
      navigate('/editor', { state: { initialPrompt: prompt } });
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
        </div>

        {/* Main Input */}
        <Card className="border-0 shadow-2xl bg-white/80 backdrop-blur-xl mb-12 overflow-hidden ring-1 ring-gray-200/50 max-w-2xl mx-auto">
          <CardContent className="p-2 sm:p-3">
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
    </div>
  );
};

export default HomePage;
