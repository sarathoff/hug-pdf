# Deploying HugPDF to Render

This guide will help you deploy your HugPDF application to Render.

## Prerequisites

1. A Render account (free tier works)
2. Your code pushed to GitHub
3. Environment variables ready (Gemini API key, Supabase credentials, etc.)

## Backend Deployment (Web Service)

### 1. Create New Web Service

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Select the repository containing your code

### 2. Configure Service

**Basic Settings:**
- **Name**: `hugpdf-backend` (or your choice)
- **Region**: Choose closest to your users
- **Branch**: `main` (or your default branch)
- **Root Directory**: `backend`
- **Runtime**: `Python 3`

**Build & Deploy:**
- **Build Command**: `./render-build.sh`
- **Start Command**: `uvicorn server:app --host 0.0.0.0 --port $PORT`

### 3. Environment Variables

Add these in the "Environment" section:

```
GEMINI_API_KEY=your_gemini_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
DODO_PAYMENTS_API_KEY=your_dodo_key
CORS_ORIGINS=https://your-frontend-url.onrender.com
JWT_SECRET_KEY=your_secret_key_here
```

### 4. Advanced Settings

- **Auto-Deploy**: Yes (recommended)
- **Health Check Path**: `/api/`

## Frontend Deployment (Static Site)

### 1. Create New Static Site

1. Click "New +" → "Static Site"
2. Connect same GitHub repository
3. Select the repository

### 2. Configure Static Site

**Basic Settings:**
- **Name**: `hugpdf-frontend`
- **Branch**: `main`
- **Root Directory**: `frontend`

**Build Settings:**
- **Build Command**: `npm install && npm run build`
- **Publish Directory**: `build`

### 3. Environment Variables

Add this in the "Environment" section:

```
REACT_APP_BACKEND_URL=https://your-backend-url.onrender.com
```

**Important**: Replace `your-backend-url` with your actual backend URL from step 1.

## Post-Deployment Steps

### 1. Update CORS Origins

After frontend deploys, update the backend's `CORS_ORIGINS` environment variable:
```
CORS_ORIGINS=https://your-frontend-url.onrender.com,http://localhost:3000
```

### 2. Test the Application

1. Visit your frontend URL
2. Create a test document
3. Try downloading a PDF
4. Verify LaTeX compilation works

## Troubleshooting

### LaTeX Not Working

If PDF generation fails:
1. Check Render logs for LaTeX installation errors
2. Verify `render-build.sh` has execute permissions
3. Make sure the build script ran successfully

### Build Fails

- Check that `render-build.sh` is executable: `chmod +x backend/render-build.sh`
- Verify all dependencies in `requirements.txt` are compatible
- Check Render build logs for specific errors

### CORS Errors

- Ensure `CORS_ORIGINS` in backend includes your frontend URL
- Make sure frontend's `REACT_APP_BACKEND_URL` points to backend

## Free Tier Limitations

Render's free tier:
- ✅ Supports LaTeX installation
- ✅ 750 hours/month (enough for one service)
- ⚠️ Spins down after 15 minutes of inactivity
- ⚠️ Cold starts take ~30 seconds

For production, consider upgrading to paid tier for:
- No spin-down
- Faster performance
- More resources

## Notes

- First deployment takes 5-10 minutes (LaTeX installation)
- Subsequent deployments are faster (~2-3 minutes)
- LaTeX packages are cached between builds
