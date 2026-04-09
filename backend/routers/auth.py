from fastapi import APIRouter, Depends
from middleware.auth import get_current_user
from models.schemas import UserProfile
from core.supabase import get_supabase

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/verify", response_model=UserProfile)
async def verify_token(current_user: dict = Depends(get_current_user)):
    """
    Verify a Firebase ID token and upsert the user into Supabase.
    Returns the full user profile including dietary preferences and allergies.
    """
    uid = current_user.get("uid", "")
    email = current_user.get("email")
    name = current_user.get("name")
    picture = current_user.get("picture")

    sb = get_supabase()

    # Upsert user into Supabase
    user_data = {
        "uid": uid,
        "email": email,
        "display_name": name,
        "photo_url": picture,
    }

    sb.table("users").upsert(
        user_data, on_conflict="uid"
    ).execute()

    # Fetch dietary preferences
    prefs_resp = sb.table("user_dietary_preferences").select(
        "preference"
    ).eq("user_uid", uid).execute()
    dietary_preferences = [p["preference"] for p in (prefs_resp.data or [])]

    # Fetch allergies
    allergy_resp = sb.table("user_allergies").select(
        "allergen"
    ).eq("user_uid", uid).execute()
    allergies = [a["allergen"] for a in (allergy_resp.data or [])]

    return UserProfile(
        uid=uid,
        email=email,
        name=name,
        picture=picture,
        dietary_preferences=dietary_preferences,
        allergies=allergies,
    )
