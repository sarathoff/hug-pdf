<div align="center">
  <img src="frontend/public/logo.png" alt="HugPDF Logo" width="120" height="120">

  # HugPDF

  ### AI-Powered PDF Generation Platform · Open Core

  [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
  [![Open Core](https://img.shields.io/badge/Model-Open%20Core-brightgreen.svg)](https://en.wikipedia.org/wiki/Open-core_model)
  [![React](https://img.shields.io/badge/React-18.x-61dafb.svg)](https://reactjs.org/)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688.svg)](https://fastapi.tiangolo.com/)
  [![Python](https://img.shields.io/badge/Python-3.11-3776ab.svg)](https://www.python.org/)

  [Live App](https://hugpdf.app) · [API Docs](https://hugpdf.app/api-docs) · [Blog](https://hugpdf.app/blog) · [Report Bug](https://github.com/sarathoff/hug-pdf/issues)
</div>

---

## What is HugPDF?

HugPDF is an **AI-powered PDF generation platform** that turns natural language prompts into professionally formatted PDF documents using Google Gemini AI and LaTeX.

This repository follows the **[Open-Core model](https://en.wikipedia.org/wiki/Open-core_model)** — the same strategy used by [Supabase](https://github.com/supabase/supabase), [Vercel](https://vercel.com/oss), and [GitLab](https://about.gitlab.com/company/stewardship/).

You can **self-host the core for free** with your own API keys, or use the **managed service at [hugpdf.app](https://hugpdf.app)** — pay only per document, no infrastructure to manage.

---

## Open-Core Model

### What's Open Source (MIT Licensed)

| Component | Description |
|---|---|
| React Frontend UI | All pages, components, layouts |
| Prompt → LaTeX Engine | Core Gemini AI integration |
| Standard PDF Templates | Normal, Research, E-book modes |
| PDF Compilation Service | LaTeX → PDF pipeline |
| API Key Management | CRUD for developer keys |
| REST API v1 | `/api/v1/generate` endpoint |
| Blog & API Docs pages | Full documentation site |

### What's Proprietary (Managed Service Only)

| Feature | Reason |
|---|---|
| Billing & Credit System | Dodo Payments integration |
| Advanced LaTeX templates | Proprietary visual quality |
| Job-description resume matching | AI pipeline |
| LinkedIn profile extraction | LinkedIn API compliance |
| High-availability infrastructure | AWS ECS + CDN |
| Priority support & SLA | Business commitment |

---

## Why use the Managed API instead of self-hosting?

Self-hosting requires: Python 3.11+, LaTeX (`texlive-full` = ~3GB), pdflatex, Google Cloud credentials, Gemini API rate limit management, Supabase migrations, CORS config, rate limiting, and server costs.

The managed API removes all of that:

```bash
# Self-host: 2+ hours setup, ongoing maintenance
# Managed: 5 minutes to your first PDF
curl -X POST https://api.hugpdf.app/api/v1/generate \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Invoice for consulting services, $2500"}' \
  --output invoice.pdf
```

**Pricing:** 3 PDFs free. Additional credits from $2. [See pricing →](https://hugpdf.app/pricing)

---

## Quick Start (Self-Hosted)

### Prerequisites

- Node.js 18+
- Python 3.11+
- LaTeX: `sudo apt install texlive-full` (Ubuntu) or `brew install --cask mactex` (macOS)
- Supabase account
- Google Gemini API key

### 1. Clone

```bash
git clone https://github.com/sarathoff/hug-pdf.git
cd hug-pdf
```

### 2. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # fill in your keys
```

### 3. Frontend

```bash
cd frontend
npm install
cp .env.example .env            # set REACT_APP_BACKEND_URL=http://localhost:8000
```

### 4. Database

Run these SQL files in your Supabase SQL Editor in order:

```
backend/database/schema.sql
backend/database/api_schema.sql
```

### 5. Run

```bash
# Terminal 1
cd backend && uvicorn server:app --reload --port 8000

# Terminal 2
cd frontend && npm start
```

Open `http://localhost:3000`

---

## Environment Variables

**`backend/.env`** (see `backend/.env.example`):

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
GEMINI_API_KEY=your_gemini_api_key
CORS_ORIGINS=http://localhost:3000
```

**`frontend/.env`** (see `frontend/.env.example`):

```env
REACT_APP_BACKEND_URL=http://localhost:8000
REACT_APP_SUPABASE_URL=https://your-project.supabase.co
REACT_APP_SUPABASE_ANON_KEY=your_supabase_anon_key
```

---

## Project Structure

```
hug-pdf/
├── frontend/                       # React 18 + Tailwind + shadcn/ui
│   └── src/
│       ├── pages/
│       │   ├── HomePage.jsx        # Landing page
│       │   ├── ApiDocsPage.jsx     # API documentation
│       │   ├── BlogPage.jsx        # Blog listing
│       │   ├── BlogPostPage.jsx    # Individual blog posts
│       │   ├── DeveloperPage.jsx   # API key management
│       │   ├── PricingPage.jsx     # Credits & billing
│       │   └── ...                 # About, Contact, Auth, etc.
│       ├── components/
│       │   ├── Header.jsx          # Navigation
│       │   ├── Footer.jsx          # Footer with open-source links
│       │   └── ...
│       └── context/AuthContext.jsx
│
├── backend/                        # FastAPI + Python 3.11
│   ├── services/
│   │   ├── gemini_service.py       # AI prompt → LaTeX
│   │   ├── pdf_service.py          # LaTeX → PDF
│   │   ├── api_key_service.py      # API key management
│   │   └── rate_limiter_service.py
│   ├── routers/ai.py               # AI generation routes
│   ├── routers/pdf.py              # PDF compilation routes
│   ├── core/config.py              # Settings
│   ├── server.py                   # FastAPI app + v1 API
│   └── .env.example
│
├── .github/
│   ├── ISSUE_TEMPLATE/             # Bug + feature templates
│   ├── workflows/ci.yml            # CI pipeline
│   └── PULL_REQUEST_TEMPLATE.md
│
├── LICENSE                         # MIT License
├── CONTRIBUTING.md                 # How to contribute
├── CODE_OF_CONDUCT.md
├── SECURITY.md                     # Vulnerability reporting
└── API_REFERENCE.md                # Full API reference
```

**Tech Stack:**
- **Frontend:** React 18, React Router v6, Tailwind CSS, shadcn/ui, Supabase Auth, Inter font
- **Backend:** FastAPI, Google Gemini 1.5 Pro, pdflatex, Supabase PostgreSQL
- **Managed Infra:** AWS ECS Fargate, CloudFront CDN, Supabase

---

## API

```bash
# Generate a PDF — 1 credit per call
curl -X POST https://api.hugpdf.app/api/v1/generate \
  -H "Authorization: Bearer pdf_live_YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Professional resume for a senior software engineer", "mode": "normal"}' \
  --output resume.pdf
```

**Modes:** `normal` (1–5 pages) · `research` (10–15 pages with citations) · `ebook` (20–50 pages)

Full reference: [hugpdf.app/api-docs](https://hugpdf.app/api-docs) · [API_REFERENCE.md](API_REFERENCE.md)

---

## Blog & Tutorials

- [Using HugPDF API on Windows](https://hugpdf.app/blog/hugpdf-api-windows)
- [Using HugPDF API on macOS](https://hugpdf.app/blog/hugpdf-api-macos)
- [Using HugPDF API on Linux](https://hugpdf.app/blog/hugpdf-api-linux)
- [Automate PDFs with Make.com](https://hugpdf.app/blog/hugpdf-make-automation)
- [Build PDF workflows with n8n](https://hugpdf.app/blog/hugpdf-n8n-workflow)
- [Connect HugPDF via Zapier](https://hugpdf.app/blog/hugpdf-zapier-automation)

---

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

```bash
git checkout -b feat/your-feature
git commit -m 'feat: describe your change'
git push origin feat/your-feature
# open a PR
```

Good first issues: prompt templates, document types, UI bugs, docs, tests.

---

## License

Copyright (c) 2026 HugPDF Contributors

The **open-source core** is released under the [MIT License](LICENSE).

The **proprietary managed service** (billing, advanced templates, enterprise infrastructure) is not covered by this license.

---

## Acknowledgments

- [Google Gemini](https://ai.google.dev/) · [Supabase](https://supabase.com/) · [shadcn/ui](https://ui.shadcn.com/) · [LaTeX Project](https://www.latex-project.org/)

---

<div align="center">
  Made with care by <a href="https://github.com/sarathoff">@sarathoff</a> and contributors<br>
  <a href="https://hugpdf.app">hugpdf.app</a> · <a href="https://github.com/sarathoff/hug-pdf">GitHub</a> · <a href="https://hugpdf.app/blog">Blog</a>
</div>
