from fastapi import APIRouter, HTTPException
from models.schemas import Category, Recipe
from data.recipes import get_all_categories, get_recipes_by_category

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("/", response_model=list[Category])
async def list_categories():
    """Get all recipe categories with their recipe counts."""
    return get_all_categories()


@router.get("/{category_name}/recipes", response_model=list[Recipe])
async def get_category_recipes(category_name: str):
    """Get all recipes in a specific category."""
    recipes = get_recipes_by_category(category_name)
    if not recipes:
        raise HTTPException(
            status_code=404,
            detail=f"No recipes found for category '{category_name}'.",
        )
    return recipes
