from fastapi import APIRouter
from core.supabase import get_supabase
from models.schemas import Category

router = APIRouter(prefix="/categories", tags=["Categories"])


# Default category descriptions
CATEGORY_DESCRIPTIONS = {
    "breakfast": "Start your day right with delicious breakfast recipes.",
    "lunch": "Satisfying midday meals to keep you going.",
    "dinner": "Hearty dinner recipes for the whole family.",
    "snacks": "Quick and tasty bites for any time of day.",
    "desserts": "Sweet treats and indulgent desserts.",
    "drinks": "Refreshing beverages and warm drinks.",
    "salads": "Fresh and healthy salad recipes.",
    "other": "Other delicious recipes.",
}


@router.get("/", response_model=list[Category])
async def list_categories():
    """Get all recipe categories with their recipe counts from Supabase."""
    sb = get_supabase()

    # Get all distinct categories from recipes table
    result = sb.table("recipes").select("category").execute()
    recipes = result.data or []

    # Count recipes per category
    category_counts: dict[str, int] = {}
    for r in recipes:
        cat = r.get("category", "other")
        category_counts[cat] = category_counts.get(cat, 0) + 1

    # If no recipes in DB yet, return default categories with 0 count
    if not category_counts:
        return [
            Category(name=name, description=desc, recipe_count=0)
            for name, desc in CATEGORY_DESCRIPTIONS.items()
        ]

    return [
        Category(
            name=cat,
            description=CATEGORY_DESCRIPTIONS.get(cat, f"Delicious {cat} recipes."),
            recipe_count=count,
        )
        for cat, count in sorted(category_counts.items())
    ]
