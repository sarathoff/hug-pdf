import os

env_content = """GEMINI_API_KEY=AIzaSyDAglmQGxquZ8nKTonNcbu-uEtC5_bbFI0
SUPABASE_URL=https://jkwgbskhfmqhnanlwlkm.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoiYW5vbiIsImlhdCI6MTczNTU2NTAzNCwiZXhwIjoyMDUxMTQxMDM0fQ.z0W68vUgRL592VpbZrFkPXvieAtvUMcwx6
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
DODO_PAYMENTS_API_KEY=yJDdTuPxA_tvFcdy-.uWx9XvO00_091bba0fefcd4852a44cccdcf47602b5
DODO_PAYMENTS_PUBLIC_KEY=pk_snd_091bba0fefcd4852a44cccdcf47602b5
JWT_SECRET=super-secret-key-123
FRONTEND_URL=http://localhost:3000
"""

env_path = r"d:\pdf\.env"
with open(env_path, 'w') as f:
    f.write(env_content)

print(f"Successfully reconstructed {env_path}")
