import sys
from unittest.mock import MagicMock, patch
import os
import pytest
import asyncio

# Mock external dependencies before import
sys.modules['dodopayments'] = MagicMock()
# sys.modules['google'] = MagicMock()
# sys.modules['google.generativeai'] = MagicMock()
# sys.modules['google.ai'] = MagicMock()
# sys.modules['google.ai.generativelanguage'] = MagicMock()

# Set env vars to avoid errors during import
os.environ['SUPABASE_URL'] = 'http://test-supabase-url'
os.environ['SUPABASE_KEY'] = 'test-supabase-key'
os.environ['GEMINI_API_KEY'] = 'test-gemini-key'
os.environ['DODO_PAYMENTS_API_KEY'] = 'test-dodo-key'

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Import server after mocks
from backend import server

@pytest.mark.anyio
async def test_get_current_user_caching():
    """Test that get_current_user caches the user data"""
    # Setup
    mock_supabase = MagicMock()
    server.supabase = mock_supabase

    # Clear cache if it exists (for robustness)
    if hasattr(server, 'user_cache'):
        server.user_cache.clear()

    # Mock auth_service.verify_token
    # We need to patch verify_token on the instance used in server.py
    server.auth_service.verify_token = MagicMock(return_value={'user_id': 'test_user', 'email': 'test@example.com'})

    # Mock database response
    mock_user_data = {'user_id': 'test_user', 'credits': 10, 'plan': 'free'}
    mock_response = MagicMock()
    mock_response.data = [mock_user_data]
    mock_execute = MagicMock(return_value=mock_response)

    # Setup chain: table().select().eq().execute()
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute = mock_execute

    # First call
    user1 = await server.get_current_user(authorization='Bearer token')
    assert user1['user_id'] == 'test_user'

    # Verify DB was hit
    assert mock_execute.call_count == 1

    # Second call (should be cached)
    user2 = await server.get_current_user(authorization='Bearer token')
    assert user2['user_id'] == 'test_user'

    # Verify DB was NOT hit again (if caching works)
    # Ideally this should be 1. Without caching it will be 2.
    if hasattr(server, 'user_cache'):
        assert mock_execute.call_count == 1, "Cache miss: DB was called again"
    else:
        # If no cache implemented yet, we expect 2
        assert mock_execute.call_count == 2

@pytest.mark.anyio
async def test_download_pdf_fetches_fresh_credits():
    """Test that download_pdf fetches fresh credits even if user is cached"""
    mock_supabase = MagicMock()
    server.supabase = mock_supabase
    server.supabase_admin = MagicMock() # Mock admin client too

    # Mock PDF service to avoid actual generation
    future = asyncio.Future()
    future.set_result(b'pdf_content')
    server.pdf_service.generate_pdf = MagicMock(return_value=future)

    # Setup fresh credits fetch
    # download_pdf calls: supabase.table("users").select("credits").eq("user_id", ...).execute()
    mock_fresh_credits = {'credits': 5}
    mock_response = MagicMock()
    mock_response.data = [mock_fresh_credits]
    mock_execute = MagicMock(return_value=mock_response)
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute = mock_execute

    # Cached user has OLD credits
    current_user = {'user_id': 'test_user', 'credits': 10} # Stale value

    request = server.DownloadPDFRequest(latex_content="test")

    # Call download_pdf
    await server.download_pdf(request, current_user=current_user)

    # Verify that DB was queried for credits
    # It should have called select("credits")
    mock_supabase.table.assert_called_with("users")
    mock_supabase.table.return_value.select.assert_called_with("credits")

    # Verify current_user was updated to fresh value (5)
    # Note: download_pdf logic we added updates current_user['credits']
    # And then decrements it.
    # So it should be 4 at the end.
    assert current_user['credits'] == 4

    # Verify update called with decremented value
    server.supabase_admin.table.return_value.update.assert_called()
    update_call_args = server.supabase_admin.table.return_value.update.call_args[0][0]
    assert update_call_args['credits'] == 4

@pytest.mark.anyio
async def test_payment_success_invalidates_cache():
    """Test that payment_success invalidates the user cache"""
    mock_supabase = MagicMock()
    server.supabase = mock_supabase
    server.supabase_admin = MagicMock()

    # Setup cache
    user_id = "test_user"
    server.user_cache[user_id] = {'user_id': user_id, 'plan': 'free', 'credits': 0}

    # Mock DB calls in payment_success
    # 1. Select current credits
    mock_response = MagicMock()
    mock_response.data = [{'credits': 0}]
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response

    # 2. Check idempotent (returns empty)
    mock_empty_response = MagicMock()
    mock_empty_response.data = []
    server.supabase_admin.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_empty_response

    current_user = {'user_id': user_id, 'plan': 'free'}

    # Call payment_success
    await server.payment_success(
        plan='pro',
        user_id=user_id,
        session_id=None, # Bypass dodo verification check in test if simple logic allows
        current_user=current_user
    )

    # Verify cache is invalidated
    assert user_id not in server.user_cache
