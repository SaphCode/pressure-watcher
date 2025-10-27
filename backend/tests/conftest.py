"""
Pytest configuration and shared fixtures for backend tests.
"""
import pytest
from httpx import AsyncClient
from unittest.mock import MagicMock, patch
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def mock_db():
    """
    Mock Firestore database client for testing.
    Returns a MagicMock that simulates Firestore operations.
    """
    mock = MagicMock()

    # Mock the collection().add() chain
    mock_collection = MagicMock()
    mock_add = MagicMock(return_value=('doc_id', 'timestamp'))
    mock_collection.add = mock_add
    mock.collection.return_value = mock_collection

    return mock


@pytest.fixture
async def test_client(mock_db):
    """
    Create a test client for the FastAPI application.
    Patches Firebase initialization to use the mock database.
    """
    # Patch firebase_admin to prevent actual initialization
    with patch('firebase_admin.initialize_app'), \
         patch('firebase_admin.credentials.Certificate'), \
         patch('firebase_admin.firestore.client', return_value=mock_db), \
         patch('firebase_init.initialize_firebase', return_value=mock_db):

        # Import the app after patching to ensure mocks are in place
        from main import app

        # Patch the db in main module to use mock
        with patch('main.db', mock_db):
            async with AsyncClient(app=app, base_url="http://test") as client:
                yield client


@pytest.fixture
def mock_firebase_init():
    """
    Mock Firebase initialization for tests that need to test
    the initialization process itself.
    """
    with patch('firebase_admin.initialize_app') as mock_init, \
         patch('firebase_admin.credentials.Certificate') as mock_cert, \
         patch('firebase_admin.firestore.client') as mock_client:
        yield {
            'init_app': mock_init,
            'certificate': mock_cert,
            'firestore_client': mock_client
        }


@pytest.fixture
def sample_image_bytes():
    """
    Provides sample image bytes for testing.
    """
    from PIL import Image
    from io import BytesIO

    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes.getvalue()
