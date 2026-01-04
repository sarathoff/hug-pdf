import React from 'react';
import { Link } from 'react-router-dom';
import { Sparkles, Code, Database, Brain, Zap, Shield, Home, Github, Mail } from 'lucide-react';
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
          <div className="flex items-center gap-2">
            <img src="/logo.png" alt="HugPDF Logo" className="h-8 w-auto" />
          </div>
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

        {/* Creator's Story */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl shadow-lg p-8 text-white mb-12">
          <h2 className="text-2xl font-bold mb-4">My Story</h2>
          <div className="text-blue-50 leading-relaxed space-y-4">
            <p>
              Hi, I'm <span className="font-semibold text-white">Sarath</span>, an ECE engineering student and the creator of HugPDF.
            </p>
            <p>
              During my studies, I constantly faced a frustrating problem: whenever we worked on projects, our professors
              would ask us to submit PDFs. I got tired of spending hours formatting documents in Google Docs, trying to
              make them look professional. It was time-consuming and often didn't give me the results I wanted.
            </p>
            <p>
              Then I discovered LaTeX. Whether I needed to create research papers or ATS-friendly resumes, LaTeX-generated
              PDFs performed significantly better than anything I could make in Canva or Google Docs. The quality was
              professional, the formatting was consistent, and the output was exactly what I needed.
            </p>
            <p>
              But there was a problem: LaTeX has a steep learning curve. So I thought, "What if I could combine the power
              of LaTeX with the simplicity of AI?" That's when I built HugPDF in just 3 days with the help of AI.
            </p>
            <p>
              As a student, I always preferred free apps. But after building this AI-powered software for everyone, I now
              understand why AI-based apps need to be paid. The API costs add up quickly! I've tried my best to keep it
              affordable by offering 3 free PDF downloads. Once I can better manage the AI request costs, I'll definitely
              increase the free tier to help more students like me.
            </p>
            <p className="font-semibold text-white">
              I hope HugPDF helps you create beautiful documents as easily as it helps me! 🚀
            </p>
          </div>

          {/* Contact Links */}
          <div className="mt-6 pt-6 border-t border-blue-400 flex flex-wrap gap-4">
            <a
              href="mailto:sarathramesh.mailbox@gmail.com"
              className="flex items-center gap-2 bg-white/10 hover:bg-white/20 px-4 py-2 rounded-lg transition-colors"
            >
              <Mail className="w-4 h-4" />
              <span>sarathramesh.mailbox@gmail.com</span>
            </a>
            <a
              href="https://github.com/sarathoff"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 bg-white/10 hover:bg-white/20 px-4 py-2 rounded-lg transition-colors"
            >
              <Github className="w-4 h-4" />
              <span>@sarathoff</span>
            </a>
          </div>
        </div>

        {/* Mission Section */}
        <div className="bg-white rounded-2xl shadow-lg p-8 mb-12">
          <div className="flex items-center gap-3 mb-4">
            <Sparkles className="w-6 h-6 text-blue-600" />
            <h2 className="text-2xl font-bold text-gray-900">Why HugPDF?</h2>
          </div>
          <p className="text-gray-700 leading-relaxed mb-4">
            HugPDF was created to make professional document creation accessible to everyone. No more struggling
            with complex formatting or spending hours trying to make your documents look good.
          </p>
          <p className="text-gray-700 leading-relaxed">
            Just describe what you need in plain English, and our AI will generate a beautifully formatted LaTeX
            document that you can download as a PDF. It's that simple!
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

        {/* Features */}
        <div className="bg-white rounded-2xl shadow-lg p-8 mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Key Features</h2>
          <ul className="space-y-4">
            <li className="flex items-start gap-3">
              <Shield className="w-5 h-5 text-green-600 mt-1 flex-shrink-0" />
              <div>
                <span className="font-semibold text-gray-900">LaTeX-Powered Quality:</span>
                <span className="text-gray-700"> Professional PDFs that outperform Canva and Google Docs</span>
              </div>
            </li>
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
          </ul>
        </div>

        {/* Feedback Section */}
        <div className="bg-blue-50 rounded-2xl p-8 mb-12 border border-blue-200">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Support & Suggestions</h2>
          <p className="text-gray-700 leading-relaxed mb-4">
            Have ideas to improve HugPDF? Found a bug? Want to suggest a feature? I'd love to hear from you!
          </p>
          <p className="text-gray-700">
            Send your feedback directly to:{' '}
            <a
              href="mailto:sarathramesh.mailbox@gmail.com"
              className="text-blue-600 hover:text-blue-700 font-semibold"
            >
              sarathramesh.mailbox@gmail.com
            </a>
          </p>
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
