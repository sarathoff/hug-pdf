# PDF Generator - Quick Start Guide

## Running Locally (Without Docker)

### Prerequisites
- MongoDB must be running on `localhost:27017`
- Gemini API key from Google AI Studio

### Option 1: Using the Startup Script (Easiest)

**Backend:**
```powershell
cd d:\pdf\backend
.\start-backend.ps1
```

**Frontend:**
```powershell
cd d:\pdf\frontend
npm start
```

### Option 2: Manual Setup

**Backend:**
```powershell
cd d:\pdf\backend
.\venv\Scripts\Activate.ps1

$env:MONGO_URL="mongodb://localhost:27017/pdf_app"
$env:DB_NAME="pdf_app"
$env:GEMINI_API_KEY="your_actual_api_key_here"
$env:CORS_ORIGINS="http://localhost:3000"

uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend:**
```powershell
cd d:\pdf\frontend
npm install --legacy-peer-deps  # Only needed first time
npm start
```

---

## Installing MongoDB Locally

If you don't have MongoDB installed:

### Option 1: MongoDB Community Server
1. Download from: https://www.mongodb.com/try/download/community
2. Install with default settings
3. MongoDB will run automatically as a service

### Option 2: Use Docker for MongoDB Only
```powershell
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

---

## Running with Docker Compose (Recommended for Production-like Setup)

**Prerequisites:**
- Docker Desktop must be running

**Steps:**
1. Make sure Docker Desktop is running
2. Create `.env` file in root directory:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   ```
3. Run:
   ```powershell
   docker-compose up --build
   ```
4. Access at: http://localhost

---

## Troubleshooting

### "KeyError: 'MONGO_URL'"
- Environment variables not set
- Use the startup script or set them manually before running uvicorn

### "Cannot connect to MongoDB"
- MongoDB is not running
- Install MongoDB or use Docker
- Check if MongoDB is running: `Get-Service MongoDB` (Windows Service)

### "Docker Desktop is not running"
- Start Docker Desktop application
- Wait for it to fully start (whale icon in system tray)
- Try `docker-compose up --build` again

### Frontend dependency errors
- Always use `npm install --legacy-peer-deps`
- This handles React 19 compatibility issues

---

## Quick Access URLs

- **Frontend**: http://localhost:3000
- **Backend API Docs**: http://localhost:8000/docs
- **Backend Health**: http://localhost:8000/api/

---

## Next Steps

Once running locally, check out the deployment guides:
- [`deployment_guide.md`](file:///C:/Users/Sarath/.gemini/antigravity/brain/cc714a6e-dcee-44a9-98ad-865af414c93d/deployment_guide.md) - Deploy to internet for free
- [`walkthrough.md`](file:///C:/Users/Sarath/.gemini/antigravity/brain/cc714a6e-dcee-44a9-98ad-865af414c93d/walkthrough.md) - What was fixed and setup details
