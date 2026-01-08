from dotenv import load_dotenv
import os
load_dotenv('.env')

key = os.environ.get('DODO_PAYMENTS_API_KEY', '')
mode = os.environ.get('PAYMENT_TEST_MODE', 'false')

print(f"KeyLength:{len(key)}")
# Only print first 5 chars to verify prefix safely
print(f"KeyPrefix:{key[:5]}")
print(f"TestModeEnv:{mode}")
