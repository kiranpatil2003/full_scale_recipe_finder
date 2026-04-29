from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from middleware.auth import get_current_user
from models.schemas import Recipe, MessageResponse, NutritionData
from core.supabase import get_supabase
from core.third_party_apis import search_all_apis, search_all_by_ingredients
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/recipes", tags=["Recipes"])


def _get_user_restrictions(uid: str) -> tuple[list[str], list[str]]:
    """Get user's allergies and dietary preferences from Supabase."""
    sb = get_supabase()

    allergy_resp = sb.table("user_allergies").select(
        "allergen"
    ).eq("user_uid", uid).execute()
    allergies = [a["allergen"] for a in (allergy_resp.data or [])]

    pref_resp = sb.table("user_dietary_preferences").select(
        "preference"
    ).eq("user_uid", uid).execute()
    preferences = [p["preference"] for p in (pref_resp.data or [])]

    return allergies, preferences


def _filter_by_restrictions(
    recipes: list[dict], allergies: list[str], preferences: list[str]
) -> list[dict]:
    """Filter out recipes that conflict with user's allergies/dietary prefs."""
    if not allergies and not preferences:
        return recipes

    filtered = []
    for recipe in recipes:
        recipe_allergens = [a.lower() for a in (recipe.get("allergens") or [])]
        recipe_ingredients = " ".join(
            i.lower() for i in (recipe.get("ingredients") or [])
        )

        # Check allergens
        skip = False
        for allergy in allergies:
            allergy_l = allergy.lower()
            if allergy_l in recipe_allergens or allergy_l in recipe_ingredients:
                skip = True
                break
        if skip:
            continue

        filtered.append(recipe)

    return filtered


def _save_recipes_to_db(recipes: list[dict]) -> list[dict]:
    """Save normalized recipes to Supabase, skip duplicates by source+external_id."""
    sb = get_supabase()
    saved = []

    for recipe in recipes:
        ext_id = recipe.get("external_id", "")
        source = recipe.get("source", "")

        if ext_id and source:
            # Check if already exists
            existing = sb.table("recipes").select("id").eq(
                "source", source
            ).eq("external_id", ext_id).execute()

            if existing.data:
                # Return existing with its DB id
                recipe["id"] = existing.data[0]["id"]
                saved.append(recipe)
                continue

        # Insert new recipe
        insert_data = {
            "name": recipe.get("name", "Unknown"),
            "description": recipe.get("description", ""),
            "category": recipe.get("category", "other"),
            "prep_time": recipe.get("prep_time", ""),
            "cook_time": recipe.get("cook_time", ""),
            "servings": recipe.get("servings", 1),
            "ingredients": recipe.get("ingredients", []),
            "instructions": recipe.get("instructions", []),
            "image_url": recipe.get("image_url"),
            "source": source,
            "external_id": ext_id,
            "allergens": recipe.get("allergens", []),
            "diet_labels": recipe.get("diet_labels", []),
        }

        result = sb.table("recipes").insert(insert_data).execute()
        if result.data:
            recipe["id"] = result.data[0]["id"]
        saved.append(recipe)

    return saved


