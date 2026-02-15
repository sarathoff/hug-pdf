<div align="center">
  <img src="frontend/public/logo.png" alt="HugPDF Logo" width="120" height="120">
  
  # HugPDF
  
  ### AI-Powered PDF Generation Platform
  
  [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
  [![React](https://img.shields.io/badge/React-18.x-61dafb.svg)](https://reactjs.org/)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688.svg)](https://fastapi.tiangolo.com/)
  [![Python](https://img.shields.io/badge/Python-3.11-3776ab.svg)](https://www.python.org/)
  
  [Live Demo](https://hugpdf.com) · [Documentation](./API_REFERENCE.md) · [Report Bug](https://github.com/yourusername/hugpdf/issues)
</div>

---

## 📖 About

HugPDF is a modern, AI-powered PDF generation platform that transforms natural language prompts into professionally formatted PDF documents. Built with Google's Gemini AI and LaTeX, it offers three distinct modes for different use cases: normal documents, research papers with citations, and comprehensive e-books.

### ✨ Key Features

- 🤖 **AI-Powered Generation** - Convert natural language to beautifully formatted PDFs
- 📚 **Multiple Modes** - Normal, Research (with citations), and E-book (20+ pages)
- 🔑 **Developer API** - RESTful API with comprehensive documentation
- 💳 **Credit System** - Flexible pay-per-use model
- 🎨 **Live Preview** - Real-time PDF preview with LaTeX editing
- 🔐 **Secure Authentication** - Supabase Auth with Google OAuth
- 📊 **Usage Analytics** - Track API usage and credit consumption
- 🎯 **Rate Limiting** - Tiered rate limits (Free/Pro)
- 🌐 **Responsive Design** - Works seamlessly on desktop and mobile

---

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- Supabase account
- Google Gemini API key

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/hugpdf.git
   cd hugpdf
   ```

2. **Backend Setup**

   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Frontend Setup**

   ```bash
   cd frontend
   npm install
   ```

4. **Environment Configuration**

   Create `.env` files in both `backend` and `frontend` directories:

   **Backend `.env`:**

   ```env
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_anon_key
   SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
   GEMINI_API_KEY=your_gemini_api_key
   JWT_SECRET=your_jwt_secret
   ```

   **Frontend `.env`:**

   ```env
   REACT_APP_BACKEND_URL=http://localhost:8000
   REACT_APP_SUPABASE_URL=your_supabase_url
   REACT_APP_SUPABASE_ANON_KEY=your_supabase_anon_key
   ```

5. **Database Setup**

   ```bash
   # Run SQL scripts in Supabase SQL Editor
   # 1. backend/database/schema.sql
   # 2. backend/database/api_schema.sql
   ```

6. **Run the Application**

   **Backend:**

   ```bash
   cd backend
   python -m uvicorn server:app --reload
   ```

   **Frontend:**

   ```bash
   cd frontend
   npm start
   ```

   Visit `http://localhost:3000` 🎉

---

## 🏗️ Architecture

### Tech Stack

**Frontend:**

- React 18 with React Router
- Tailwind CSS + shadcn/ui components
- Axios for API calls
- Supabase Auth

**Backend:**

- FastAPI (Python)
- Google Gemini AI
- LaTeX (pdflatex)
- Supabase (PostgreSQL)

**Infrastructure:**

- Vercel (Frontend)
- AWS ECS Fargate (Backend)
- Supabase (Database & Auth)

### Project Structure

```
hugpdf/
├── frontend/                 # React application
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/           # Page components
│   │   ├── context/         # React context (Auth)
│   │   └── lib/             # Utilities & Supabase client
│   └── public/              # Static assets
│
├── backend/                 # FastAPI application
│   ├── services/            # Business logic
│   │   ├── gemini_service.py
│   │   ├── pdf_service.py
│   │   ├── api_key_service.py
│   │   └── auth_service.py
│   ├── database/            # SQL schemas
│   ├── core/                # Dependencies & config
│   └── server.py            # Main FastAPI app
│
├── API_SETUP_GUIDE.md       # API setup documentation
├── API_REFERENCE.md         # Complete API reference
└── README.md                # This file
```

---

## 🔌 API Usage

HugPDF provides a RESTful API for programmatic PDF generation.

### Quick Example

```bash
curl -X POST https://api.hugpdf.com/api/v1/generate \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a professional resume for John Doe"}' \
  --output resume.pdf
```

### Python Example

```python
import requests

response = requests.post(
    "https://api.hugpdf.com/api/v1/generate",
    headers={"Authorization": "Bearer YOUR_API_KEY"},
    json={"prompt": "Create a research paper on AI ethics", "mode": "research"}
)

with open("paper.pdf", "wb") as f:
    f.write(response.content)
```

### Credit System

- Each PDF generation costs **1 credit**
- Credits are shared between web app and API
- Response includes `X-Credits-Remaining` header
- Purchase credits via the web interface

For complete API documentation, see [API_REFERENCE.md](./API_REFERENCE.md).

---

## 🎯 Features in Detail

### 1. Normal Mode

Generate standard documents like resumes, invoices, letters, and forms.

### 2. Research Mode (Pro)

Create research papers with:

- Web research integration (Perplexity API)
- Automatic citations
- Bibliography generation
- 10-15 pages

### 3. E-book Mode (Pro)

Generate comprehensive e-books with:

- Chapter organization
- Table of contents
- Image integration
- 20-50 pages

### 4. Developer Portal

- API key management
- Interactive documentation
- Usage analytics
- Code examples (cURL, Python, JavaScript)

---

## 🚢 Deployment

### Frontend (Vercel)

1. **Connect Repository**
   - Import project to Vercel
   - Select `frontend` as root directory

2. **Configure Build**

   ```
   Build Command: npm run build
   Output Directory: build
   Install Command: npm install
   ```

3. **Environment Variables**
   - Add all `REACT_APP_*` variables
   - Deploy!

### Backend (AWS ECS Fargate)

See [aws_deployment_steps.md](./aws_deployment_steps.md) for detailed instructions.

**Quick Steps:**

1. Build Docker image
2. Push to ECR
3. Create ECS task definition
4. Deploy to Fargate
5. Configure ALB

---

## 💳 Pricing

| Tier              | Price  | Credits | Features                       |
| ----------------- | ------ | ------- | ------------------------------ |
| **Free**          | $0     | 5       | Normal mode, 10 req/min        |
| **Credit Top-up** | $2     | 20      | All features, 100 req/min      |
| **Pro**           | $10/mo | 100     | All features, priority support |

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow existing code style
- Add tests for new features
- Update documentation
- Keep commits atomic and descriptive

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Google Gemini](https://ai.google.dev/) - AI model
- [Supabase](https://supabase.com/) - Backend infrastructure
- [shadcn/ui](https://ui.shadcn.com/) - UI components
- [FastAPI](https://fastapi.tiangolo.com/) - Backend framework
- [LaTeX](https://www.latex-project.org/) - Document typesetting

---

## 📧 Contact

- **Website:** [hugpdf.com](https://hugpdf.com)
- **Email:** support@hugpdf.com
- **GitHub:** [@yourusername](https://github.com/yourusername)
- **Twitter:** [@hugpdf](https://twitter.com/hugpdf)

---

## 🗺️ Roadmap

- [ ] Webhook support for async generation
- [ ] More document templates
- [ ] Collaborative editing
- [ ] Custom branding options
- [ ] Mobile app (iOS/Android)
- [ ] Multi-language support
- [ ] Advanced analytics dashboard

---

<div align="center">
  
  **⭐ Star this repo if you find it helpful!**
  
  Made with ❤️ by the HugPDF Team
  
</div>
