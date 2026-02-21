import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import {
  Sparkles, Code, Database, Brain, Zap, Shield,
  Mail, Github, Heart, CheckCircle2, ArrowRight,
} from 'lucide-react';

const AboutPage = () => {
  const navigate = useNavigate();

  const technologies = [
    { icon: Code, name: 'React', description: 'Modern UI framework for fast, interactive interfaces' },
    { icon: Zap, name: 'FastAPI', description: 'High-performance Python backend with async support' },
    { icon: Database, name: 'Supabase', description: 'PostgreSQL database with real-time capabilities' },
    { icon: Brain, name: 'Google Gemini AI', description: 'State-of-the-art AI for intelligent document generation' },
  ];

  const features = [
    { title: 'LaTeX-Powered Quality', desc: 'Professional PDFs that outperform Canva and Google Docs' },
    { title: 'AI-Powered Generation', desc: 'Leverages Google Gemini AI for intelligent content creation' },
    { title: 'Interactive Editing', desc: 'Chat with AI to refine and customize your documents' },
    { title: 'Instant Download', desc: 'Generate and download professional PDFs in seconds' },
  ];

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Hero Section */}
      <div className="bg-white border-b border-slate-100 py-20 px-4">
        <div className="max-w-4xl mx-auto text-center space-y-5">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-violet-50 border border-violet-200 rounded-full text-xs font-semibold text-violet-700 uppercase tracking-wider">
            <Heart className="w-3.5 h-3.5 fill-violet-400 text-violet-400" />
            Built by a student, for everyone
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-slate-900">
            About{' '}
            <span className="text-violet-600">HugPDF</span>
          </h1>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto leading-relaxed">
            Transform your ideas into beautiful, professional PDFs with the power of artificial intelligence.
            No design skills, no LaTeX knowledge required.
          </p>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-16 space-y-12">
        {/* Creator's Story Card */}
        <div className="relative bg-slate-900 rounded-2xl overflow-hidden shadow-xl">
          {/* Background decoration */}
          <div className="absolute top-0 right-0 w-64 h-64 bg-violet-600/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 pointer-events-none" />
          <div className="absolute bottom-0 left-0 w-48 h-48 bg-blue-600/10 rounded-full blur-3xl translate-y-1/2 -translate-x-1/2 pointer-events-none" />

          <div className="relative z-10 p-8 sm:p-10">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-violet-500/20 rounded-lg">
                <Sparkles className="w-5 h-5 text-violet-400" />
              </div>
              <h2 className="text-xl font-bold text-white">My Story</h2>
            </div>

            <div className="text-slate-300 leading-relaxed space-y-4 text-sm sm:text-base">
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
                As a student, I always preferred free apps. But after building this AI-powered software, I now
                understand why AI-based apps need to be paid. The API costs add up quickly! I've tried my best to keep it
                affordable by offering 3 free PDF downloads. Once I can better manage the AI request costs, I'll definitely
                increase the free tier to help more users create professional documents.
              </p>
              <p className="font-semibold text-white pt-2">
                I hope HugPDF helps you create beautiful documents as easily as it helps me!
              </p>
            </div>

            {/* Contact Links */}
            <div className="mt-8 pt-6 border-t border-white/10 flex flex-col sm:flex-row flex-wrap gap-3">
              <a
                href="mailto:sarathramesh.mailbox@gmail.com"
                className="inline-flex items-center gap-2 px-4 py-2.5 bg-white/10 hover:bg-white/20 text-white rounded-lg text-sm font-medium transition-colors"
              >
                <Mail className="w-4 h-4 shrink-0" />
                <span className="truncate">sarathramesh.mailbox@gmail.com</span>
              </a>
              <a
                href="https://github.com/sarathoff"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-4 py-2.5 bg-white/10 hover:bg-white/20 text-white rounded-lg text-sm font-medium transition-colors"
              >
                <Github className="w-4 h-4" />
                @sarathoff
              </a>
            </div>
          </div>
        </div>

        {/* Mission Section */}
        <div className="bg-white rounded-2xl border border-slate-200 p-8 shadow-sm">
          <div className="flex items-center gap-3 mb-5">
            <div className="p-2.5 bg-violet-50 rounded-xl">
              <Sparkles className="w-5 h-5 text-violet-600" />
            </div>
            <h2 className="text-2xl font-bold text-slate-900">Why HugPDF?</h2>
          </div>
          <div className="space-y-3 text-slate-600 leading-relaxed">
            <p>
              HugPDF was created to make professional document creation accessible to everyone. No more struggling
              with complex formatting or spending hours trying to make your documents look good.
            </p>
            <p>
              Just describe what you need in plain English, and our AI will generate a beautifully formatted LaTeX
              document that you can download as a PDF. It's that simple.
            </p>
          </div>
        </div>

        {/* Technology Stack */}
        <div>
          <h2 className="text-2xl font-bold text-slate-900 mb-6 text-center">Built With Modern Technology</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {technologies.map((tech) => {
              const Icon = tech.icon;
              return (
                <div
                  key={tech.name}
                  className="flex items-start gap-4 p-5 bg-white rounded-xl border border-slate-200 shadow-sm hover:border-violet-200 hover:shadow-md transition-all duration-200 group"
                >
                  <div className="p-2.5 bg-violet-50 rounded-lg group-hover:bg-violet-100 transition-colors shrink-0">
                    <Icon className="w-5 h-5 text-violet-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-900 mb-0.5">{tech.name}</h3>
                    <p className="text-sm text-slate-500">{tech.description}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Key Features */}
        <div className="bg-white rounded-2xl border border-slate-200 p-8 shadow-sm">
          <h2 className="text-2xl font-bold text-slate-900 mb-6">Key Features</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {features.map((feature, i) => (
              <div
                key={i}
                className="flex items-start gap-3 p-4 rounded-xl bg-slate-50 border border-slate-100"
              >
                <div className="p-0.5 rounded-full bg-emerald-100 shrink-0 mt-0.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                </div>
                <div>
                  <span className="font-semibold text-slate-900 block mb-0.5 text-sm">{feature.title}</span>
                  <span className="text-sm text-slate-500">{feature.desc}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* CTA */}
        <div className="text-center py-8 space-y-5">
          <div className="flex items-center justify-center gap-2 text-slate-500">
            <span className="text-sm">Made with</span>
            <Heart className="w-4 h-4 text-red-500 fill-current animate-pulse" />
            <span className="text-sm">for researchers, creators, and marketers</span>
          </div>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Button
              onClick={() => navigate('/')}
              size="lg"
              className="h-12 px-8 bg-violet-600 hover:bg-violet-700 text-white rounded-xl font-semibold shadow-lg shadow-violet-500/20"
            >
              Start Creating Now
              <ArrowRight className="ml-2 w-4 h-4" />
            </Button>
            <a
              href="https://github.com/sarathoff/hug-pdf"
              target="_blank"
              rel="noopener noreferrer"
            >
              <Button
                variant="outline"
                size="lg"
                className="h-12 px-8 rounded-xl font-semibold border-slate-200 text-slate-700 hover:bg-slate-50 w-full sm:w-auto"
              >
                <Github className="mr-2 w-4 h-4" />
                View on GitHub
              </Button>
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AboutPage;
