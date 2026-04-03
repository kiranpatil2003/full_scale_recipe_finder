import firebase_admin
from firebase_admin import credentials
from core.config import settings
import os


def initialize_firebase():
    """Initialize Firebase Admin SDK with service account credentials."""
    if not firebase_admin._apps:
        cred_path = settings.FIREBASE_CREDENTIALS_PATH

        if not os.path.exists(cred_path):
            print(
                f"⚠️  Firebase credentials file not found at '{cred_path}'. "
                "Firebase authentication will not work. "
                "Download your service account key from Firebase Console."
            )
            return False

        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        print("✅ Firebase Admin SDK initialized successfully.")
        return True

    return True
