# Pressure Watcher - Setup Guide

## Prerequisites

- Python 3.11+
- Node.js and npm
- Firebase CLI: `npm install -g firebase-tools`
- Google Cloud account with billing enabled

## Quick Start

### 1. Firebase Project Setup

```bash
# Login to Firebase
firebase login

# Initialize Firebase project
firebase init
```

Select:
- Firestore
- Functions
- Hosting

When prompted:
- Choose "Use an existing project" or create a new one
- For Functions, select Python
- For Hosting, set public directory to `frontend`

### 2. Update Configuration Files

#### Update `.firebaserc`
Replace `your-project-id` with your actual Firebase project ID.

#### Get Firebase Web Config
1. Go to Firebase Console → Project Settings → General
2. Under "Your apps", add a web app
3. Copy the config object
4. Update `frontend/app.js` with your Firebase config
5. Uncomment the Firebase imports in `app.js`

#### Get Service Account Key
1. Go to Firebase Console → Project Settings → Service Accounts
2. Click "Generate New Private Key"
3. Save as `backend/serviceAccountKey.json`
4. **Never commit this file!**

### 3. Local Development

#### Backend
```bash
cd backend
pip install -r requirements.txt
python main.py
```

Backend runs at: `http://localhost:8080`

#### Frontend
Open `frontend/index.html` in a browser, or:
```bash
cd frontend
python -m http.server 8000
```

Frontend runs at: `http://localhost:8000`

#### Test
Open `tests/test_upload.html` in a browser to test image uploads.

### 4. Deploy to Production

```bash
# Deploy everything
firebase deploy

# Or deploy separately
firebase deploy --only hosting
firebase deploy --only functions
```

## API Usage

### Upload Image

```bash
curl -X POST http://localhost:8080/upload-image \
  -F "file=@/path/to/gauge-image.jpg"
```

### Response

```json
{
  "timestamp": "2025-10-27T12:00:00.000000",
  "pressure": 0.0,
  "image": "base64_encoded_image",
  "status": "success"
}
```

## Project Structure

```
PressureWatcher/
├── backend/
│   ├── main.py                    # FastAPI app
│   ├── firebase_init.py           # Firebase setup
│   ├── cloud_function_main.py     # Cloud Functions entry
│   └── requirements.txt           # Dependencies
├── frontend/
│   ├── index.html                 # Dashboard UI
│   ├── styles.css                 # Styles
│   └── app.js                     # Frontend logic
├── tests/
│   ├── test_upload.html          # Test UI
│   └── test_upload.js            # Test scripts
├── firebase.json                  # Firebase config
├── .firebaserc                    # Firebase project
└── .gitignore                     # Git ignore rules
```

## Notes

- The `process_pressure_gauge()` function is a placeholder - implement your image processing logic there
- Backend prints "Backend code running" when processing images
- Cloud Functions uses uvicorn to serve the FastAPI app
- Frontend uses Firestore for real-time updates (uncomment in app.js)

## Troubleshooting

### Backend won't start
- Check Python version: `python --version`
- Reinstall dependencies: `pip install -r requirements.txt`

### Firebase deploy fails
- Ensure billing is enabled on Google Cloud
- Check Firebase CLI version: `firebase --version`
- Try: `firebase login --reauth`

### Images not displaying
- Check CORS settings in `backend/main.py`
- Verify API URL in `frontend/app.js`
- Check browser console for errors
