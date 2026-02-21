// Copyright (c) 2026 HugPDF Contributors
// SPDX-License-Identifier: MIT
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Code, Copy, CheckCircle2, ChevronRight, Terminal, Zap, Lock,
  Globe, BarChart3, AlertCircle, FileText, BookOpen, ArrowRight,
  Shield, Cpu, RefreshCw
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';

const CopyButton = ({ text }) => {
  const [copied, setCopied] = useState(false);
  const handleCopy = () => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  return (
    <button
      onClick={handleCopy}
      className="absolute top-3 right-3 p-1.5 rounded-md bg-white/10 hover:bg-white/20 text-white/70 hover:text-white transition-colors"
      title="Copy to clipboard"
    >
      {copied ? <CheckCircle2 className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
    </button>
  );
};

const CodeBlock = ({ code, language = 'bash' }) => (
  <div className="relative">
    <pre className="bg-slate-900 text-slate-100 rounded-xl p-4 overflow-x-auto text-sm leading-relaxed">
      <code>{code}</code>
    </pre>
    <CopyButton text={code} />
  </div>
);

const EndpointBadge = ({ method }) => {
  const colors = {
    GET: 'bg-emerald-100 text-emerald-700 border-emerald-200',
    POST: 'bg-blue-100 text-blue-700 border-blue-200',
    DELETE: 'bg-red-100 text-red-700 border-red-200',
  };
  return (
    <span className={`inline-flex px-2 py-0.5 rounded text-xs font-bold border ${colors[method] || 'bg-gray-100 text-gray-700'}`}>
      {method}
    </span>
  );
};

const ApiDocsPage = () => {
  const [activeSection, setActiveSection] = useState('overview');

  const sections = [
    { id: 'overview', label: 'Overview', icon: Globe },
    { id: 'authentication', label: 'Authentication', icon: Lock },
    { id: 'generate', label: 'Generate PDF', icon: FileText },
    { id: 'keys', label: 'API Keys', icon: Code },
    { id: 'rate-limits', label: 'Rate Limits', icon: BarChart3 },
    { id: 'errors', label: 'Error Handling', icon: AlertCircle },
    { id: 'sdks', label: 'Code Examples', icon: Terminal },
  ];

  const scrollToSection = (id) => {
    setActiveSection(id);
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Hero Banner */}
      <div className="bg-gradient-to-br from-slate-900 via-violet-950 to-slate-900 text-white py-20 px-4">
        <div className="max-w-6xl mx-auto text-center space-y-6">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-white/10 rounded-full text-sm border border-white/20">
            <Zap className="w-4 h-4 text-yellow-400" />
            HugPDF Public API — v1.0
          </div>
          <h1 className="text-4xl md:text-6xl font-bold">
            Build with the{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-cyan-400">
              HugPDF API
            </span>
          </h1>
          <p className="text-xl text-slate-300 max-w-2xl mx-auto">
            Programmatically generate professional PDFs, research papers, and e-books
            from natural language prompts. Integrate into any workflow in minutes.
          </p>
          <div className="flex flex-wrap gap-3 justify-center">
            <Link to="/developer">
              <Button className="bg-violet-600 hover:bg-violet-500 text-white gap-2">
                Get API Key <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
            <a href="https://github.com/sarathoff/hug-pdf" target="_blank" rel="noopener noreferrer">
              <Button variant="outline" className="border-white/30 text-white hover:bg-white/10 gap-2">
                View on GitHub
              </Button>
            </a>
          </div>
          <div className="flex flex-wrap gap-6 justify-center text-sm text-slate-400 pt-4">
            <div className="flex items-center gap-2"><Shield className="w-4 h-4 text-emerald-400" /> MIT Licensed</div>
            <div className="flex items-center gap-2"><Cpu className="w-4 h-4 text-blue-400" /> Gemini AI Powered</div>
            <div className="flex items-center gap-2"><RefreshCw className="w-4 h-4 text-violet-400" /> REST API</div>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 py-12">
        <div className="flex gap-8">
          {/* Sidebar Navigation */}
          <aside className="hidden lg:block w-56 shrink-0">
            <div className="sticky top-24">
              <nav className="space-y-1">
                {sections.map((s) => (
                  <button
                    key={s.id}
                    onClick={() => scrollToSection(s.id)}
                    className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-left transition-colors ${
                      activeSection === s.id
                        ? 'bg-violet-100 text-violet-700 font-medium'
                        : 'text-slate-600 hover:bg-slate-100'
                    }`}
                  >
                    <s.icon className="w-4 h-4 shrink-0" />
                    {s.label}
                  </button>
                ))}
              </nav>
              <div className="mt-8 p-4 bg-violet-50 rounded-xl border border-violet-100">
                <p className="text-xs text-violet-700 font-medium mb-2">Need credits?</p>
                <p className="text-xs text-violet-600 mb-3">Each PDF generation uses 1 credit. Buy credits to start building.</p>
                <Link to="/pricing">
                  <Button size="sm" className="w-full bg-violet-600 hover:bg-violet-500 text-white text-xs">
                    Buy Credits
                  </Button>
                </Link>
              </div>
            </div>
          </aside>

          {/* Main Content */}
          <main className="flex-1 space-y-16 min-w-0">

            {/* Overview */}
            <section id="overview">
              <h2 className="text-2xl font-bold text-slate-900 mb-4">Overview</h2>
              <p className="text-slate-600 mb-6 leading-relaxed">
                The HugPDF API lets you generate professional PDF documents programmatically using natural language prompts.
                Perfect for automation workflows, document pipelines, and integrations with tools like Make.com, n8n, and Zapier.
              </p>

              <div className="bg-slate-900 rounded-xl p-6 mb-6">
                <p className="text-slate-400 text-sm mb-2">Base URL</p>
                <code className="text-emerald-400 text-lg font-mono">https://api.hugpdf.app/api</code>
              </div>

              <div className="grid sm:grid-cols-3 gap-4">
                {[
                  { icon: FileText, title: 'REST API', desc: 'Standard JSON requests and responses over HTTPS' },
                  { icon: Lock, title: 'API Key Auth', desc: 'Secure Bearer token authentication' },
                  { icon: BarChart3, title: 'Credit System', desc: '1 credit per PDF — buy more anytime' },
                ].map((f, i) => (
                  <div key={i} className="bg-white border border-slate-200 rounded-xl p-4">
                    <f.icon className="w-6 h-6 text-violet-600 mb-2" />
                    <h3 className="font-semibold text-slate-900 text-sm mb-1">{f.title}</h3>
                    <p className="text-xs text-slate-500">{f.desc}</p>
                  </div>
                ))}
              </div>
            </section>

            {/* Authentication */}
            <section id="authentication">
              <h2 className="text-2xl font-bold text-slate-900 mb-2">Authentication</h2>
              <p className="text-slate-600 mb-6">
                All API requests require a valid API key in the <code className="bg-slate-100 px-1.5 py-0.5 rounded text-sm font-mono">Authorization</code> header.
                Get your API key from the <Link to="/developer" className="text-violet-600 hover:underline">Developer Portal</Link>.
              </p>

              <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 mb-6">
                <div className="flex gap-2">
                  <AlertCircle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-amber-800">Keep your API key secret</p>
                    <p className="text-xs text-amber-700 mt-0.5">Never expose your API key in client-side code, public repositories, or logs.</p>
                  </div>
                </div>
              </div>

              <CodeBlock
                language="bash"
                code={`# Include your API key in every request
Authorization: Bearer pdf_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`}
              />

              <h3 className="text-lg font-semibold text-slate-900 mt-8 mb-4">Example authenticated request</h3>
              <CodeBlock
                language="bash"
                code={`curl -X POST https://api.hugpdf.app/api/v1/generate \\
  -H "Authorization: Bearer pdf_live_YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{"prompt": "Create a professional invoice for $500"}' \\
  --output invoice.pdf`}
              />
            </section>

            {/* Generate PDF */}
            <section id="generate">
              <h2 className="text-2xl font-bold text-slate-900 mb-2">Generate PDF</h2>
              <p className="text-slate-600 mb-6">Generate a PDF document from a natural language prompt.</p>

              <div className="bg-white border border-slate-200 rounded-xl p-4 mb-6">
                <div className="flex items-center gap-3">
                  <EndpointBadge method="POST" />
                  <code className="text-sm font-mono text-slate-800">/api/v1/generate</code>
                  <Badge variant="outline" className="text-xs ml-auto">1 credit</Badge>
                </div>
              </div>

              <h3 className="text-lg font-semibold text-slate-900 mb-3">Request Body</h3>
              <div className="overflow-x-auto mb-6">
                <table className="w-full text-sm border border-slate-200 rounded-xl overflow-hidden">
                  <thead className="bg-slate-50">
                    <tr>
                      <th className="text-left px-4 py-3 font-semibold text-slate-700">Parameter</th>
                      <th className="text-left px-4 py-3 font-semibold text-slate-700">Type</th>
                      <th className="text-left px-4 py-3 font-semibold text-slate-700">Required</th>
                      <th className="text-left px-4 py-3 font-semibold text-slate-700">Description</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {[
                      { param: 'prompt', type: 'string', required: 'Yes', desc: 'Natural language description of the PDF to generate' },
                      { param: 'mode', type: 'string', required: 'No', desc: 'normal | research | ebook (default: normal)' },
                      { param: 'format', type: 'string', required: 'No', desc: 'Page format: A4 | Letter (default: A4)' },
                    ].map((row) => (
                      <tr key={row.param} className="bg-white">
                        <td className="px-4 py-3 font-mono text-violet-700">{row.param}</td>
                        <td className="px-4 py-3 text-slate-500">{row.type}</td>
                        <td className="px-4 py-3">
                          <Badge variant={row.required === 'Yes' ? 'default' : 'outline'} className="text-xs">
                            {row.required}
                          </Badge>
                        </td>
                        <td className="px-4 py-3 text-slate-600">{row.desc}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <h3 className="text-lg font-semibold text-slate-900 mb-3">Generation Modes</h3>
              <div className="grid sm:grid-cols-3 gap-4 mb-6">
                {[
                  { mode: 'normal', label: 'Normal', desc: 'Standard documents up to 5 pages. Resumes, invoices, letters, reports.', color: 'bg-blue-50 border-blue-200 text-blue-700' },
                  { mode: 'research', label: 'Research', desc: 'Academic papers with citations, bibliography, and web research (10–15 pages).', color: 'bg-purple-50 border-purple-200 text-purple-700' },
                  { mode: 'ebook', label: 'E-book', desc: 'Long-form content with chapters and TOC (20–50 pages).', color: 'bg-amber-50 border-amber-200 text-amber-700' },
                ].map((m) => (
                  <div key={m.mode} className={`border rounded-xl p-4 ${m.color}`}>
                    <code className="text-xs font-bold block mb-1">{m.mode}</code>
                    <p className="text-xs font-medium mb-1">{m.label}</p>
                    <p className="text-xs opacity-80">{m.desc}</p>
                  </div>
                ))}
              </div>

              <h3 className="text-lg font-semibold text-slate-900 mb-3">Response</h3>
              <p className="text-slate-600 text-sm mb-3">Returns the PDF file as binary with response headers:</p>
              <CodeBlock
                language="bash"
                code={`Content-Type: application/pdf
Content-Disposition: attachment; filename="document_20260221_120000.pdf"
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 9
X-RateLimit-Reset: 2026-02-21T12:05:00Z
X-Credits-Remaining: 42`}
              />

              <h3 className="text-lg font-semibold text-slate-900 mt-8 mb-3">Example Request</h3>
              <CodeBlock
                language="bash"
                code={`curl -X POST https://api.hugpdf.app/api/v1/generate \\
  -H "Authorization: Bearer pdf_live_YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "prompt": "Create a professional resume for Jane Smith, senior software engineer with 8 years experience in React, Node.js, and AWS",
    "mode": "normal"
  }' \\
  --output resume.pdf`}
              />
            </section>

            {/* API Keys */}
            <section id="keys">
              <h2 className="text-2xl font-bold text-slate-900 mb-2">API Key Management</h2>
              <p className="text-slate-600 mb-6">
                Manage your API keys programmatically or via the <Link to="/developer" className="text-violet-600 hover:underline">Developer Portal</Link>.
                Key management endpoints require your Supabase JWT token.
              </p>

              {/* Create Key */}
              <div className="space-y-4 mb-8">
                <div className="bg-white border border-slate-200 rounded-xl p-4">
                  <div className="flex items-center gap-3 mb-3">
                    <EndpointBadge method="POST" />
                    <code className="text-sm font-mono text-slate-800">/api/v1/keys</code>
                    <span className="text-xs text-slate-500 ml-auto">Create API key</span>
                  </div>
                  <CodeBlock
                    language="bash"
                    code={`curl -X POST https://api.hugpdf.app/api/v1/keys \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{"name": "My Automation Bot", "tier": "free"}'`}
                  />
                </div>

                <div className="bg-white border border-slate-200 rounded-xl p-4">
                  <div className="flex items-center gap-3 mb-3">
                    <EndpointBadge method="GET" />
                    <code className="text-sm font-mono text-slate-800">/api/v1/keys</code>
                    <span className="text-xs text-slate-500 ml-auto">List all keys</span>
                  </div>
                  <CodeBlock
                    language="bash"
                    code={`curl https://api.hugpdf.app/api/v1/keys \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN"`}
                  />
                </div>

                <div className="bg-white border border-slate-200 rounded-xl p-4">
                  <div className="flex items-center gap-3 mb-3">
                    <EndpointBadge method="DELETE" />
                    <code className="text-sm font-mono text-slate-800">/api/v1/keys/{'{key_id}'}</code>
                    <span className="text-xs text-slate-500 ml-auto">Revoke key</span>
                  </div>
                  <CodeBlock
                    language="bash"
                    code={`curl -X DELETE https://api.hugpdf.app/api/v1/keys/KEY_ID \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN"`}
                  />
                </div>
              </div>
            </section>

            {/* Rate Limits */}
            <section id="rate-limits">
              <h2 className="text-2xl font-bold text-slate-900 mb-2">Rate Limits</h2>
              <p className="text-slate-600 mb-6">
                Rate limits protect the API and ensure fair usage. Limits reset on a rolling per-minute basis.
              </p>

              <div className="grid sm:grid-cols-2 gap-4 mb-6">
                {[
                  { tier: 'Free', rpm: '10 req/min', monthly: '1,000 req/month', modes: 'Normal only', color: 'border-slate-300' },
                  { tier: 'Pro', rpm: '100 req/min', monthly: '10,000 req/month', modes: 'All modes', color: 'border-violet-400 bg-violet-50' },
                ].map((t) => (
                  <div key={t.tier} className={`border ${t.color} rounded-xl p-6`}>
                    <h3 className="font-bold text-slate-900 mb-4">{t.tier} Tier</h3>
                    <ul className="space-y-2 text-sm text-slate-600">
                      <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-500" />{t.rpm}</li>
                      <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-500" />{t.monthly}</li>
                      <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-500" />{t.modes}</li>
                    </ul>
                  </div>
                ))}
              </div>

              <p className="text-sm text-slate-600 mb-3">Handle 429 responses with exponential backoff:</p>
              <CodeBlock
                language="python"
                code={`import time, requests

def generate_pdf(prompt, api_key, max_retries=3):
    for attempt in range(max_retries):
        r = requests.post(
            "https://api.hugpdf.app/api/v1/generate",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"prompt": prompt}
        )
        if r.status_code == 200:
            return r.content
        elif r.status_code == 429:
            time.sleep(2 ** attempt)  # 1s, 2s, 4s
            continue
        else:
            r.raise_for_status()
    raise Exception("Max retries exceeded")`}
              />
            </section>

            {/* Errors */}
            <section id="errors">
              <h2 className="text-2xl font-bold text-slate-900 mb-2">Error Handling</h2>
              <p className="text-slate-600 mb-6">All errors return JSON with a <code className="bg-slate-100 px-1 rounded text-sm">detail</code> field explaining the issue.</p>

              <div className="overflow-x-auto mb-6">
                <table className="w-full text-sm border border-slate-200 rounded-xl overflow-hidden">
                  <thead className="bg-slate-50">
                    <tr>
                      <th className="text-left px-4 py-3 font-semibold text-slate-700">Status</th>
                      <th className="text-left px-4 py-3 font-semibold text-slate-700">Meaning</th>
                      <th className="text-left px-4 py-3 font-semibold text-slate-700">Solution</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {[
                      { code: '200', meaning: 'Success', solution: 'PDF returned as binary' },
                      { code: '400', meaning: 'Bad Request', solution: 'Check required parameters (prompt)' },
                      { code: '401', meaning: 'Unauthorized', solution: 'Verify your API key is correct and active' },
                      { code: '402', meaning: 'Payment Required', solution: 'Purchase more credits at hugpdf.app/pricing' },
                      { code: '429', meaning: 'Rate Limited', solution: 'Wait and retry with exponential backoff' },
                      { code: '500', meaning: 'Server Error', solution: 'Simplify your prompt or contact support' },
                    ].map((row) => (
                      <tr key={row.code} className="bg-white">
                        <td className="px-4 py-3">
                          <code className={`text-sm font-bold ${row.code === '200' ? 'text-emerald-600' : row.code.startsWith('4') ? 'text-amber-600' : row.code.startsWith('5') ? 'text-red-600' : 'text-slate-600'}`}>
                            {row.code}
                          </code>
                        </td>
                        <td className="px-4 py-3 text-slate-800 font-medium">{row.meaning}</td>
                        <td className="px-4 py-3 text-slate-600">{row.solution}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <CodeBlock
                language="json"
                code={`// Error response format
{
  "detail": "Insufficient credits. Please purchase more credits to continue using the API."
}`}
              />
            </section>

            {/* Code Examples */}
            <section id="sdks">
              <h2 className="text-2xl font-bold text-slate-900 mb-2">Code Examples</h2>
              <p className="text-slate-600 mb-8">Ready-to-use examples in popular languages and frameworks.</p>

              <div className="space-y-8">
                {/* Python */}
                <div>
                  <h3 className="text-lg font-semibold text-slate-900 mb-3 flex items-center gap-2">
                    <span className="w-6 h-6 bg-blue-100 text-blue-700 rounded text-xs font-bold flex items-center justify-center">Py</span>
                    Python
                  </h3>
                  <CodeBlock
                    language="python"
                    code={`import requests

API_KEY = "pdf_live_YOUR_API_KEY"
BASE_URL = "https://api.hugpdf.app/api"

def generate_pdf(prompt: str, mode: str = "normal", output_path: str = "output.pdf"):
    """Generate a PDF using the HugPDF API."""
    response = requests.post(
        f"{BASE_URL}/v1/generate",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={"prompt": prompt, "mode": mode},
        timeout=60
    )
    response.raise_for_status()

    credits_remaining = response.headers.get("X-Credits-Remaining")
    print(f"Credits remaining: {credits_remaining}")

    with open(output_path, "wb") as f:
        f.write(response.content)
    print(f"PDF saved to {output_path}")

# Usage
generate_pdf("Create a professional invoice for consulting services, $2,500")
generate_pdf("Write a research paper on machine learning ethics", mode="research")
generate_pdf("E-book: Complete Python Programming Guide for Beginners", mode="ebook")`}
                  />
                </div>

                {/* JavaScript/Node.js */}
                <div>
                  <h3 className="text-lg font-semibold text-slate-900 mb-3 flex items-center gap-2">
                    <span className="w-6 h-6 bg-yellow-100 text-yellow-700 rounded text-xs font-bold flex items-center justify-center">JS</span>
                    JavaScript / Node.js
                  </h3>
                  <CodeBlock
                    language="javascript"
                    code={`const fs = require("fs");

const API_KEY = "pdf_live_YOUR_API_KEY";
const BASE_URL = "https://api.hugpdf.app/api";

async function generatePDF(prompt, mode = "normal", outputPath = "output.pdf") {
  const response = await fetch(\`\${BASE_URL}/v1/generate\`, {
    method: "POST",
    headers: {
      Authorization: \`Bearer \${API_KEY}\`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ prompt, mode }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(\`API Error \${response.status}: \${error.detail}\`);
  }

  const credits = response.headers.get("X-Credits-Remaining");
  console.log(\`Credits remaining: \${credits}\`);

  const buffer = Buffer.from(await response.arrayBuffer());
  fs.writeFileSync(outputPath, buffer);
  console.log(\`PDF saved to \${outputPath}\`);
}

// Usage
generatePDF("Create a professional resume for a full-stack developer")
  .then(() => console.log("Done!"))
  .catch(console.error);`}
                  />
                </div>

                {/* cURL */}
                <div>
                  <h3 className="text-lg font-semibold text-slate-900 mb-3 flex items-center gap-2">
                    <span className="w-6 h-6 bg-slate-200 text-slate-700 rounded text-xs font-bold flex items-center justify-center">$</span>
                    cURL (Shell)
                  </h3>
                  <CodeBlock
                    language="bash"
                    code={`#!/bin/bash
API_KEY="pdf_live_YOUR_API_KEY"

# Generate a normal document
curl -X POST https://api.hugpdf.app/api/v1/generate \\
  -H "Authorization: Bearer $API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{"prompt": "Create a certificate of completion for John Doe - Python Course", "mode": "normal"}' \\
  --output certificate.pdf \\
  -w "\\nStatus: %{http_code}\\n"

# Generate a research paper
curl -X POST https://api.hugpdf.app/api/v1/generate \\
  -H "Authorization: Bearer $API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{"prompt": "Research paper: The impact of large language models on software development", "mode": "research"}' \\
  --output research_paper.pdf`}
                  />
                </div>

                {/* PHP */}
                <div>
                  <h3 className="text-lg font-semibold text-slate-900 mb-3 flex items-center gap-2">
                    <span className="w-6 h-6 bg-indigo-100 text-indigo-700 rounded text-xs font-bold flex items-center justify-center">PHP</span>
                    PHP
                  </h3>
                  <CodeBlock
                    language="php"
                    code={`<?php
$apiKey = "pdf_live_YOUR_API_KEY";
$baseUrl = "https://api.hugpdf.app/api";

function generatePDF(string $prompt, string $mode = "normal", string $outputPath = "output.pdf"): void {
    global $apiKey, $baseUrl;

    $ch = curl_init("$baseUrl/v1/generate");
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_POST => true,
        CURLOPT_POSTFIELDS => json_encode(["prompt" => $prompt, "mode" => $mode]),
        CURLOPT_HTTPHEADER => [
            "Authorization: Bearer $apiKey",
            "Content-Type: application/json",
        ],
        CURLOPT_TIMEOUT => 60,
    ]);

    $response = curl_exec($ch);
    $statusCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    if ($statusCode !== 200) {
        $error = json_decode($response, true);
        throw new Exception("API Error $statusCode: " . $error["detail"]);
    }

    file_put_contents($outputPath, $response);
    echo "PDF saved to $outputPath\\n";
}

generatePDF("Create a professional business proposal for a SaaS product launch");
?>`}
                  />
                </div>
              </div>

              {/* CTA */}
              <div className="mt-12 bg-gradient-to-r from-violet-600 to-indigo-600 rounded-2xl p-8 text-white text-center">
                <h3 className="text-2xl font-bold mb-2">Ready to start building?</h3>
                <p className="text-violet-200 mb-6">Get your free API key and start generating PDFs today. No credit card required for the free tier.</p>
                <div className="flex flex-wrap gap-3 justify-center">
                  <Link to="/developer">
                    <Button className="bg-white text-violet-700 hover:bg-violet-50 gap-2">
                      Get API Key <ArrowRight className="w-4 h-4" />
                    </Button>
                  </Link>
                  <Link to="/blog">
                    <Button variant="outline" className="border-white/30 text-white hover:bg-white/10 gap-2">
                      <BookOpen className="w-4 h-4" /> Read Tutorials
                    </Button>
                  </Link>
                </div>
              </div>
            </section>
          </main>
        </div>
      </div>
    </div>
  );
};

export default ApiDocsPage;
