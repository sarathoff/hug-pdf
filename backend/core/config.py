
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent.parent.parent

# Try loading .env from multiple locations in order of preference
env_paths = [
    ROOT_DIR / '.env',
    ROOT_DIR / 'backend' / '.env',
    ROOT_DIR / 'backend' / 'services' / '.env', # Where user has it open
    ROOT_DIR / 'frontend' / '.env'
]

env_loaded = False
for path in env_paths:
    if path.exists():
        load_dotenv(path)
        print(f"Loaded environment from: {path}")
        env_loaded = True
        break

if not env_loaded:
    print("WARNING: No .env file found in common locations.")

class Settings:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    DODO_PAYMENTS_API_KEY: str = os.getenv("DODO_PAYMENTS_API_KEY")
    DODO_PAYMENTS_WEBHOOK_KEY: str = os.getenv("DODO_PAYMENTS_WEBHOOK_KEY")
    SUPABASE_URL: str = os.getenv("SUPABASE_URL")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    # Models
    # Updated based on user request and available models
    GEMINI_MODEL_STARTER: str = "gemini-3-flash-preview" 
    GEMINI_MODEL_PRO: str = "gemini-2.5-pro"
    
    # Paths
    BACKEND_DIR = ROOT_DIR / "backend"
    TEMP_UPLOADS_DIR = BACKEND_DIR / "temp_uploads"

settings = Settings()
