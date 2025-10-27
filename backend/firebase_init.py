import firebase_admin
from firebase_admin import credentials, firestore
import os

# Initialize Firebase Admin SDK
def initialize_firebase():
    """
    Initialize Firebase Admin SDK for backend operations.
    Looks for service account key in environment variable or file.
    """
    try:
        # For local development, use service account key file
        if os.path.exists('serviceAccountKey.json'):
            cred = credentials.Certificate('serviceAccountKey.json')
            firebase_admin.initialize_app(cred)
        # For Cloud Functions deployment, default credentials are used
        else:
            firebase_admin.initialize_app()

        # Return Firestore client
        db = firestore.client()
        print("Firebase initialized successfully")
        return db

    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        return None


def get_firestore_client():
    """Get Firestore client instance"""
    return firestore.client()
