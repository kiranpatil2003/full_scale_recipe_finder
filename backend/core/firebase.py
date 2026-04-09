import firebase_admin
from firebase_admin import credentials
from core.config import settings
import os
import json


def initialize_firebase():
    """Initialize Firebase Admin SDK with service account credentials."""
    if not firebase_admin._apps:
        # 1. Try to initialize from JSON string (Recommended for Render)
        if settings.FIREBASE_CREDENTIALS_JSON:
            try:
                # Strip potential wrapping quotes or whitespace
                json_str = settings.FIREBASE_CREDENTIALS_JSON.strip()
                if json_str.startswith("'") and json_str.endswith("'"):
                    json_str = json_str[1:-1].strip()
                
                cred_dict = json.loads(json_str)
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred)
                print("✅ Firebase Admin SDK initialized from JSON environment variable.")
                return True
            except Exception as e:
                print(f"❌ Error parsing FIREBASE_CREDENTIALS_JSON: {e}")
                # Fall through to check file path if JSON parsing fails

        # 2. Fallback to file path
        cred_path = settings.FIREBASE_CREDENTIALS_PATH

        if not os.path.exists(cred_path):
            print(
                f"⚠️  Firebase credentials not found (tried JSON env var and file at '{cred_path}'). "
                "Firebase authentication will not work."
            )
            return False

        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        print(f"✅ Firebase Admin SDK initialized from file: {cred_path}")
        return True

    return True
