import os

env_path = r"d:\pdf\.env"
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        print(f"Content of {env_path}:")
        print("--- START ---")
        print(f.read())
        print("--- END ---")
else:
    print(f"{env_path} does not exist")
