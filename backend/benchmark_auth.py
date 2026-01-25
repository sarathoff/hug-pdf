import os
import sys
import asyncio
import time
from unittest.mock import MagicMock

# 1. Setup Environment
os.environ['GEMINI_API_KEY'] = 'dummy_key'
os.environ['SUPABASE_URL'] = 'https://dummy.supabase.co'
os.environ['SUPABASE_KEY'] = 'dummy_key'
os.environ['DODO_PAYMENTS_API_KEY'] = 'dummy_key'
os.environ['JWT_SECRET'] = 'dummy_secret'
os.environ['SUPABASE_SERVICE_ROLE_KEY'] = 'dummy_key'

# 2. Mock External Modules to avoid side effects and network calls during import
sys.modules['supabase'] = MagicMock()
sys.modules['google'] = MagicMock()
sys.modules['google.genai'] = MagicMock()
sys.modules['google.generativeai'] = MagicMock()
sys.modules['dodopayments'] = MagicMock()
sys.modules['firecrawl'] = MagicMock()

# Mock internal services that might cause trouble
# We want server to import, but we don't need real services
# services.gemini_service uses google.genai which is mocked, so it should be fine.

# Add project root to sys.path
sys.path.append(os.getcwd())

try:
    from backend import server
except ImportError as e:
    print(f"ImportError: {e}")
    # Try adding backend to path directly
    sys.path.append(os.path.join(os.getcwd(), 'backend'))
    import server

# 3. Setup Benchmark
async def benchmark():
    print("Starting benchmark for get_current_user...")

    # Mock auth_service
    server.auth_service.verify_token = MagicMock(return_value={'user_id': 'test_user', 'email': 'test@example.com'})

    # Mock Supabase behavior
    # We need to mock the chain: supabase.table().select().eq().execute()
    mock_supabase = MagicMock()
    server.supabase = mock_supabase

    mock_response = MagicMock()
    mock_response.data = [{'user_id': 'test_user', 'credits': 10, 'email': 'test@example.com', 'plan': 'free'}]

    # This function simulates the blocking nature of the real Supabase client
    def blocking_execute():
        time.sleep(0.1) # Simulate 100ms network latency
        return mock_response

    # Setup the mock chain to call blocking_execute
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = blocking_execute

    # Also mock supabase_admin for auto-create path (just in case, though we expect success path)
    server.supabase_admin = MagicMock()

    # 4. Run Benchmark
    # We run 5 concurrent requests.
    # If blocking, they will run sequentially: 5 * 0.1s = 0.5s
    # If non-blocking (asyncio.to_thread), they will run in parallel threads: ~0.1s

    start_time = time.time()

    tasks = [server.get_current_user('Bearer valid_token') for _ in range(5)]
    results = await asyncio.gather(*tasks)

    end_time = time.time()
    duration = end_time - start_time

    print(f"Total duration for 5 concurrent requests: {duration:.4f}s")

    # Verify results
    assert all(r is not None for r in results)
    assert results[0]['user_id'] == 'test_user'

    # Check if cache is working (Supabase should be called only once if cached)
    # We count calls to execute()
    execute_calls = mock_supabase.table.return_value.select.return_value.eq.return_value.execute.call_count
    print(f"Supabase execute() called {execute_calls} times")

    if duration > 0.4:
        print("Result: BLOCKING (Slow) - Optimization needed")
    elif execute_calls == 1 and duration < 0.2:
        print("Result: CACHED (Fast) - Optimization working")
    elif duration < 0.2:
         print("Result: NON-BLOCKING (Fast) - Async IO working")
    else:
        print("Result: UNKNOWN state")

if __name__ == "__main__":
    asyncio.run(benchmark())
