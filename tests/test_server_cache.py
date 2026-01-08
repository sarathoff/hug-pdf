import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

# Mock env vars before importing server
os.environ['SUPABASE_URL'] = 'http://test.supabase.co'
os.environ['SUPABASE_KEY'] = 'test-key'
os.environ['GEMINI_API_KEY'] = 'test-key'
os.environ['DODO_PAYMENTS_API_KEY'] = 'test-key'

# Mock dependencies that might be imported at top level
sys.modules['google'] = MagicMock()
sys.modules['google.genai'] = MagicMock()
sys.modules['dodopayments'] = MagicMock()
# Mock supabase client
mock_supabase = MagicMock()
sys.modules['supabase'] = MagicMock()
sys.modules['supabase'].create_client.return_value = mock_supabase

# Now import server
from backend.server import get_current_user, user_cache, supabase

class TestUserCache(unittest.IsolatedAsyncioTestCase):
    async def test_get_current_user_caching(self):
        # Clear cache
        user_cache.clear()

        # Mock auth service
        with patch('backend.server.auth_service') as mock_auth_service:
            # Setup valid token
            token = "valid_token"
            user_id = "user_123"
            payload = {'user_id': user_id}
            mock_auth_service.verify_token.return_value = payload

            # Setup supabase response
            expected_user = {'user_id': user_id, 'email': 'test@example.com', 'credits': 10}
            mock_response = MagicMock()
            mock_response.data = [expected_user]

            # We need to mock the chain: supabase.table().select().eq().execute()
            # Since 'supabase' in server.py is a global variable, we need to mock it there
            # or ensure the imported 'supabase' is the one used.
            # In server.py: supabase = create_client(...) or None.
            # We patched the module 'supabase', but server.py imports 'create_client' and calls it.
            # Let's mock the 'supabase' object in server.py directly.

            import backend.server
            backend.server.supabase = MagicMock()
            mock_table = MagicMock()
            mock_select = MagicMock()
            mock_eq = MagicMock()

            backend.server.supabase.table.return_value = mock_table
            mock_table.select.return_value = mock_select
            mock_select.eq.return_value = mock_eq
            mock_eq.execute.return_value = mock_response

            # First call: Should hit DB
            user1 = await get_current_user(f"Bearer {token}")
            self.assertEqual(user1, expected_user)
            self.assertEqual(backend.server.supabase.table.call_count, 1)

            # Verify it's in cache
            self.assertIn(user_id, user_cache)

            # Second call: Should hit cache
            user2 = await get_current_user(f"Bearer {token}")
            self.assertEqual(user2, expected_user)
            self.assertEqual(backend.server.supabase.table.call_count, 1) # Count remains 1

            # Invalidate cache
            del user_cache[user_id]

            # Third call: Should hit DB again
            user3 = await get_current_user(f"Bearer {token}")
            self.assertEqual(user3, expected_user)
            self.assertEqual(backend.server.supabase.table.call_count, 2) # Count increases to 2

if __name__ == '__main__':
    unittest.main()