@router.get("/", response_model=list[Recipe])
async def list_recipes(
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
    category: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    """Get recipes from Supabase, filtered by user's dietary restrictions."""
    uid = current_user["uid"]
    allergies, preferences = _get_user_restrictions(uid)

    sb = get_supabase()
    
    all_filtered = []
    current_offset = offset
    # We'll try to fetch a bit more than 'limit' to satisfy the request after filtering
    batch_size = max(limit * 2, 50) 
    max_iterations = 3

    for _ in range(max_iterations):
        query = sb.table("recipes").select("*")
        if category:
            query = query.ilike("category", category)

        # Fetch a range of recipes
        query = query.range(current_offset, current_offset + batch_size - 1).order("id", desc=True)
        result = query.execute()
        batch_recipes = result.data or []

        if not batch_recipes:
            break

        filtered_batch = _filter_by_restrictions(batch_recipes, allergies, preferences)
        
        # Add filtered results to our list
        all_filtered.extend(filtered_batch)

        current_offset += len(batch_recipes)
        
        # If we have enough or reached the end of the DB, stop
        if len(all_filtered) >= limit or len(batch_recipes) < batch_size:
            break

    return all_filtered[:limit]


@router.get("/search", response_model=list[Recipe])
async def search_recipes(
    q: str = Query(..., min_length=1, description="Search query"),
    current_user: dict = Depends(get_current_user),
):
    """
    Search recipes: first checks Supabase DB, then falls back to
    third-party APIs if not enough results. New recipes are saved to DB.
    """
    uid = current_user["uid"]
    allergies, preferences = _get_user_restrictions(uid)

    sb = get_supabase()

    # Step 1: Search Supabase
    db_result = sb.table("recipes").select("*").ilike(
        "name", f"%{q}%"
    ).limit(20).execute()
    db_recipes = db_result.data or []

    # Step 2: If not enough results, fetch from third-party APIs
    if len(db_recipes) < 5:
        logger.info(f"Using third-party APIs for search query: '{q}' (DB had {len(db_recipes)} results)")
        api_recipes = await search_all_apis(q, number_per_api=5)
        if api_recipes:
            saved = _save_recipes_to_db(api_recipes)
            # Merge, avoiding duplicates
            existing_ids = {
                (r.get("source", ""), r.get("external_id", ""))
                for r in db_recipes
            }
            for recipe in saved:
                key = (recipe.get("source", ""), recipe.get("external_id", ""))
                if key not in existing_ids:
                    db_recipes.append(recipe)

    # Step 3: Filter by user restrictions
    filtered = _filter_by_restrictions(db_recipes, allergies, preferences)
    return filtered


@router.get("/search-by-ingredients", response_model=list[Recipe])
async def search_by_ingredients(
    ingredients: str = Query(
        ..., description="Comma-separated list of ingredients"
    ),
    current_user: dict = Depends(get_current_user),
):
    """Search recipes by ingredients with allergy filtering."""
    uid = current_user["uid"]
    allergies, preferences = _get_user_restrictions(uid)

    ingredient_list = [i.strip() for i in ingredients.split(",") if i.strip()]

    # Search Supabase first (using regex for ingredient matching)
    sb = get_supabase()
    db_recipes = []
    
    import re
    # Create regex patterns for the ingredients to do a case-insensitive search
    patterns = [re.compile(re.escape(ing), re.IGNORECASE) for ing in ingredient_list[:3]]
    
    # Fetch a batch of recent recipes to filter in memory
    result = sb.table("recipes").select("*").order("id", desc=True).limit(1000).execute()
    all_recipes = result.data or []
    
    for recipe in all_recipes:
        recipe_ingredients = recipe.get("ingredients", [])
        for pattern in patterns:
            if any(pattern.search(ing) for ing in recipe_ingredients):
                if recipe not in db_recipes:
                    db_recipes.append(recipe)
                break
        
        if len(db_recipes) >= 20:
            break

    # If not enough, try third-party APIs
    if len(db_recipes) < 5:
        print("it is not founded in the db using third party api")
        logger.info(f"Using third-party APIs for ingredient search: {ingredient_list} (DB had {len(db_recipes)} results)")
        api_recipes = await search_all_by_ingredients(ingredient_list)
        if api_recipes:
            saved = _save_recipes_to_db(api_recipes)
            existing_ids = {r.get("id") for r in db_recipes}
            for recipe in saved:
                if recipe.get("id") not in existing_ids:
                    db_recipes.append(recipe)

    filtered = _filter_by_restrictions(db_recipes, allergies, preferences)
    return filtered


# ─── Nutrition fields used for search-by-nutrition ─────────────────────────
_NUTRITION_FIELDS = [
    "calories_kcal", "protein_g", "fat_total_g", "carbohydrates_g",
    "fiber_g", "sugar_g", "sodium_mg", "cholesterol_mg",
    "saturated_fat_g", "potassium_mg", "calcium_mg", "iron_mg",
    "vitamin_c_mg", "vitamin_a_iu", "vitamin_d_iu", "vitamin_b12_mcg",
    "folate_mcg", "zinc_mg", "magnesium_mg", "phosphorus_mg",
]


@router.get("/search-by-nutrition", response_model=list[Recipe])
async def search_by_nutrition(
    # ── Macros ──
    min_calories_kcal: Optional[float] = Query(None), max_calories_kcal: Optional[float] = Query(None),
    min_protein_g: Optional[float] = Query(None), max_protein_g: Optional[float] = Query(None),
    min_fat_total_g: Optional[float] = Query(None), max_fat_total_g: Optional[float] = Query(None),
    min_carbohydrates_g: Optional[float] = Query(None), max_carbohydrates_g: Optional[float] = Query(None),
    # ── Sugars & Fiber ──
    min_fiber_g: Optional[float] = Query(None), max_fiber_g: Optional[float] = Query(None),
    min_sugar_g: Optional[float] = Query(None), max_sugar_g: Optional[float] = Query(None),
    # ── Vitamins ──
    min_vitamin_a_iu: Optional[float] = Query(None), max_vitamin_a_iu: Optional[float] = Query(None),
    min_vitamin_c_mg: Optional[float] = Query(None), max_vitamin_c_mg: Optional[float] = Query(None),
    min_vitamin_d_iu: Optional[float] = Query(None), max_vitamin_d_iu: Optional[float] = Query(None),
    min_vitamin_b12_mcg: Optional[float] = Query(None), max_vitamin_b12_mcg: Optional[float] = Query(None),
    min_folate_mcg: Optional[float] = Query(None), max_folate_mcg: Optional[float] = Query(None),
    # ── Minerals ──
    min_sodium_mg: Optional[float] = Query(None), max_sodium_mg: Optional[float] = Query(None),
    min_cholesterol_mg: Optional[float] = Query(None), max_cholesterol_mg: Optional[float] = Query(None),
    min_saturated_fat_g: Optional[float] = Query(None), max_saturated_fat_g: Optional[float] = Query(None),
    min_potassium_mg: Optional[float] = Query(None), max_potassium_mg: Optional[float] = Query(None),
    min_calcium_mg: Optional[float] = Query(None), max_calcium_mg: Optional[float] = Query(None),
    min_iron_mg: Optional[float] = Query(None), max_iron_mg: Optional[float] = Query(None),
    min_zinc_mg: Optional[float] = Query(None), max_zinc_mg: Optional[float] = Query(None),
    min_magnesium_mg: Optional[float] = Query(None), max_magnesium_mg: Optional[float] = Query(None),
    min_phosphorus_mg: Optional[float] = Query(None), max_phosphorus_mg: Optional[float] = Query(None),
    # ── Pagination ──
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: dict = Depends(get_current_user),
):
    """
    Search recipes by nutrition range filters.
    All nutrition fields are optional — only the ones provided are used as filters.
    """
    uid = current_user["uid"]
    allergies, preferences = _get_user_restrictions(uid)

    sb = get_supabase()

    # Build a dict of all provided min/max values
    locals_copy = locals()
    filters: dict[str, tuple[Optional[float], Optional[float]]] = {}
    for field in _NUTRITION_FIELDS:
        mn = locals_copy.get(f"min_{field}")
        mx = locals_copy.get(f"max_{field}")
        if mn is not None or mx is not None:
            filters[field] = (mn, mx)

    if not filters:
        raise HTTPException(
            status_code=400,
            detail="At least one nutrition filter (min or max) is required.",
        )

    # Query the nutritions table
    query = sb.table("nutritions").select("recipe_id")
    for field, (mn, mx) in filters.items():
        if mn is not None:
            query = query.gte(field, mn)
        if mx is not None:
            query = query.lte(field, mx)

    query = query.range(offset, offset + limit - 1)
    nut_result = query.execute()
    matched_ids = [row["recipe_id"] for row in (nut_result.data or [])]

    if not matched_ids:
        return []

    # Fetch the full recipe rows for the matched IDs
    recipe_result = sb.table("recipes").select("*").in_("id", matched_ids).execute()
    recipes = recipe_result.data or []

    # Apply allergy / dietary restrictions
    filtered = _filter_by_restrictions(recipes, allergies, preferences)
    return filtered


@router.get("/{recipe_id}/nutrition", response_model=NutritionData)
async def get_recipe_nutrition(
    recipe_id: int,
    current_user: dict = Depends(get_current_user),
):
    """Get nutrition data for a specific recipe."""
    sb = get_supabase()
    result = sb.table("nutritions").select("*").eq("recipe_id", recipe_id).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Nutrition data not found for this recipe.")

    return result.data[0]


@router.get("/{recipe_id}", response_model=Recipe)
async def get_recipe(
    recipe_id: int,
    current_user: dict = Depends(get_current_user),
):
    """Get a specific recipe by ID from Supabase."""
    sb = get_supabase()
    result = sb.table("recipes").select("*").eq("id", recipe_id).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Recipe not found.")

    return result.data[0]
