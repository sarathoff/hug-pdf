import React, { useState } from 'react';
import { Mail, Send, User, MessageSquare, Github, ArrowRight, ExternalLink } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Label } from '../components/ui/label';

const ContactPage = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: '',
  });

  const [submitted, setSubmitted] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Form submitted:', formData);
    setSubmitted(true);
    setTimeout(() => setSubmitted(false), 3000);
  };

  const quickLinks = [
    {
      icon: Github,
      label: 'Open a GitHub issue',
      desc: 'Report bugs or request features directly on the repo.',
      href: 'https://github.com/sarathoff/hug-pdf/issues',
      external: true,
    },
    {
      icon: Mail,
      label: 'Email the creator',
      desc: 'Reach Sarath directly for partnerships or other enquiries.',
      href: 'mailto:sarathramesh.mailbox@gmail.com',
      external: false,
    },
    {
      icon: MessageSquare,
      label: 'Give feedback',
      desc: 'Your suggestions help us prioritise new features.',
      href: 'https://github.com/sarathoff/hug-pdf/discussions',
      external: true,
    },
  ];

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Hero */}
      <div className="bg-white border-b border-slate-100 py-16 px-4">
        <div className="max-w-3xl mx-auto text-center space-y-3">
          <h1 className="text-4xl font-bold text-slate-900">Get in touch</h1>
          <p className="text-lg text-slate-600">
            Have questions, feedback, or a bug to report? We'd love to hear from you.
          </p>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-4 sm:px-6 py-16">
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-10">

          {/* Left column: contact info + quick links */}
          <div className="lg:col-span-2 space-y-6">
            {/* Creator info */}
            <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-5">
              <div>
                <h2 className="text-lg font-bold text-slate-900 mb-1">Contact Information</h2>
                <p className="text-sm text-slate-500">Reach out directly via email or social media.</p>
              </div>

              <div className="flex items-start gap-3">
                <div className="p-2 bg-violet-50 rounded-lg shrink-0">
                  <Mail className="w-4 h-4 text-violet-600" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-slate-900 mb-0.5">Email</h3>
                  <a
                    href="mailto:sarathramesh.mailbox@gmail.com"
                    className="text-sm text-violet-600 hover:text-violet-700 hover:underline break-all"
                  >
                    sarathramesh.mailbox@gmail.com
                  </a>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <div className="p-2 bg-violet-50 rounded-lg shrink-0">
                  <User className="w-4 h-4 text-violet-600" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-slate-900 mb-0.5">Creator</h3>
                  <p className="text-sm text-slate-600">Sarath</p>
                  <a
                    href="https://github.com/sarathoff"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-sm text-violet-600 hover:text-violet-700 hover:underline mt-0.5"
                  >
                    <Github className="w-3.5 h-3.5" />
                    @sarathoff
                  </a>
                </div>
              </div>
            </div>

            {/* Quick links */}
            <div className="space-y-3">
              <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-widest px-1">Quick Links</h3>
              {quickLinks.map((link, i) => (
                <a
                  key={i}
                  href={link.href}
                  target={link.external ? '_blank' : undefined}
                  rel={link.external ? 'noopener noreferrer' : undefined}
                  className="flex items-start gap-3 p-4 bg-white rounded-xl border border-slate-200 shadow-sm hover:border-violet-200 hover:shadow-md transition-all duration-200 group"
                >
                  <div className="p-2 bg-slate-50 group-hover:bg-violet-50 rounded-lg shrink-0 transition-colors">
                    <link.icon className="w-4 h-4 text-slate-500 group-hover:text-violet-600 transition-colors" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-1 mb-0.5">
                      <span className="text-sm font-semibold text-slate-900">{link.label}</span>
                      {link.external && <ExternalLink className="w-3 h-3 text-slate-400" />}
                    </div>
                    <p className="text-xs text-slate-500 leading-relaxed">{link.desc}</p>
                  </div>
                </a>
              ))}
            </div>
          </div>

          {/* Right column: contact form */}
          <div className="lg:col-span-3">
            <div className="bg-white rounded-2xl border border-slate-200 p-7 shadow-sm">
              <div className="mb-6">
                <h2 className="text-lg font-bold text-slate-900 mb-1">Send a message</h2>
                <p className="text-sm text-slate-500">Fill out the form and we'll get back to you as soon as possible.</p>
              </div>

              {submitted ? (
                <div className="p-6 bg-emerald-50 border border-emerald-200 rounded-xl text-center animate-in fade-in zoom-in">
                  <div className="w-12 h-12 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-3">
                    <Send className="w-5 h-5 text-emerald-600" />
                  </div>
                  <p className="text-emerald-800 font-semibold text-lg mb-1">Message sent!</p>
                  <p className="text-emerald-600 text-sm">We'll get back to you soon.</p>
                </div>
              ) : (
                <form onSubmit={handleSubmit} className="space-y-5">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                    <div className="space-y-1.5">
                      <Label htmlFor="name" className="text-sm font-medium text-slate-700">Name</Label>
                      <Input
                        id="name"
                        name="name"
                        value={formData.name}
                        onChange={handleChange}
                        required
                        placeholder="Your name"
                        className="h-10 border-slate-200 bg-slate-50 focus:bg-white focus:border-violet-400 rounded-lg placeholder:text-slate-400"
                      />
                    </div>
                    <div className="space-y-1.5">
                      <Label htmlFor="email" className="text-sm font-medium text-slate-700">Email</Label>
                      <Input
                        type="email"
                        id="email"
                        name="email"
                        value={formData.email}
                        onChange={handleChange}
                        required
                        placeholder="your@email.com"
                        className="h-10 border-slate-200 bg-slate-50 focus:bg-white focus:border-violet-400 rounded-lg placeholder:text-slate-400"
                      />
                    </div>
                  </div>

                  <div className="space-y-1.5">
                    <Label htmlFor="subject" className="text-sm font-medium text-slate-700">Subject</Label>
                    <Input
                      id="subject"
                      name="subject"
                      value={formData.subject}
                      onChange={handleChange}
                      required
                      placeholder="How can we help?"
                      className="h-10 border-slate-200 bg-slate-50 focus:bg-white focus:border-violet-400 rounded-lg placeholder:text-slate-400"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <Label htmlFor="message" className="text-sm font-medium text-slate-700">Message</Label>
                    <Textarea
                      id="message"
                      name="message"
                      value={formData.message}
                      onChange={handleChange}
                      required
                      placeholder="Tell us what's on your mind..."
                      className="min-h-[140px] border-slate-200 bg-slate-50 focus:bg-white focus:border-violet-400 rounded-lg resize-none placeholder:text-slate-400"
                    />
                  </div>

                  <Button
                    type="submit"
                    className="w-full h-11 bg-violet-600 hover:bg-violet-700 text-white font-semibold rounded-xl shadow-sm shadow-violet-500/20 transition-all"
                  >
                    <Send className="w-4 h-4 mr-2" />
                    Send Message
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </form>
              )}
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export default ContactPage;
