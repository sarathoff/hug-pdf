import re

with open(r"d:\pdf\.env", 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

print("Searching for strings that look like part of a JWT (Base64 characters)...")
# JWTs typically have three parts separated by dots.
# Part 1: eyJ...
# Part 2: eyJ...
# Part 3: the signature

# Let's find all long strings of alphanumeric + _ + - characters
fragments = re.findall(r"[A-Za-z0-9_-]{20,}", content)
for i, frag in enumerate(fragments):
    print(f"Fragment {i}: {frag}")

# Specifically look for the eyJ prefix
parts = re.findall(r"eyJ[A-Za-z0-9._-]+", content)
for i, part in enumerate(parts):
    print(f"potential_key_part {i}: {part}")
