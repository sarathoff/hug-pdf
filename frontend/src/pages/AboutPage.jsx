import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { Sparkles, Code, Database, Brain, Zap, Shield, Mail, Github, Heart } from 'lucide-react';

const AboutPage = () => {
  const navigate = useNavigate();
  const technologies = [
    { icon: Code, name: 'React', description: 'Modern UI framework' },
    { icon: Zap, name: 'FastAPI', description: 'High-performance backend' },
    { icon: Database, name: 'Supabase', description: 'PostgreSQL database' },
    { icon: Brain, name: 'Google Gemini AI', description: 'AI-powered generation' },
  ];

  return (
    <div className="relative w-full h-full max-w-5xl mx-auto px-4 sm:px-6 py-12 sm:py-16">
      {/* Hero Section */}
      <div className="text-center mb-8 sm:mb-16">
        <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold mb-4 sm:mb-6 px-4 text-gray-900">
          About
          <span className="block mt-2 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            HugPDF
          </span>
        </h1>
        <p className="text-base sm:text-lg md:text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed px-4">
          Transform your ideas into beautiful, professional PDFs with the power of artificial intelligence.
        </p>
      </div>

      {/* Creator's Story */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl shadow-xl p-6 sm:p-10 text-white mb-8 sm:mb-12 relative overflow-hidden">
        <div className="absolute top-0 right-0 p-32 bg-white/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 pointer-events-none"></div>

        <h2 className="text-xl sm:text-2xl font-bold mb-4 sm:mb-6 relative z-10">My Story</h2>
        <div className="text-blue-50 leading-relaxed space-y-4 sm:space-y-5 text-sm sm:text-base relative z-10">
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
          <p className="font-semibold text-white pt-2">
            I hope HugPDF helps you create beautiful documents as easily as it helps me! 🚀
          </p>
        </div>

        {/* Contact Links */}
        <div className="mt-8 pt-6 border-t border-white/20 flex flex-col sm:flex-row flex-wrap gap-4 relative z-10">
          <a
            href="mailto:sarathramesh.mailbox@gmail.com"
            className="flex items-center gap-2 bg-white/10 hover:bg-white/20 px-4 py-2.5 rounded-lg transition-colors text-sm sm:text-base backdrop-blur-sm"
          >
            <Mail className="w-4 h-4 flex-shrink-0" />
            <span className="truncate">sarathramesh.mailbox@gmail.com</span>
          </a>
          <a
            href="https://github.com/sarathoff"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 bg-white/10 hover:bg-white/20 px-4 py-2.5 rounded-lg transition-colors backdrop-blur-sm"
          >
            <Github className="w-4 h-4" />
            <span>@sarathoff</span>
          </a>
        </div>
      </div>

      {/* Mission Section */}
      <Card className="mb-8 sm:mb-12 border-none shadow-lg">
        <CardContent className="p-6 sm:p-8">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-blue-50 rounded-lg">
              <Sparkles className="w-6 h-6 text-blue-600" />
            </div>
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
        </CardContent>
      </Card>

      {/* Technology Stack */}
      <div className="mb-8 sm:mb-12">
        <h2 className="text-xl sm:text-2xl font-bold text-gray-900 mb-6 sm:mb-8 text-center px-4">Built With Modern Technology</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {technologies.map((tech) => {
            const Icon = tech.icon;
            return (
              <div
                key={tech.name}
                className="bg-white rounded-xl border border-gray-100 p-6 shadow-sm hover:shadow-md transition-shadow"
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
      <Card className="mb-8 sm:mb-12 border-none shadow-lg">
        <CardContent className="p-6 sm:p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Key Features</h2>
          <ul className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {[
              { title: 'LaTeX-Powered Quality', desc: 'Professional PDFs that outperform Canva and Google Docs' },
              { title: 'AI-Powered Generation', desc: 'Leverages Google Gemini AI for intelligent content creation' },
              { title: 'Interactive Editing', desc: 'Chat with AI to refine and customize your documents' },
              { title: 'Instant Download', desc: 'Generate and download professional PDFs in seconds' }
            ].map((feature, i) => (
              <li key={i} className="flex items-start gap-3 p-3 rounded-lg bg-gray-50 border border-gray-100">
                <Shield className="w-5 h-5 text-green-600 mt-1 flex-shrink-0" />
                <div>
                  <span className="font-semibold text-gray-900 block mb-1">{feature.title}</span>
                  <span className="text-sm text-gray-600">{feature.desc}</span>
                </div>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>

      {/* Message from Developer */}
      <div className="text-center py-8">
        <div className="flex items-center justify-center gap-2 text-gray-500 mb-4">
          <span>Made with</span>
          <Heart className="w-5 h-5 text-red-500 fill-current animate-pulse" />
          <span>for students and professionals</span>
        </div>
        <Button
          onClick={() => navigate('/')}
          size="lg"
          className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-lg rounded-xl px-8"
        >
          Start Creating Now
        </Button>
      </div>
    </div>
  );
};

export default AboutPage;
