import re

with open(r"d:\pdf\.env", 'r') as f:
    text = f.read()

# Find the start of SUPABASE_KEY and read until the end of the "clean" segment
match = re.search(r"SUPABASE_KEY=([^\s]+)", text)
if match:
    print(f"FULL_SUPABASE_KEY={match.group(1)}")
else:
    print("SUPABASE_KEY not found")
