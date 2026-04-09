from fastapi import APIRouter, Depends, HTTPException
from middleware.auth import get_current_user
from models.schemas import MessageResponse, Recipe
from core.supabase import get_supabase

router = APIRouter(prefix="/favorites", tags=["Favorites"])


@router.get("/", response_model=list[Recipe])
async def get_favorites(current_user: dict = Depends(get_current_user)):
    """Get the current user's favorite recipes from Supabase."""
    uid = current_user["uid"]
    sb = get_supabase()

    # Get favorite recipe IDs
    fav_resp = sb.table("user_favorites").select(
        "recipe_id"
    ).eq("user_uid", uid).execute()

    if not fav_resp.data:
        return []

    recipe_ids = [f["recipe_id"] for f in fav_resp.data]

    # Fetch full recipe data
    recipes_resp = sb.table("recipes").select("*").in_(
        "id", recipe_ids
    ).execute()

    return recipes_resp.data or []


@router.post("/{recipe_id}", response_model=MessageResponse)
async def add_favorite(
    recipe_id: int, current_user: dict = Depends(get_current_user)
):
    """Add a recipe to the user's favorites in Supabase."""
    uid = current_user["uid"]
    sb = get_supabase()

    # Validate recipe exists
    recipe_resp = sb.table("recipes").select("id, name").eq(
        "id", recipe_id
    ).execute()
    if not recipe_resp.data:
        raise HTTPException(status_code=404, detail="Recipe not found.")

    # Check if already favorited
    existing = sb.table("user_favorites").select("id").eq(
        "user_uid", uid
    ).eq("recipe_id", recipe_id).execute()

    if existing.data:
        return MessageResponse(message="Recipe is already in your favorites.")

    # Add favorite
    sb.table("user_favorites").insert({
        "user_uid": uid,
        "recipe_id": recipe_id,
    }).execute()

    recipe_name = recipe_resp.data[0].get("name", "Recipe")
    return MessageResponse(message=f"Added '{recipe_name}' to favorites.")


@router.delete("/{recipe_id}", response_model=MessageResponse)
async def remove_favorite(
    recipe_id: int, current_user: dict = Depends(get_current_user)
):
    """Remove a recipe from the user's favorites in Supabase."""
    uid = current_user["uid"]
    sb = get_supabase()

    result = sb.table("user_favorites").delete().eq(
        "user_uid", uid
    ).eq("recipe_id", recipe_id).execute()

    if not result.data:
        raise HTTPException(
            status_code=404, detail="Recipe not found in your favorites."
        )

    return MessageResponse(message="Recipe removed from favorites.")


@router.get("/check/{recipe_id}")
async def check_favorite(
    recipe_id: int, current_user: dict = Depends(get_current_user)
):
    """Check if a recipe is in the user's favorites."""
    uid = current_user["uid"]
    sb = get_supabase()

    result = sb.table("user_favorites").select("id").eq(
        "user_uid", uid
    ).eq("recipe_id", recipe_id).execute()

    return {"is_favorite": bool(result.data)}
