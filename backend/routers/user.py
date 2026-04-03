from fastapi import APIRouter, Depends
from middleware.auth import get_current_user
from models.schemas import UserProfile

router = APIRouter(prefix="/user", tags=["User"])


@router.get("/profile", response_model=UserProfile)
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Get the current user's profile. Requires authentication."""
    return UserProfile(
        uid=current_user.get("uid", ""),
        email=current_user.get("email"),
        name=current_user.get("name"),
        picture=current_user.get("picture"),
    )
