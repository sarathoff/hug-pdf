import os

with open(r"d:\pdf\.env", 'r') as f:
    lines = f.readlines()
    
keys = ["GEMINI_API_KEY", "SUPABASE_URL", "SUPABASE_KEY", "CORS_ORIGINS", "DODO_PAYMENTS_API_KEY", "JWT_SECRET", "REACT_APP_BACKEND_URL"]
current_key = None
collected = {}

for line in lines:
    line = line.strip()
    if not line:
        continue
    
    found_key = False
    for k in keys:
        if line.startswith(f"{k}="):
            current_key = k
            collected[current_key] = line[len(k)+1:]
            found_key = True
            break
    
    if not found_key and current_key:
        # Check if this is a continuation or another key
        if "=" in line and any(line.startswith(k) for k in keys):
             parts = line.split("=", 1)
             current_key = parts[0]
             collected[current_key] = parts[1]
        else:
             collected[current_key] += line

for k, v in collected.items():
    print(f"{k}='{v.strip()}'")
