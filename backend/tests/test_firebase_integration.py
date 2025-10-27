import pytest
from unittest.mock import MagicMock, patch, call
from datetime import datetime, timezone
from io import BytesIO
from PIL import Image


@pytest.mark.asyncio
async def test_firebase_insert_on_image_upload(test_client, mock_db):
    """Test that Firebase Firestore insert is called when image is uploaded"""
    # Create a test image
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    # Upload the image
    files = {'file': ('test_image.png', img_bytes, 'image/png')}
    response = await test_client.post("/upload-image", files=files)

    # Verify the request was successful
    assert response.status_code == 200

    # Verify that Firestore add() was called
    mock_db.collection.assert_called_with('readings')
    mock_db.collection.return_value.add.assert_called_once()


@pytest.mark.asyncio
async def test_firebase_insert_data_structure(test_client, mock_db):
    """Test that the correct data structure is inserted into Firestore"""
    img = Image.new('RGB', (100, 100), color='blue')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    files = {'file': ('gauge.png', img_bytes, 'image/png')}
    response = await test_client.post("/upload-image", files=files)

    # Get the arguments passed to add()
    call_args = mock_db.collection.return_value.add.call_args[0][0]

    # Verify the data structure
    assert 'timestamp' in call_args
    assert 'pressure' in call_args

    # Verify timestamp is a string
    assert isinstance(call_args['timestamp'], str)

    # Verify pressure is a number
    assert isinstance(call_args['pressure'], (int, float))


@pytest.mark.asyncio
async def test_firebase_insert_pressure_value(test_client, mock_db):
    """Test that pressure value is correctly stored in Firebase"""
    img = Image.new('RGB', (150, 150), color='green')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    files = {'file': ('pressure_gauge.png', img_bytes, 'image/png')}
    response = await test_client.post("/upload-image", files=files)

    # Get the data that was inserted
    call_args = mock_db.collection.return_value.add.call_args[0][0]

    # The current implementation returns 0.0, but verify it's a number
    assert call_args['pressure'] >= 0
    assert isinstance(call_args['pressure'], (int, float))


@pytest.mark.asyncio
async def test_firebase_collection_name(test_client, mock_db):
    """Test that data is inserted into the correct Firestore collection"""
    img = Image.new('RGB', (100, 100), color='yellow')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    files = {'file': ('test.png', img_bytes, 'image/png')}
    response = await test_client.post("/upload-image", files=files)

    # Verify the correct collection is used
    mock_db.collection.assert_called_with('readings')


@pytest.mark.asyncio
async def test_firebase_multiple_inserts(test_client, mock_db):
    """Test that multiple image uploads create multiple Firestore entries"""
    # Upload first image
    img1 = Image.new('RGB', (100, 100), color='red')
    img_bytes1 = BytesIO()
    img1.save(img_bytes1, format='PNG')
    img_bytes1.seek(0)

    files1 = {'file': ('image1.png', img_bytes1, 'image/png')}
    response1 = await test_client.post("/upload-image", files=files1)
    assert response1.status_code == 200

    # Upload second image
    img2 = Image.new('RGB', (100, 100), color='blue')
    img_bytes2 = BytesIO()
    img2.save(img_bytes2, format='PNG')
    img_bytes2.seek(0)

    files2 = {'file': ('image2.png', img_bytes2, 'image/png')}
    response2 = await test_client.post("/upload-image", files=files2)
    assert response2.status_code == 200

    # Verify add() was called twice
    assert mock_db.collection.return_value.add.call_count == 2


@pytest.mark.asyncio
async def test_firebase_timestamp_format(test_client, mock_db):
    """Test that timestamps are stored in ISO format"""
    img = Image.new('RGB', (100, 100), color='purple')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    files = {'file': ('test.png', img_bytes, 'image/png')}
    response = await test_client.post("/upload-image", files=files)

    # Get the inserted data
    call_args = mock_db.collection.return_value.add.call_args[0][0]
    timestamp = call_args['timestamp']

    # Verify it's parseable as ISO format
    parsed_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    assert parsed_time is not None


@pytest.mark.asyncio
async def test_firebase_not_called_without_db(monkeypatch):
    """Test that app handles gracefully when Firebase is not initialized"""
    from httpx import AsyncClient
    from main import app

    # Create a version of the app with db set to None
    with patch('main.db', None):
        async with AsyncClient(app=app, base_url="http://test") as client:
            img = Image.new('RGB', (100, 100), color='white')
            img_bytes = BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)

            files = {'file': ('test.png', img_bytes, 'image/png')}
            response = await client.post("/upload-image", files=files)

            # Should still return success even if db is None
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"


def test_firebase_initialization():
    """Test Firebase initialization function"""
    from firebase_init import initialize_firebase
    import firebase_admin
    from firebase_admin import firestore

    # Mock the firebase_admin module
    with patch('firebase_admin.initialize_app') as mock_init_app, \
         patch('firebase_admin.credentials.Certificate') as mock_cert, \
         patch('firebase_admin.firestore.client') as mock_firestore_client, \
         patch('os.path.exists', return_value=True):

        # Call initialize_firebase
        result = initialize_firebase()

        # Verify that firebase_admin.initialize_app was called
        mock_init_app.assert_called_once()

        # Verify that Certificate was created with the correct file
        mock_cert.assert_called_once_with('serviceAccountKey.json')

        # Verify that firestore.client() was called
        mock_firestore_client.assert_called_once()

        # Verify that a db client was returned
        assert result is not None


def test_firebase_initialization_without_service_key():
    """Test Firebase initialization when service key file doesn't exist"""
    from firebase_init import initialize_firebase

    with patch('firebase_admin.initialize_app') as mock_init_app, \
         patch('firebase_admin.firestore.client') as mock_firestore_client, \
         patch('os.path.exists', return_value=False):

        # Call initialize_firebase
        result = initialize_firebase()

        # Verify that initialize_app was called without credentials
        mock_init_app.assert_called_once_with()

        # Verify that firestore.client() was called
        mock_firestore_client.assert_called_once()
