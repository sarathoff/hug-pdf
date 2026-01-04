with open(r"d:\pdf\.env", 'r') as f:
    for i, line in enumerate(f):
        print(f"{i+1}: {repr(line)}")
