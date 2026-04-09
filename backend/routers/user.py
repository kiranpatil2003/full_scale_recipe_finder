from fastapi import APIRouter, Depends, HTTPException
from middleware.auth import get_current_user
from models.schemas import (
    UserProfile, UserProfileUpdate, DietaryPreferencesUpdate,
    AllergyAction, FCMTokenUpdate, MessageResponse,
)
from core.supabase import get_supabase

router = APIRouter(prefix="/user", tags=["User"])


@router.get("/profile", response_model=UserProfile)
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Get the current user's full profile including dietary info."""
    uid = current_user["uid"]
    sb = get_supabase()

    # Get user base info
    user_resp = sb.table("users").select("*").eq("uid", uid).execute()
    user_data = user_resp.data[0] if user_resp.data else {}

    # Get dietary preferences
    pref_resp = sb.table("user_dietary_preferences").select(
        "preference"
    ).eq("user_uid", uid).execute()
    dietary_preferences = [p["preference"] for p in (pref_resp.data or [])]

    # Get allergies
    allergy_resp = sb.table("user_allergies").select(
        "allergen"
    ).eq("user_uid", uid).execute()
    allergies = [a["allergen"] for a in (allergy_resp.data or [])]

    return UserProfile(
        uid=uid,
        email=user_data.get("email", current_user.get("email")),
        name=user_data.get("display_name", current_user.get("name")),
        picture=user_data.get("photo_url", current_user.get("picture")),
        dietary_preferences=dietary_preferences,
        allergies=allergies,
        fcm_token=user_data.get("fcm_token"),
    )


@router.put("/profile", response_model=MessageResponse)
async def update_profile(
    update: UserProfileUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Update user's display name and photo."""
    uid = current_user["uid"]
    sb = get_supabase()

    update_data = {}
    if update.name is not None:
        update_data["display_name"] = update.name
    if update.picture is not None:
        update_data["photo_url"] = update.picture

    if update_data:
        sb.table("users").update(update_data).eq("uid", uid).execute()

    return MessageResponse(message="Profile updated successfully.")


@router.put("/dietary-preferences", response_model=MessageResponse)
async def update_dietary_preferences(
    update: DietaryPreferencesUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Set/replace the user's dietary preferences."""
    uid = current_user["uid"]
    sb = get_supabase()

    # Clear existing preferences
    sb.table("user_dietary_preferences").delete().eq(
        "user_uid", uid
    ).execute()

    # Insert new preferences
    if update.preferences:
        rows = [
            {"user_uid": uid, "preference": pref}
            for pref in update.preferences
        ]
        sb.table("user_dietary_preferences").insert(rows).execute()

    return MessageResponse(
        message=f"Dietary preferences updated: {', '.join(update.preferences) if update.preferences else 'none'}"
    )


@router.get("/allergies")
async def get_allergies(current_user: dict = Depends(get_current_user)):
    """Get the user's allergy list."""
    uid = current_user["uid"]
    sb = get_supabase()

    result = sb.table("user_allergies").select(
        "allergen"
    ).eq("user_uid", uid).execute()

    return {"allergies": [a["allergen"] for a in (result.data or [])]}


@router.post("/allergies", response_model=MessageResponse)
async def add_allergy(
    action: AllergyAction,
    current_user: dict = Depends(get_current_user),
):
    """Add an allergy to the user's profile."""
    uid = current_user["uid"]
    sb = get_supabase()

    # Check if already exists
    existing = sb.table("user_allergies").select("id").eq(
        "user_uid", uid
    ).eq("allergen", action.allergen.lower()).execute()

    if existing.data:
        return MessageResponse(
            message=f"'{action.allergen}' is already in your allergy list."
        )

    sb.table("user_allergies").insert({
        "user_uid": uid,
        "allergen": action.allergen.lower(),
    }).execute()

    return MessageResponse(message=f"Added '{action.allergen}' to allergies.")


@router.delete("/allergies/{allergen}", response_model=MessageResponse)
async def remove_allergy(
    allergen: str,
    current_user: dict = Depends(get_current_user),
):
    """Remove an allergy from the user's profile."""
    uid = current_user["uid"]
    sb = get_supabase()

    result = sb.table("user_allergies").delete().eq(
        "user_uid", uid
    ).eq("allergen", allergen.lower()).execute()

    if not result.data:
        raise HTTPException(
            status_code=404,
            detail=f"Allergy '{allergen}' not found in your profile.",
        )

    return MessageResponse(message=f"Removed '{allergen}' from allergies.")


@router.put("/fcm-token", response_model=MessageResponse)
async def update_fcm_token(
    update: FCMTokenUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Save or update the user's FCM token for push notifications."""
    uid = current_user["uid"]
    sb = get_supabase()

    sb.table("users").update(
        {"fcm_token": update.token}
    ).eq("uid", uid).execute()

    return MessageResponse(message="FCM token updated.")
