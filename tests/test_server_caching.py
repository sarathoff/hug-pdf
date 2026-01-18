import sys
from unittest.mock import MagicMock, patch
import pytest
from datetime import datetime, timezone
import os

# Add backend to sys.path so we can import server and services
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Mock all external dependencies BEFORE importing server
sys.modules['google'] = MagicMock()
sys.modules['google.generativeai'] = MagicMock()
sys.modules['google.ai'] = MagicMock()
sys.modules['google.ai.generativelanguage'] = MagicMock()
sys.modules['dodopayments'] = MagicMock()
sys.modules['supabase'] = MagicMock()

# Mock services modules to avoid instantiation issues
# We mock the modules themselves so the imports in server.py succeed and return mocks
sys.modules['services'] = MagicMock()
sys.modules['services.gemini_service'] = MagicMock()
sys.modules['services.pdf_service'] = MagicMock()
sys.modules['services.auth_service'] = MagicMock()
sys.modules['services.payment_service'] = MagicMock()
sys.modules['services.pexels_service'] = MagicMock()
sys.modules['services.rephrasy_service'] = MagicMock()

# Set up environment variables
os.environ['SUPABASE_URL'] = 'https://example.supabase.co'
os.environ['SUPABASE_KEY'] = 'fake-key'
os.environ['SUPABASE_SERVICE_ROLE_KEY'] = 'fake-service-key'
os.environ['JWT_SECRET'] = 'fake-jwt-secret'

# Now we can import server
import server

# Test data
TEST_USER_ID = "user-123"
TEST_TOKEN = "valid-token"
TEST_USER_DATA = {
    "user_id": TEST_USER_ID,
    "email": "test@example.com",
    "credits": 10,
    "plan": "free"
}

@pytest.fixture
def mock_supabase():
    mock = MagicMock()
    server.supabase = mock
    server.supabase_admin = mock
    server.supabase.table.reset_mock() # Reset call counts
    return mock

@pytest.fixture
def mock_auth_service():
    # Since we mocked the module services.auth_service, server.auth_service is already a Mock
    # but we want to control it easily
    mock = MagicMock()
    server.auth_service = mock
    return mock

def test_get_current_user_no_cache_initially(mock_supabase, mock_auth_service):
    """Test that the first call hits the database"""
    # Verify we can inject cache (this confirms we can modify server state for next tests)
    if hasattr(server, 'user_cache'):
        server.user_cache.clear()

    # Setup
    mock_auth_service.verify_token.return_value = {"user_id": TEST_USER_ID, "email": "test@example.com"}

    # Mock DB response
    mock_response = MagicMock()
    mock_response.data = [TEST_USER_DATA]
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response

    # Execute (need to run async function)
    import asyncio
    result = asyncio.run(server.get_current_user(f"Bearer {TEST_TOKEN}"))

    # Verify
    assert result == TEST_USER_DATA
    # Check that table("users") was called
    mock_supabase.table.assert_called_with("users")

def test_get_current_user_caching(mock_supabase, mock_auth_service):
    """Test that subsequent calls hit the cache"""
    if hasattr(server, 'user_cache'):
        server.user_cache.clear()

    # Setup
    mock_auth_service.verify_token.return_value = {"user_id": TEST_USER_ID, "email": "test@example.com"}

    # Mock DB response
    mock_response = MagicMock()
    mock_response.data = [TEST_USER_DATA]
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response

    # First call (Miss)
    import asyncio
    result1 = asyncio.run(server.get_current_user(f"Bearer {TEST_TOKEN}"))
    assert result1 == TEST_USER_DATA
    mock_supabase.table.assert_called_with("users")

    # Reset mock counts
    mock_supabase.table.reset_mock()

    # Second call (Hit)
    result2 = asyncio.run(server.get_current_user(f"Bearer {TEST_TOKEN}"))
    assert result2 == TEST_USER_DATA

    # DB should NOT be called again
    mock_supabase.table.assert_not_called()

def test_download_pdf_invalidation(mock_supabase, mock_auth_service):
    """Test that download_pdf invalidates cache"""
    if hasattr(server, 'user_cache'):
        server.user_cache.clear()

    user_id = "user-credits"
    initial_credits = 10

    mock_auth_service.verify_token.return_value = {"user_id": user_id, "email": "test@example.com"}

    # Mock DB response
    mock_response = MagicMock()
    mock_response.data = [{"user_id": user_id, "credits": initial_credits, "plan": "free"}]
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response

    # 1. Populate cache via get_current_user
    import asyncio
    asyncio.run(server.get_current_user(f"Bearer {TEST_TOKEN}"))
    assert user_id in server.user_cache
    assert server.user_cache[user_id]['credits'] == 10

    # 2. Call download_pdf
    # Mock PDFService.generate_pdf to be async
    async def async_gen_pdf(*args, **kwargs):
        return b"%PDF-1.4..."
    server.pdf_service.generate_pdf = async_gen_pdf

    request = server.DownloadPDFRequest(latex_content="test")

    # We invoke download_pdf directly with the cached user data
    cached_user = server.user_cache[user_id]

    asyncio.run(server.download_pdf(request, current_user=cached_user))

    # 3. Verify cache is invalidated
    assert user_id not in server.user_cache

def test_payment_success_invalidation(mock_supabase, mock_auth_service):
    """Test that payment_success invalidates cache"""
    if hasattr(server, 'user_cache'):
        server.user_cache.clear()

    user_id = "user-paid"

    # Configure mock side_effect to handle different tables
    mock_users_select = MagicMock()
    mock_users_select.execute.return_value.data = [{"user_id": user_id, "credits": 3, "plan": "free"}]

    mock_payment_sessions_select = MagicMock()
    mock_payment_sessions_select.execute.return_value.data = [] # Not processed yet

    def table_side_effect(name):
        mock_builder = MagicMock()
        if name == "users":
            mock_builder.select.return_value.eq.return_value = mock_users_select
            mock_builder.update.return_value.eq.return_value.execute.return_value = MagicMock(data=[{"user_id": user_id, "credits": 23}])
            mock_builder.insert.return_value.execute.return_value = MagicMock(data=[{"user_id": user_id}])
        elif name == "payment_sessions":
            mock_builder.select.return_value.eq.return_value = mock_payment_sessions_select
            mock_builder.insert.return_value.execute.return_value = MagicMock(data=[{}])
        else:
            # Fallback for other tables
            mock_builder.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
        return mock_builder

    mock_supabase.table.side_effect = table_side_effect

    # 1. Populate cache
    mock_auth_service.verify_token.return_value = {"user_id": user_id, "email": "test@example.com"}

    import asyncio
    asyncio.run(server.get_current_user(f"Bearer {TEST_TOKEN}"))
    assert user_id in server.user_cache

    # 2. Invoke payment_success
    asyncio.run(server.payment_success(
        plan="credit_topup",
        user_id=user_id,
        session_id="test_session_123", # Use test session to bypass Dodo check
        current_user={"user_id": user_id}
    ))

    # 3. Verify cache is invalidated
    assert user_id not in server.user_cache
