from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
import base64
from firebase_init import initialize_firebase
from contextlib import asynccontextmanager

# Initialize Firebase Admin SDK
db = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI application"""
    global db
    db = initialize_firebase()
    yield
    # Shutdown actions can be added here if needed

app = FastAPI(lifespan=lifespan)

# Configure CORS to allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your Firebase Hosting URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def process_pressure_gauge(image_bytes: bytes) -> float:
    """
    Placeholder function for processing the analog pressure gauge image.
    This will be implemented later with actual image processing logic.

    Args:
        image_bytes: Raw image bytes

    Returns:
        float: Pressure reading (currently returns dummy value)
    """
    print("Backend code running")
    # TODO: Implement actual image processing logic here
    # For now, return a dummy pressure value
    return 0.0


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "Pressure Watcher API is running"}


@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    """
    Endpoint to receive pressure gauge images.
    Processes the image, extracts pressure reading, and stores data.

    Args:
        file: Uploaded image file

    Returns:
        dict: Contains timestamp, pressure reading, and base64 encoded image
    """
    try:
        # Read the uploaded image
        image_bytes = await file.read()

        # Process the image to get pressure reading
        pressure_reading = process_pressure_gauge(image_bytes)

        # Get current timestamp
        timestamp = datetime.now(timezone.utc).isoformat()

        # Convert image to base64 for sending to frontend
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')

        # Store data in Firestore (will be implemented when Firebase is configured)
        if db is not None:
            db.collection('readings').add({
                'timestamp': timestamp,
                'pressure': pressure_reading
            })

        # Return data to be sent to frontend
        return {
            "timestamp": timestamp,
            "pressure": pressure_reading,
            "image": image_base64,
            "status": "success"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
