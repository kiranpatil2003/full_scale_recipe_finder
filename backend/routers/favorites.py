from fastapi import APIRouter, Depends, HTTPException
from middleware.auth import get_current_user
from models.schemas import MessageResponse, Recipe
from data.recipes import get_recipe_by_id

router = APIRouter(prefix="/favorites", tags=["Favorites"])

# In-memory favorites store (keyed by user UID)
# In production, replace with a database
_user_favorites: dict[str, list[int]] = {}


@router.get("/", response_model=list[Recipe])
async def get_favorites(current_user: dict = Depends(get_current_user)):
    """Get the current user's favorite recipes. Requires authentication."""
    uid = current_user["uid"]
    favorite_ids = _user_favorites.get(uid, [])
    return [
        get_recipe_by_id(rid) for rid in favorite_ids if get_recipe_by_id(rid)
    ]


@router.post("/{recipe_id}", response_model=MessageResponse)
async def add_favorite(
    recipe_id: int, current_user: dict = Depends(get_current_user)
):
    """Add a recipe to the user's favorites. Requires authentication."""
    uid = current_user["uid"]

    # Validate recipe exists
    recipe = get_recipe_by_id(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found.")

    if uid not in _user_favorites:
        _user_favorites[uid] = []

    if recipe_id in _user_favorites[uid]:
        return MessageResponse(message="Recipe is already in your favorites.")

    _user_favorites[uid].append(recipe_id)
    return MessageResponse(message=f"Added '{recipe['name']}' to favorites.")


@router.delete("/{recipe_id}", response_model=MessageResponse)
async def remove_favorite(
    recipe_id: int, current_user: dict = Depends(get_current_user)
):
    """Remove a recipe from the user's favorites. Requires authentication."""
    uid = current_user["uid"]

    if uid not in _user_favorites or recipe_id not in _user_favorites[uid]:
        raise HTTPException(
            status_code=404, detail="Recipe not found in your favorites."
        )

    _user_favorites[uid].remove(recipe_id)
    return MessageResponse(message="Recipe removed from favorites.")
