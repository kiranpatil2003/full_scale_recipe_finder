from fastapi import APIRouter, Depends
from middleware.auth import get_current_user
from models.schemas import UserProfile

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/verify", response_model=UserProfile)
async def verify_token(current_user: dict = Depends(get_current_user)):
    """
    Verify a Firebase ID token and return user profile info.
    Requires a valid Bearer token in the Authorization header.
    """
    return UserProfile(
        uid=current_user.get("uid", ""),
        email=current_user.get("email"),
        name=current_user.get("name"),
        picture=current_user.get("picture"),
    )
