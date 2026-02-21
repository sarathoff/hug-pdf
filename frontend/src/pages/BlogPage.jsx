// Copyright (c) 2026 HugPDF Contributors
// SPDX-License-Identifier: MIT
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { BookOpen, Calendar, Clock, ChevronRight, Search, Tag } from 'lucide-react';

export const BLOG_POSTS = [
  {
    slug: 'hugpdf-api-windows',
    title: 'Using the HugPDF API on Windows: Complete Setup Guide',
    excerpt: 'Learn how to integrate the HugPDF API in your Windows environment using PowerShell, Python, and Node.js — with real-world automation examples.',
    category: 'Tutorial',
    tags: ['Windows', 'Python', 'PowerShell'],
    date: '2026-02-20',
    readTime: '8 min read',
    author: 'HugPDF Team',
    featured: true,
  },
  {
    slug: 'hugpdf-api-macos',
    title: 'HugPDF API on macOS: From Zero to Automated PDF Generation',
    excerpt: 'Step-by-step guide to setting up the HugPDF API on macOS with Homebrew, Python virtual environments, and shell scripts.',
    category: 'Tutorial',
    tags: ['macOS', 'Python', 'Shell'],
    date: '2026-02-19',
    readTime: '7 min read',
    author: 'HugPDF Team',
    featured: true,
  },
  {
    slug: 'hugpdf-api-linux',
    title: 'HugPDF API on Linux: Production-Ready PDF Automation',
    excerpt: 'Deploy PDF automation on Ubuntu, Debian, and other Linux distros. Includes systemd services, cron jobs, and Docker setup.',
    category: 'Tutorial',
    tags: ['Linux', 'Ubuntu', 'Docker', 'Python'],
    date: '2026-02-18',
    readTime: '10 min read',
    author: 'HugPDF Team',
    featured: true,
  },
  {
    slug: 'hugpdf-make-automation',
    title: 'Automate PDF Generation with Make.com (formerly Integromat)',
    excerpt: 'Build powerful no-code PDF automation workflows in Make.com. Create PDFs from form submissions, CRM data, spreadsheets, and more.',
    category: 'Automation',
    tags: ['Make.com', 'No-code', 'Automation'],
    date: '2026-02-17',
    readTime: '9 min read',
    author: 'HugPDF Team',
    featured: true,
  },
  {
    slug: 'hugpdf-n8n-workflow',
    title: 'Build PDF Automation Workflows with n8n',
    excerpt: 'Self-hosted automation with n8n. Create scalable PDF pipelines triggered by webhooks, databases, APIs, and scheduled tasks.',
    category: 'Automation',
    tags: ['n8n', 'Self-hosted', 'Automation', 'Webhooks'],
    date: '2026-02-16',
    readTime: '11 min read',
    author: 'HugPDF Team',
    featured: false,
  },
  {
    slug: 'hugpdf-zapier-automation',
    title: 'Connect HugPDF with 5,000+ Apps Using Zapier',
    excerpt: 'Use Zapier webhooks to trigger PDF generation from Google Forms, HubSpot, Slack, Airtable, and hundreds of other tools.',
    category: 'Automation',
    tags: ['Zapier', 'No-code', 'Integration'],
    date: '2026-02-15',
    readTime: '6 min read',
    author: 'HugPDF Team',
    featured: false,
  },
];

