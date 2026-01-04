import re

with open(r"d:\pdf\.env", 'r') as f:
    content = f.read()

# Try to find sequences that look like keys
gemini = re.search(r"GEMINI_API_KEY=([^\n\r ]+)", content)
supabase_url = re.search(r"SUPABASE_URL=(https://[^\n\r ]+)", content)
supabase_key = re.search(r"SUPABASE_KEY=([^\n\r ]+)", content)
dodo = re.search(r"DODO_PAYMENTS_API_KEY=([^\n\r ]+)", content)

print(f"GEMINI_API_KEY: {gemini.group(1) if gemini else 'Not found'}")
print(f"SUPABASE_URL: {supabase_url.group(1) if supabase_url else 'Not found'}")
print(f"SUPABASE_KEY: {supabase_key.group(1) if supabase_key else 'Not found'}")
print(f"DODO_PAYMENTS_API_KEY: {dodo.group(1) if dodo else 'Not found'}")
