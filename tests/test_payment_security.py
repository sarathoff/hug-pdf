
import sys
import os
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

# Add backend to sys.path
sys.path.append(os.path.join(os.getcwd(), "backend"))

# Mock external dependencies BEFORE importing server
sys.modules["supabase"] = MagicMock()
sys.modules["dodopayments"] = MagicMock()
sys.modules["google.generativeai"] = MagicMock()

# Mock ALL services
for service in ["gemini_service", "pdf_service", "auth_service", "payment_service", "pexels_service", "rephrasy_service"]:
    mock_module = MagicMock()
    # Mock class name: gemini_service -> GeminiService
    class_name = "".join(x.title() for x in service.split('_'))
    setattr(mock_module, class_name, MagicMock)
    sys.modules[f"services.{service}"] = mock_module

# Set env vars
os.environ["SUPABASE_URL"] = "https://example.supabase.co"
os.environ["SUPABASE_KEY"] = "mock-key"
os.environ["GEMINI_API_KEY"] = "mock-gemini-key"
os.environ["DODO_PAYMENTS_API_KEY"] = "mock-dodo-key"
os.environ["JWT_SECRET"] = "mock-secret"
os.environ["BACKEND_URL"] = "http://test-backend"

# Import app
try:
    from server import app, get_current_user
    import server
except ImportError:
    # If running from tests/ directory, backend/ might need adjusted path or PYTHONPATH
    pass

client = TestClient(app)

# Mock user
mock_user = {
    "user_id": "test_user_123",
    "email": "test@example.com",
    "credits": 10,
    "plan": "free"
}

# Override auth dependency
app.dependency_overrides[get_current_user] = lambda: mock_user

# Mock Supabase
mock_supabase = server.supabase
server.supabase_admin = mock_supabase

def setup_mocks():
    mock_table = MagicMock()
    server.supabase.table = mock_table

    def table_side_effect(name):
        query_mock = MagicMock()
        if name == "users":
            query_mock.select.return_value.eq.return_value.execute.return_value.data = [{'credits': 10}]
            query_mock.update.return_value.eq.return_value.execute.return_value = MagicMock()
        elif name == "payment_sessions":
            query_mock.select.return_value.eq.return_value.execute.return_value.data = []
            query_mock.insert.return_value.execute.return_value = MagicMock()
        return query_mock

    mock_table.side_effect = table_side_effect

def test_payment_success_rejects_missing_session_id():
    """Verify that payment success endpoint requires session_id"""
    setup_mocks()
    response = client.post(
        "/api/payment/success",
        params={
            "plan": "pro",
            "user_id": "test_user_123"
            # session_id is MISSING
        }
    )
    assert response.status_code == 400
    assert response.json()['detail'] == "Payment session ID required"

def test_payment_success_accepts_valid_session_id():
    """Verify that payment success endpoint accepts valid session_id (test mode)"""
    setup_mocks()
    response = client.post(
        "/api/payment/success",
        params={
            "plan": "pro",
            "user_id": "test_user_123",
            "session_id": "test_session_123"
        }
    )
    assert response.status_code == 200
    assert response.json()['success'] is True
