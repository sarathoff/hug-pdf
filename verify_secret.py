import jwt

# Data provided by user
SUPABASE_KEY_SERVICE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imprd2dic2toZm1xaG5hbmx3bGttIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NzE2NzA3MCwiZXhwIjoyMDgyNzQzMDcwfQ.mtGIZV9XiMJoiCticeYsnDvj6fFYdgHSwqs0lZ7FtkQ"
SUPABASE_JWT_SECRET = "15dLcJ/4ErgblYMcwUoFRjHXF6ftUi3oJYKDtnMHBJ+SEba/k17xdpoma+2SdbBWNj2yyYFgcbhvUhKNtMj5Ww=="

print(f"Testing Secret: {SUPABASE_JWT_SECRET[:10]}...")

try:
    # Try decoding simply
    decoded = jwt.decode(
        SUPABASE_KEY_SERVICE,
        SUPABASE_JWT_SECRET,
        algorithms=["HS256"],
        options={"verify_aud": False}
    )
    print("SUCCESS: Secret matched! The key works.")
    print("Decoded payload:", decoded)
except jwt.InvalidSignatureError:
    print("FAILURE: Invalid Signature. The secret is WRONG.")
except Exception as e:
    print(f"FAILURE: Error: {e}")
