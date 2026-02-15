import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Textarea } from '../components/ui/textarea';
import { 
  Sparkles, FileText, Briefcase, BarChart3, Receipt, ArrowRight, 
  Search, Book, Lock, X, Upload, Target, Presentation, 
  CheckCircle2, Zap, LayoutTemplate, GraduationCap, Building2, PenTool, Mic
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import VoiceRecorder from '../components/VoiceRecorder';

const HomePage = () => {
  const [prompt, setPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [mode, setMode] = useState('normal'); // 'normal' | 'research' | 'ebook' | 'ppt'
  
  // PPT Mode States
  const [pptInputMode, setPptInputMode] = useState('topic'); // 'topic' or 'content'
  const [pptTopic, setPptTopic] = useState('');
  const [pptContent, setPptContent] = useState('');
  const [pptStyle, setPptStyle] = useState('minimal');

  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const [showResumeOptimizerModal, setShowResumeOptimizerModal] = useState(false);
  const [resumeFile, setResumeFile] = useState(null);
  const [jobDescription, setJobDescription] = useState('');
  const [optimizerLoading, setOptimizerLoading] = useState(false);
  const [showVoiceRecorder, setShowVoiceRecorder] = useState(false);
  const navigate = useNavigate();
  const { user } = useAuth();
  
  // Use Case Tab State
  const [activeTab, setActiveTab] = useState('students');

  // Handle mode change with Pro user validation
  const handleModeChange = (newMode) => {
    if (newMode === 'research' || newMode === 'ebook') {
      if (!user) {
        navigate('/auth');
        return;
      }
      // Check credits instead of plan: >5 credits = Pro user
      if (user.credits <= 5) {
        setShowUpgradeModal(true);
        return;
      }
    }
    setMode(newMode);
  };

  const handleCreatePDF = () => {
    let isValid = false;
    if (mode === 'ppt') {
      isValid = (pptInputMode === 'topic' && pptTopic.trim()) || (pptInputMode === 'content' && pptContent.trim());
    } else {
      isValid = prompt.trim();
    }

    if (isValid) {
      if (!user) {
        navigate('/auth');
        return;
      }
      
      if (mode !== 'ppt' && user.credits <= 0) {
        navigate('/pricing');
        return;
      }
      
      setIsGenerating(true);
      
      if (mode === 'ppt') {
        navigate('/editor', { 
            state: { 
                mode: 'ppt',
                pptConfig: {
                    topic: pptInputMode === 'topic' ? pptTopic : null,
                    content: pptInputMode === 'content' ? pptContent : null,
                    numSlides: 10,
                    style: pptStyle
                }
            } 
        });
      } else {
        navigate('/editor', { state: { initialPrompt: prompt, mode: mode } });
      }
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleCreatePDF();
    }
  };

  const handleOptimizeResume = async () => {
    if (!resumeFile) return;
    if (!user) {
      navigate('/auth');
      return;
    }
    setOptimizerLoading(true);
    try {
      const formData = new FormData();
      formData.append('resume_pdf', resumeFile);
      if (jobDescription.trim()) formData.append('job_description', jobDescription);

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/optimize-resume`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${user.token || localStorage.getItem('token')}` 
        },
        body: formData
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to optimize resume');
      }

      const data = await response.json();
      setShowResumeOptimizerModal(false);
      setResumeFile(null);
      setJobDescription('');
      navigate('/editor', { 
        state: { 
          initialLatex: data.latex_content,
          mode: 'normal',
          skipGeneration: true,
          atsScore: data.ats_score,
          improvements: data.improvements
        } 
      });
    } catch (error) {
      console.error('Resume optimization error:', error);
      alert(error.message || 'Failed to optimize resume');
    } finally {
      setOptimizerLoading(false);
    }
  };

  const examplePrompts = [
    { icon: FileText, text: 'Create a professional resume for a software engineer' },
    { icon: Briefcase, text: 'Write a business proposal for a new marketing campaign' },
    { icon: BarChart3, text: 'Design a project report with executive summary' },
    { icon: Receipt, text: 'Make an invoice template with logo placeholder' }
  ];

  return (
    <div className="min-h-screen bg-slate-50 font-sans selection:bg-violet-100 selection:text-violet-900">
      {/* Hero Section */}
      <div className="relative pt-20 pb-32 overflow-hidden">
        {/* Abstract Background Shapes */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full z-0 pointer-events-none">
          <div className="absolute top-20 left-10 w-72 h-72 bg-violet-200/30 rounded-full blur-3xl" />
          <div className="absolute bottom-10 right-10 w-96 h-96 bg-blue-200/30 rounded-full blur-3xl" />
        </div>

        <div className="relative z-10 max-w-6xl mx-auto px-4 sm:px-6">
          <div className="text-center space-y-8 mb-16">
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-white border border-slate-200 rounded-full shadow-sm animate-in fade-in slide-in-from-bottom-4 duration-700">
              <Sparkles className="w-4 h-4 text-violet-600" />
              <span className="text-sm font-medium text-slate-600">The #1 AI Writing Partner for Professionals</span>
            </div>

            <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-slate-900 max-w-4xl mx-auto leading-[1.1]">
              Turn text into <span className="text-violet-600">beautiful documents</span> instantly.
            </h1>

            <p className="text-xl text-slate-600 max-w-2xl mx-auto leading-relaxed">
              Create professional PDFs, E-books, and Presentations in seconds using advanced AI. 
              No design skills required.
            </p>
          </div>

          {/* Main Interactive Card */}
          <div className="relative max-w-3xl mx-auto">
            <div className="absolute -inset-1 bg-gradient-to-r from-violet-500 to-fuchsia-500 rounded-2xl blur opacity-20" />
            <Card className="relative border-0 shadow-2xl bg-white/95 backdrop-blur-xl ring-1 ring-slate-200/50">
              <CardContent className="p-6">
                {/* Segmented Control Mode Selector */}
                <div className="flex justify-center mb-8">
                  <div className="inline-flex bg-slate-100/80 p-1.5 rounded-full shadow-inner gap-1">
                    {[
                      { id: 'normal', icon: FileText, label: 'Docs' },
                      { id: 'ppt', icon: Presentation, label: 'Slides' },
                      { id: 'research', icon: Search, label: 'Research' },
                      { id: 'ebook', icon: Book, label: 'E-books' }
                    ].map((m) => (
                      <button
                        key={m.id}
                        onClick={() => handleModeChange(m.id)}
                        className={`flex items-center gap-2 px-5 py-2.5 rounded-full text-sm font-medium transition-all duration-300 ${
                          mode === m.id
                            ? 'bg-white text-violet-700 shadow-sm ring-1 ring-black/5'
                            : 'text-slate-500 hover:text-slate-900 hover:bg-slate-200/50'
                        }`}
                      >
                        <m.icon className="w-4 h-4" />
                        {m.label}
                        {(m.id === 'research' || m.id === 'ebook') && (!user || user.credits <= 5) && (
                          <Lock className="w-3 h-3 ml-1 opacity-40" />
                        )}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Input Area */}
                {mode === 'ppt' ? (
                  <div className="space-y-4 animate-in fade-in duration-300">
                    <div className="flex gap-2 mb-2 p-1 bg-slate-50 rounded-lg w-fit">
                      {['topic', 'content'].map((type) => (
                        <button
                          key={type}
                          onClick={() => setPptInputMode(type)}
                          className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all ${
                            pptInputMode === type ? 'bg-white shadow-sm text-slate-900' : 'text-slate-500 hover:text-slate-900'
                          }`}
                        >
                          From {type.charAt(0).toUpperCase() + type.slice(1)}
                        </button>
                      ))}
                    </div>
                    {pptInputMode === 'topic' ? (
                      <div className="relative group">
                         <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                            <Sparkles className="h-5 w-5 text-violet-400 group-focus-within:text-violet-600 transition-colors" />
                         </div>
                        <input
                          type="text"
                          value={pptTopic}
                          onChange={(e) => setPptTopic(e.target.value)}
                          placeholder="e.g., Marketing Strategy for 2024..."
                          className="w-full pl-12 pr-4 py-4 bg-slate-50 border-2 border-slate-100 rounded-xl focus:border-violet-500 focus:bg-white text-lg outline-none transition-all placeholder:text-slate-400"
                        />
                      </div>
                    ) : (
                      <Textarea
                        value={pptContent}
                        onChange={(e) => setPptContent(e.target.value)}
                        placeholder="Paste your content outline here..."
                        className="min-h-[120px] bg-slate-50 border-2 border-slate-100 rounded-xl focus:border-violet-500 focus:bg-white text-base resize-none"
                      />
                    )}
                  </div>
                ) : (
                  <div className="relative group animate-in fade-in duration-300">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                      <Sparkles className="h-5 w-5 text-violet-400 group-focus-within:text-violet-600 transition-colors" />
                    </div>
                    <input
                      type="text"
                      value={prompt}
                      onChange={(e) => setPrompt(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder={
                        mode === 'research' ? "Research topic (e.g., Quantum Computing Trends)..." : 
                        mode === 'ebook' ? "E-book title (e.g., The Guide to Digital Marketing)..." :
                        "Describe your document (e.g., Resume for Senior Developer)..."
                      }
                      className="w-full pl-12 pr-32 py-4 bg-slate-50 border-2 border-slate-100 rounded-xl focus:border-violet-500 focus:bg-white text-lg outline-none transition-all placeholder:text-slate-400"
                    />
                    <button
                      onClick={() => setShowVoiceRecorder(true)}
                      className="absolute right-4 top-1/2 -translate-y-1/2 p-2 hover:bg-violet-100 rounded-lg transition-colors group"
                      title="Voice input"
                    >
                      <Mic className="w-5 h-5 text-slate-400 group-hover:text-violet-600" />
                    </button>
                  </div>
                )}

                {/* Submit Button */}
                <div className="mt-6">
                   <Button
                    onClick={handleCreatePDF}
                    disabled={isGenerating || (mode === 'ppt' && (!pptTopic && !pptContent)) || (mode !== 'ppt' && !prompt.trim())}
                    className="w-full h-14 bg-violet-600 hover:bg-violet-700 text-white rounded-xl text-lg font-semibold shadow-lg shadow-violet-500/25 transition-all transform active:scale-[0.99]"
                  >
                    {isGenerating ? (
                      <span className="flex items-center gap-2">
                        <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        Generating Magic...
                      </span>
                    ) : (
                      <span className="flex items-center gap-2">
                        Generate {mode === 'ppt' ? 'Presentation' : 'Document'} 
                        <ArrowRight className="w-5 h-5" />
                      </span>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Quick Actions Strip */}
            <div className="flex gap-4 mt-6 overflow-x-auto pb-4 no-scrollbar">
               {/* Resume Optimizer Button */}
               <button 
                  onClick={() => setShowResumeOptimizerModal(true)}
                  className="flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 rounded-lg shadow-sm hover:border-violet-300 hover:text-violet-700 transition-colors whitespace-nowrap"
                >
                  <Target className="w-4 h-4 text-violet-500" />
                  <span className="text-sm font-medium">Optimize Resume</span>
                </button>
                {examplePrompts.map((p, i) => (
                  <button 
                    key={i}
                    onClick={() => setPrompt(p.text)}
                    className="flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 rounded-lg shadow-sm hover:border-violet-300 hover:text-violet-700 transition-colors whitespace-nowrap"
                  >
                    <p.icon className="w-4 h-4 text-slate-400" />
                    <span className="text-sm font-medium text-slate-600">{p.text.split(' ').slice(0, 3).join(' ')}...</span>
                  </button>
                ))}
            </div>
          </div>
        </div>
      </div>

      {/* Trusted By Marquee */}
      <div className="border-y border-slate-200 bg-white py-12 overflow-hidden">
        <p className="text-center text-sm font-semibold text-slate-500 uppercase tracking-wider mb-8">Trusted by teams from innovative companies</p>
        <div className="relative flex overflow-x-hidden group">
          <div className="flex animate-marquee whitespace-nowrap gap-16 px-8">
            {['TechFlow', 'GlobalSync', 'InnovateLabs', 'FutureScales', 'DataMind', 'CloudPeak', 'NextGen', 'SmartSystems'].map((name, i) => (
              <span key={i} className="text-2xl font-bold text-slate-300 flex items-center gap-2">
                <div className="w-8 h-8 bg-slate-200 rounded-md" /> {name}
              </span>
            ))}
             {['TechFlow', 'GlobalSync', 'InnovateLabs', 'FutureScales', 'DataMind', 'CloudPeak', 'NextGen', 'SmartSystems'].map((name, i) => (
              <span key={`dup-${i}`} className="text-2xl font-bold text-slate-300 flex items-center gap-2">
                <div className="w-8 h-8 bg-slate-200 rounded-md" /> {name}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Features Grid */}
      <div className="py-24 px-4 bg-slate-50">
        <div className="max-w-6xl mx-auto">
           <div className="text-center mb-16 space-y-4">
             <h2 className="text-3xl md:text-5xl font-bold text-slate-900">Everything you need to create</h2>
             <p className="text-lg text-slate-600 max-w-2xl mx-auto">From simple docs to complex research papers, we've got you covered.</p>
           </div>
           
           <div className="grid md:grid-cols-3 gap-8">
              {[
                { icon: Zap, title: "Instant Generation", desc: "Turn simple prompts into full documents with proper formatting and structure in seconds.", color: "text-amber-500", bg: "bg-amber-50" },
                { icon: Search, title: "Deep Research", desc: "Powered by Perplexity, find accurate citations and sources for academic papers.", color: "text-purple-500", bg: "bg-purple-50" },
                { icon: Presentation, title: "Smart Decks", desc: "Convert text into beautiful presentation slides ready for your next meeting.", color: "text-blue-500", bg: "bg-blue-50" }
              ].map((f, i) => (
                <div key={i} className="bg-white p-8 rounded-2xl shadow-sm border border-slate-200 hover:shadow-xl hover:border-violet-100 transition-all duration-300 group">
                   <div className={`w-14 h-14 ${f.bg} rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform`}>
                      <f.icon className={`w-7 h-7 ${f.color}`} />
                   </div>
                   <h3 className="text-xl font-bold text-slate-900 mb-3">{f.title}</h3>
                   <p className="text-slate-600 leading-relaxed">{f.desc}</p>
                </div>
              ))}
           </div>
        </div>
      </div>

      {/* Use Cases Section */}
      <div className="py-24 px-4 bg-white border-y border-slate-100">
         <div className="max-w-6xl mx-auto">
            <div className="grid lg:grid-cols-2 gap-16 items-center">
               <div className="space-y-8">
                  <h2 className="text-3xl md:text-5xl font-bold text-slate-900">Tailored for your workflow</h2>
                  <div className="space-y-4">
                     {[
                       { id: 'students', icon: GraduationCap, label: 'For Students', desc: 'Create essays, research papers, and study notes 10x faster.' },
                       { id: 'business', icon: Building2, label: 'For Business', desc: 'Generate reports, proposals, and presentations instantly.' },
                       { id: 'creators', icon: PenTool, label: 'For Creators', desc: 'Write e-books and guides to grow your audience.' }
                     ].map((t) => (
                        <button
                          key={t.id}
                          onClick={() => setActiveTab(t.id)}
                          className={`w-full flex items-start text-left gap-4 p-6 rounded-xl border transition-all duration-300 ${
                            activeTab === t.id 
                            ? 'bg-violet-50 border-violet-200 shadow-md transform scale-[1.02]' 
                            : 'bg-white border-slate-100 hover:bg-slate-50'
                          }`}
                        >
                          <div className={`p-3 rounded-lg ${activeTab === t.id ? 'bg-violet-100' : 'bg-slate-100'}`}>
                             <t.icon className={`w-6 h-6 ${activeTab === t.id ? 'text-violet-600' : 'text-slate-500'}`} />
                          </div>
                          <div>
                             <h4 className={`text-lg font-bold ${activeTab === t.id ? 'text-violet-900' : 'text-slate-700'}`}>{t.label}</h4>
                             <p className="text-slate-500 mt-1">{t.desc}</p>
                          </div>
                        </button>
                     ))}
                  </div>
               </div>
               <div className="relative">
                  <div className="absolute inset-0 bg-gradient-to-tr from-violet-600/20 to-blue-500/20 rounded-3xl blur-2xl" />
                  <div className="relative bg-slate-900 rounded-2xl p-6 shadow-2xl border border-slate-800 aspect-square flex flex-col items-center justify-center text-center space-y-6">
                      <div className="w-20 h-20 bg-slate-800 rounded-full flex items-center justify-center">
                         {activeTab === 'students' && <GraduationCap className="w-10 h-10 text-violet-400" />}
                         {activeTab === 'business' && <Building2 className="w-10 h-10 text-blue-400" />}
                         {activeTab === 'creators' && <Book className="w-10 h-10 text-amber-400" />}
                      </div>
                      <div>
                         <h3 className="text-2xl font-bold text-white mb-2">
                           {activeTab === 'students' ? 'A+ Papers in Minutes' : activeTab === 'business' ? 'Close Deals Faster' : 'Publish Besellers'}
                         </h3>
                         <p className="text-slate-400 max-w-xs mx-auto">
                            Stop staring at a blank page. Let our AI handle the formatting, citations, and structure so you can focus on the ideas.
                         </p>
                      </div>
                      <div className="flex gap-2">
                         <div className="w-2 h-2 rounded-full bg-slate-700" />
                         <div className="w-2 h-2 rounded-full bg-slate-700" />
                         <div className="w-12 h-2 rounded-full bg-violet-500" />
                      </div>
                  </div>
               </div>
            </div>
         </div>
      </div>

       {/* Upgrade Modal for Pro Features */}
       {showUpgradeModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-[100] p-4 animate-in fade-in duration-200">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 relative">
            <button
              onClick={() => setShowUpgradeModal(false)}
              className="absolute top-4 right-4 text-slate-400 hover:text-slate-600 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="text-center">
              <div className="w-16 h-16 bg-violet-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Lock className="w-8 h-8 text-violet-600" />
              </div>
              <h3 className="text-2xl font-bold text-slate-900 mb-2">Unlock Pro Features</h3>
              <p className="text-slate-600 mb-6">Upgrade to access Research Mode and E-book generation.</p>
              
              <div className="space-y-4 mb-6">
                <div className="flex items-center gap-3 p-3 bg-violet-50 rounded-lg">
                  <Search className="w-5 h-5 text-violet-600" />
                  <span className="text-sm font-medium text-violet-900">Deep Research Mode</span>
                </div>
                <div className="flex items-center gap-3 p-3 bg-violet-50 rounded-lg">
                  <Book className="w-5 h-5 text-violet-600" />
                  <span className="text-sm font-medium text-violet-900">Unlimited E-books</span>
                </div>
              </div>

              <Button
                onClick={() => {
                  setShowUpgradeModal(false);
                  navigate('/pricing');
                }}
                className="w-full bg-violet-600 hover:bg-violet-700 text-white"
              >
                Upgrade Now
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Resume Optimizer Modal */}
      {showResumeOptimizerModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-[100] p-4 animate-in fade-in duration-200">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 relative">
            <button
              onClick={() => {
                setShowResumeOptimizerModal(false);
                setResumeFile(null);
                setJobDescription('');
              }}
              className="absolute top-4 right-4 text-slate-400 hover:text-slate-600"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="text-center mb-6">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Target className="w-8 h-8 text-purple-600" />
              </div>
              <h3 className="text-2xl font-bold text-slate-900">Resume Optimizer</h3>
              <p className="text-slate-600 text-sm">Upload your resume for ATS optimization</p>
            </div>

            <div className="space-y-4">
              <div className="border-2 border-dashed border-slate-300 rounded-xl p-8 hover:bg-slate-50 transition-colors text-center cursor-pointer relative">
                <input
                  type="file"
                  accept=".pdf"
                  onChange={(e) => setResumeFile(e.target.files[0])}
                  className="absolute inset-0 opacity-0 cursor-pointer"
                />
                <Upload className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                <p className="text-sm text-slate-600 font-medium">{resumeFile ? resumeFile.name : 'Click to upload PDF'}</p>
              </div>

              <Textarea
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                placeholder="Paste job description (optional)..."
                className="bg-slate-50 border-slate-200 text-sm"
              />

              <div className="flex gap-3">
                <Button variant="outline" onClick={() => setShowResumeOptimizerModal(false)} className="flex-1">Cancel</Button>
                <Button 
                  onClick={handleOptimizeResume} 
                  disabled={!resumeFile || optimizerLoading} 
                  className="flex-1 bg-purple-600 hover:bg-purple-700 text-white"
                >
                  {optimizerLoading ? 'Optimizing...' : 'Optimize'}
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Voice Recorder Modal */}
      {showVoiceRecorder && (
        <VoiceRecorder
          onTranscriptComplete={(text) => {
            if (mode === 'ppt') {
              if (pptInputMode === 'topic') {
                setPptTopic(text);
              } else {
                setPptContent(text);
              }
            } else {
              setPrompt(text);
            }
            setShowVoiceRecorder(false);
          }}
          onClose={() => setShowVoiceRecorder(false)}
        />
      )}
    </div>
  );
};

export default HomePage;