const CategoryBadge = ({ category }) => {
  const colors = {
    Tutorial: 'bg-blue-100 text-blue-700',
    Automation: 'bg-violet-100 text-violet-700',
    Guide: 'bg-emerald-100 text-emerald-700',
  };
  return (
    <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${colors[category] || 'bg-slate-100 text-slate-600'}`}>
      <Tag className="w-3 h-3" />
      {category}
    </span>
  );
};

const BlogPage = () => {
  const [search, setSearch] = useState('');
  const [activeFilter, setActiveFilter] = useState('All');

  const filters = ['All', 'Tutorial', 'Automation'];

  const filtered = BLOG_POSTS.filter((p) => {
    const matchSearch = p.title.toLowerCase().includes(search.toLowerCase()) ||
      p.excerpt.toLowerCase().includes(search.toLowerCase()) ||
      p.tags.some(t => t.toLowerCase().includes(search.toLowerCase()));
    const matchFilter = activeFilter === 'All' || p.category === activeFilter;
    return matchSearch && matchFilter;
  });

  const featured = filtered.filter(p => p.featured).slice(0, 3);
  const rest = filtered.filter(p => !p.featured || filtered.filter(p => p.featured).indexOf(p) >= 3);

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Hero */}
      <div className="bg-white border-b border-slate-200 py-16 px-4">
        <div className="max-w-4xl mx-auto text-center space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-violet-100 rounded-full text-sm text-violet-700 font-medium">
            <BookOpen className="w-4 h-4" />
            HugPDF Blog
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-slate-900">
            Tutorials & Automation Guides
          </h1>
          <p className="text-xl text-slate-600 max-w-2xl mx-auto">
            Learn how to integrate HugPDF into your workflows. From CLI scripts to no-code platforms.
          </p>

          {/* Search */}
          <div className="relative max-w-lg mx-auto mt-6">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              type="text"
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Search articles..."
              className="w-full pl-12 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:border-violet-400 focus:bg-white outline-none text-sm transition-colors"
            />
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 py-12">
        {/* Filters */}
        <div className="flex gap-2 mb-8">
          {filters.map(f => (
            <button
              key={f}
              onClick={() => setActiveFilter(f)}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                activeFilter === f
                  ? 'bg-violet-600 text-white'
                  : 'bg-white border border-slate-200 text-slate-600 hover:border-violet-300'
              }`}
            >
              {f}
            </button>
          ))}
        </div>

        {filtered.length === 0 ? (
          <div className="text-center py-20 text-slate-500">
            <BookOpen className="w-12 h-12 mx-auto mb-4 opacity-30" />
            <p>No articles found for "{search}"</p>
          </div>
        ) : (
          <>
            {/* Featured Posts */}
            {featured.length > 0 && (
              <div className="grid md:grid-cols-3 gap-6 mb-12">
                {featured.map((post) => (
                  <Link key={post.slug} to={`/blog/${post.slug}`} className="group">
                    <article className="bg-white border border-slate-200 rounded-2xl overflow-hidden hover:shadow-xl hover:border-violet-200 transition-all duration-300 h-full flex flex-col">
                      {/* Gradient thumbnail */}
                      <div className={`h-40 flex items-center justify-center ${
                        post.category === 'Automation'
                          ? 'bg-gradient-to-br from-violet-600 to-indigo-600'
                          : 'bg-gradient-to-br from-slate-700 to-slate-900'
                      }`}>
                        <BookOpen className="w-12 h-12 text-white/50" />
                      </div>
                      <div className="p-6 flex flex-col flex-1">
                        <div className="flex items-center gap-2 mb-3">
                          <CategoryBadge category={post.category} />
                        </div>
                        <h3 className="font-bold text-slate-900 group-hover:text-violet-700 transition-colors mb-2 leading-snug">
                          {post.title}
                        </h3>
                        <p className="text-sm text-slate-500 leading-relaxed flex-1 mb-4">{post.excerpt}</p>
                        <div className="flex items-center gap-4 text-xs text-slate-400">
                          <span className="flex items-center gap-1"><Calendar className="w-3 h-3" />{new Date(post.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</span>
                          <span className="flex items-center gap-1"><Clock className="w-3 h-3" />{post.readTime}</span>
                        </div>
                      </div>
                    </article>
                  </Link>
                ))}
              </div>
            )}

            {/* Rest of posts */}
            {rest.length > 0 && (
              <div className="space-y-4">
                <h2 className="text-lg font-semibold text-slate-700 mb-4">More Articles</h2>
                {rest.map((post) => (
                  <Link key={post.slug} to={`/blog/${post.slug}`} className="group">
                    <article className="bg-white border border-slate-200 rounded-xl p-6 hover:shadow-md hover:border-violet-200 transition-all flex gap-6 items-start">
                      <div className={`w-16 h-16 rounded-xl shrink-0 flex items-center justify-center ${
                        post.category === 'Automation' ? 'bg-violet-100' : 'bg-slate-100'
                      }`}>
                        <BookOpen className={`w-7 h-7 ${post.category === 'Automation' ? 'text-violet-500' : 'text-slate-500'}`} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <CategoryBadge category={post.category} />
                          <span className="text-xs text-slate-400">{post.readTime}</span>
                        </div>
                        <h3 className="font-bold text-slate-900 group-hover:text-violet-700 transition-colors mb-1">
                          {post.title}
                        </h3>
                        <p className="text-sm text-slate-500 line-clamp-2">{post.excerpt}</p>
                      </div>
                      <ChevronRight className="w-5 h-5 text-slate-300 group-hover:text-violet-500 transition-colors shrink-0 mt-1" />
                    </article>
                  </Link>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default BlogPage;
