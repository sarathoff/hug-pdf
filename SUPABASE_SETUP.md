# Supabase Configuration Guide

## Required Environment Variables

Add these to your `.env` file in the project root (`d:\pdf\.env`):

```env
# Frontend - Supabase Client
REACT_APP_SUPABASE_URL=https://your-project.supabase.co
REACT_APP_SUPABASE_ANON_KEY=your_anon_key_here

# Backend - Supabase Service
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_service_role_key_here
SUPABASE_JWT_SECRET=your_jwt_secret_here
```

## Where to Find These Values

1. Go to [Supabase Dashboard](https://app.supabase.com)
2. Select your project
3. Go to **Settings** → **API**

- **SUPABASE_URL**: Found under "Project URL"
- **SUPABASE_ANON_KEY**: Found under "Project API keys" → "anon public"
- **SUPABASE_KEY** (service_role): Found under "Project API keys" → "service_role" (keep secret!)
- **SUPABASE_JWT_SECRET**: Found under "JWT Settings" → "JWT Secret"

## Google OAuth Setup

### 1. Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Navigate to **APIs & Services** → **Credentials**
4. Click **Create Credentials** → **OAuth 2.0 Client ID**
5. Configure OAuth consent screen if prompted
6. Select **Web application** as application type
7. Add **Authorized redirect URIs**:
   ```
   https://your-project.supabase.co/auth/v1/callback
   ```
8. Click **Create**
9. Copy the **Client ID** and **Client Secret**

### 2. Supabase Dashboard

1. Go to your Supabase project
2. Navigate to **Authentication** → **Providers**
3. Find **Google** in the list
4. Toggle **Enable Sign in with Google**
5. Paste your **Client ID** from Google
6. Paste your **Client Secret** from Google
7. Click **Save**

### 3. Add Redirect URLs

In Supabase **Authentication** → **URL Configuration**:

Add your frontend URLs:
- Development: `http://localhost:3000`
- Production: `https://your-domain.com`

## Testing the Setup

1. Restart your backend server
2. Restart your frontend development server
3. Navigate to `/auth`
4. Click "Continue with Google"
5. You should be redirected to Google's OAuth consent screen

If you see errors, check:
- Environment variables are correctly set
- Google OAuth credentials are correct
- Redirect URLs match exactly
- Supabase Google provider is enabled
