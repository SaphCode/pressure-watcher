import pytest
from httpx import AsyncClient
from fastapi import status
from io import BytesIO
from PIL import Image
import base64


@pytest.mark.asyncio
async def test_upload_image_success(test_client, mock_db):
    """Test successful image upload and processing"""
    # Create a dummy image
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    # Upload the image
    files = {'file': ('test_image.png', img_bytes, 'image/png')}
    response = await test_client.post("/upload-image", files=files)

    # Assertions
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "timestamp" in data
    assert "pressure" in data
    assert "image" in data
    assert "status" in data
    assert data["status"] == "success"

    # Verify the image is returned as base64
    assert isinstance(data["image"], str)
    assert len(data["image"]) > 0

    # Verify we can decode the base64 image
    decoded_image = base64.b64decode(data["image"])
    assert len(decoded_image) > 0


@pytest.mark.asyncio
async def test_upload_image_jpeg(test_client, mock_db):
    """Test uploading a JPEG image"""
    # Create a JPEG image
    img = Image.new('RGB', (200, 200), color='blue')
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)

    files = {'file': ('test_image.jpg', img_bytes, 'image/jpeg')}
    response = await test_client.post("/upload-image", files=files)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"


@pytest.mark.asyncio
async def test_upload_image_missing_file(test_client, mock_db):
    """Test upload endpoint with missing file"""
    response = await test_client.post("/upload-image")

    # Should return 422 Unprocessable Entity for missing required field
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_upload_image_empty_file(test_client, mock_db):
    """Test upload endpoint with empty file"""
    files = {'file': ('empty.png', BytesIO(b''), 'image/png')}
    response = await test_client.post("/upload-image", files=files)

    # Should still succeed but with empty image data
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "status" in data


@pytest.mark.asyncio
async def test_upload_image_large_file(test_client, mock_db):
    """Test uploading a larger image"""
    # Create a larger image
    img = Image.new('RGB', (1920, 1080), color='green')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    files = {'file': ('large_image.png', img_bytes, 'image/png')}
    response = await test_client.post("/upload-image", files=files)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"


@pytest.mark.asyncio
async def test_upload_image_returns_pressure(test_client, mock_db):
    """Test that pressure reading is included in response"""
    img = Image.new('RGB', (100, 100), color='white')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    files = {'file': ('gauge.png', img_bytes, 'image/png')}
    response = await test_client.post("/upload-image", files=files)

    data = response.json()
    assert "pressure" in data
    assert isinstance(data["pressure"], (int, float))


@pytest.mark.asyncio
async def test_upload_image_timestamp_format(test_client, mock_db):
    """Test that timestamp is in ISO format"""
    img = Image.new('RGB', (100, 100), color='yellow')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    files = {'file': ('test.png', img_bytes, 'image/png')}
    response = await test_client.post("/upload-image", files=files)

    data = response.json()
    assert "timestamp" in data

    # Verify timestamp format (ISO 8601)
    from datetime import datetime
    timestamp = data["timestamp"]
    # Should be parseable as ISO format
    parsed_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    assert parsed_time is not None


@pytest.mark.asyncio
async def test_health_check_endpoint(test_client):
    """Test the root health check endpoint"""
    response = await test_client.get("/")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "ok"
    assert "message" in data
