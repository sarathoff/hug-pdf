import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Sparkles, FileText, Briefcase, BarChart3, Receipt } from 'lucide-react';

const HomePage = () => {
  const [prompt, setPrompt] = useState('');
  const navigate = useNavigate();

  const handleCreatePDF = () => {
    if (prompt.trim()) {
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
    { icon: FileText, text: 'Create a professional resume' },
    { icon: Briefcase, text: 'Write a business proposal' },
    { icon: BarChart3, text: 'Design a project report' },
    { icon: Receipt, text: 'Make an invoice template' }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      <div className="max-w-5xl mx-auto px-6 py-16">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-6xl font-bold mb-6 tracking-tight">
            Create Beautiful PDFs
            <span className="block mt-2 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              with AI
            </span>
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto leading-relaxed">
            Just describe what you need. Our AI will generate, format, and deliver
            stunning PDFs in seconds.
          </p>
        </div>

        {/* Main Input */}
        <div className="bg-white rounded-2xl shadow-lg p-3 mb-12 hover:shadow-xl transition-shadow duration-300">
          <div className="flex items-center gap-3">
            <div className="flex-1 flex items-center gap-3 px-4">
              <Sparkles className="w-5 h-5 text-blue-500 flex-shrink-0" />
              <input
                type="text"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Describe your PDF... e.g., 'Create a marketing proposal for a tech startup'"
                className="flex-1 py-4 bg-transparent outline-none text-gray-800 placeholder-gray-400 text-base"
              />
            </div>
            <Button
              onClick={handleCreatePDF}
              disabled={!prompt.trim()}
              className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-6 rounded-xl font-medium shadow-md hover:shadow-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Create PDF
            </Button>
          </div>
        </div>

        {/* Example Prompts */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-3xl mx-auto">
          {examplePrompts.map((example, index) => {
            const Icon = example.icon;
            return (
              <button
                key={index}
                onClick={() => setPrompt(example.text)}
                className="flex items-center gap-3 px-6 py-4 bg-white rounded-xl border border-gray-200 hover:border-blue-300 hover:shadow-md transition-all duration-300 text-left group"
              >
                <div className="p-2 bg-blue-50 rounded-lg group-hover:bg-blue-100 transition-colors duration-300">
                  <Icon className="w-5 h-5 text-blue-600" />
                </div>
                <span className="text-gray-700 font-medium">{example.text}</span>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default HomePage;