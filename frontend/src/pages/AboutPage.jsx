import React from 'react';
import { Link } from 'react-router-dom';
import { Sparkles, Code, Database, Brain, Zap, Shield, Home } from 'lucide-react';
import { Button } from '../components/ui/button';
import { useNavigate } from 'react-router-dom';

const AboutPage = () => {
  const navigate = useNavigate();
  const technologies = [
    { icon: Code, name: 'React', description: 'Modern UI framework' },
    { icon: Zap, name: 'FastAPI', description: 'High-performance backend' },
    { icon: Database, name: 'Supabase', description: 'PostgreSQL database' },
    { icon: Brain, name: 'Google Gemini AI', description: 'AI-powered generation' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <h1 className="text-xl font-semibold text-gray-800">About Us</h1>
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

      <div className="max-w-5xl mx-auto px-6 py-16">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold mb-6">
            About
            <span className="block mt-2 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              HugPDF
            </span>
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
            Transform your ideas into beautiful, professional PDFs with the power of artificial intelligence.
          </p>
        </div>

        {/* Mission Section */}
        <div className="bg-white rounded-2xl shadow-lg p-8 mb-12">
          <div className="flex items-center gap-3 mb-4">
            <Sparkles className="w-6 h-6 text-blue-600" />
            <h2 className="text-2xl font-bold text-gray-900">Our Mission</h2>
          </div>
          <p className="text-gray-700 leading-relaxed mb-4">
            HugPDF was created to simplify document creation. Whether you need a resume, business proposal,
            invoice, or any other document, our AI-powered platform generates professional PDFs in seconds.
          </p>
          <p className="text-gray-700 leading-relaxed">
            We believe that creating beautiful documents shouldn't require hours of formatting and design work.
            Just describe what you need, and let our AI handle the rest.
          </p>
        </div>

        {/* Technology Stack */}
        <div className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">Built With Modern Technology</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {technologies.map((tech) => {
              const Icon = tech.icon;
              return (
                <div
                  key={tech.name}
                  className="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-lg transition-shadow"
                >
                  <div className="flex items-start gap-4">
                    <div className="p-3 bg-blue-50 rounded-lg">
                      <Icon className="w-6 h-6 text-blue-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-1">{tech.name}</h3>
                      <p className="text-sm text-gray-600">{tech.description}</p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* About Creator */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl shadow-lg p-8 text-white mb-12">
          <h2 className="text-2xl font-bold mb-4">About the Creator</h2>
          <p className="text-blue-50 leading-relaxed mb-4">
            Hi, I'm <span className="font-semibold text-white">Sarath</span>, the creator of HugPDF.
            I built this tool to make document creation faster and easier for everyone.
          </p>
          <p className="text-blue-50 leading-relaxed">
            As a developer passionate about AI and web technologies, I wanted to create something that combines
            the power of modern AI with practical everyday needs. This project showcases the potential of
            AI-assisted content generation while maintaining a focus on user experience and simplicity.
          </p>
        </div>

        {/* Features */}
        <div className="bg-white rounded-2xl shadow-lg p-8 mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Key Features</h2>
          <ul className="space-y-4">
            <li className="flex items-start gap-3">
              <Shield className="w-5 h-5 text-green-600 mt-1 flex-shrink-0" />
              <div>
                <span className="font-semibold text-gray-900">AI-Powered Generation:</span>
                <span className="text-gray-700"> Leverages Google Gemini AI for intelligent content creation</span>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <Shield className="w-5 h-5 text-green-600 mt-1 flex-shrink-0" />
              <div>
                <span className="font-semibold text-gray-900">Interactive Editing:</span>
                <span className="text-gray-700"> Chat with AI to refine and customize your documents</span>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <Shield className="w-5 h-5 text-green-600 mt-1 flex-shrink-0" />
              <div>
                <span className="font-semibold text-gray-900">Instant Download:</span>
                <span className="text-gray-700"> Generate and download professional PDFs in seconds</span>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <Shield className="w-5 h-5 text-green-600 mt-1 flex-shrink-0" />
              <div>
                <span className="font-semibold text-gray-900">Free to Use:</span>
                <span className="text-gray-700"> No subscriptions, no hidden fees, completely free</span>
              </div>
            </li>
          </ul>
        </div>

        {/* CTA */}
        <div className="text-center">
          <Link
            to="/"
            className="inline-block bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-4 rounded-xl font-medium shadow-lg hover:shadow-xl transition-all duration-300"
          >
            Try HugPDF Now
          </Link>
        </div>
      </div>
    </div>
  );
};

export default AboutPage;
