
import sys
import unittest
from unittest.mock import MagicMock, patch
import asyncio
import time

# Mock dependencies before importing server
sys.modules['supabase'] = MagicMock()
sys.modules['dodopayments'] = MagicMock()
sys.modules['services.gemini_service'] = MagicMock()
sys.modules['services.pdf_service'] = MagicMock()
sys.modules['services.auth_service'] = MagicMock()
sys.modules['services.payment_service'] = MagicMock()
sys.modules['services.pexels_service'] = MagicMock()
sys.modules['services.rephrasy_service'] = MagicMock()

# Patch environment variables to avoid import errors or side effects
with patch.dict('os.environ', {
    'SUPABASE_URL': 'http://mock-url',
    'SUPABASE_KEY': 'mock-key',
    'DODO_PAYMENTS_API_KEY': 'mock-dodo'
}):
    from server import get_current_user, supabase, auth_service, user_cache

class TestAuthPerformance(unittest.TestCase):
    def setUp(self):
        # Reset mocks
        supabase.table.reset_mock()
        auth_service.verify_token.reset_mock()

        # Setup default successful auth flow
        auth_service.verify_token.return_value = {'user_id': 'test-user-123', 'email': 'test@example.com'}

        # Mock Supabase response
        mock_response = MagicMock()
        mock_response.data = [{'user_id': 'test-user-123', 'credits': 10, 'plan': 'free'}]

        # Chain: supabase.table().select().eq().execute()
        supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response

        # Clear cache before each test
        user_cache.clear()

    def test_repeated_auth_calls_cached(self):
        """
        Verify that repeated calls to get_current_user trigger ONLY ONE DB call (cached).
        """
        async def run_calls():
            for _ in range(5):
                await get_current_user(authorization="Bearer test-token")

        asyncio.run(run_calls())

        # Check call count
        # supabase.table call count
        table_call_count = supabase.table.call_count
        print(f"Supabase table access count: {table_call_count}")

        # Assert that we are hitting the DB ONLY ONCE
        self.assertEqual(table_call_count, 1, "Expected 1 DB call for 5 auth requests with cache")

if __name__ == '__main__':
    unittest.main()
