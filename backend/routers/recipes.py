from fastapi import APIRouter, HTTPException, Query
from models.schemas import Recipe
from data.recipes import RECIPES, get_recipe_by_id, search_recipes

router = APIRouter(prefix="/recipes", tags=["Recipes"])


@router.get("/", response_model=list[Recipe])
async def list_recipes():
    """Get all recipes."""
    return RECIPES


@router.get("/search", response_model=list[Recipe])
async def search(q: str = Query(..., min_length=1, description="Search query")):
    """Search recipes by name or description."""
    results = search_recipes(q)
    return results


@router.get("/{recipe_id}", response_model=Recipe)
async def get_recipe(recipe_id: int):
    """Get a specific recipe by ID."""
    recipe = get_recipe_by_id(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found.")
    return recipe
