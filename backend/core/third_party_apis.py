"""
Unified third-party recipe API service.
Fetches recipes from Spoonacular, TheMealDB, Edamam, and Tasty,
normalizes them into a common schema, and returns them.
"""

import httpx
from typing import Optional
from core.config import settings


# ---------------------------------------------------------------------------
# Normalizer helpers
# ---------------------------------------------------------------------------

def _normalize_spoonacular_recipe(raw: dict) -> dict:
    """Convert a Spoonacular recipe to our common schema."""
    ingredients = []
    for ing in raw.get("extendedIngredients", []):
        ingredients.append(ing.get("original", ing.get("name", "")))

    instructions_list = []
    analyzed = raw.get("analyzedInstructions", [])
    if analyzed:
        for step in analyzed[0].get("steps", []):
            instructions_list.append(step.get("step", ""))
    elif raw.get("instructions"):
        instructions_list = [raw["instructions"]]

    allergens = []
    diet_labels = []
    if raw.get("glutenFree"):
        diet_labels.append("gluten-free")
    if raw.get("dairyFree"):
        diet_labels.append("dairy-free")
        allergens.append("dairy")
    if raw.get("vegetarian"):
        diet_labels.append("vegetarian")
    if raw.get("vegan"):
        diet_labels.append("vegan")

    return {
        "name": raw.get("title", "Unknown"),
        "description": raw.get("summary", "")[:500] if raw.get("summary") else "",
        "category": _guess_category(raw.get("dishTypes", [])),
        "prep_time": f"{raw.get('preparationMinutes', 0)} min",
        "cook_time": f"{raw.get('cookingMinutes', raw.get('readyInMinutes', 0))} min",
        "servings": raw.get("servings", 1),
        "ingredients": ingredients,
        "instructions": instructions_list,
        "image_url": raw.get("image"),
        "source": "spoonacular",
        "external_id": str(raw.get("id", "")),
        "allergens": allergens,
        "diet_labels": diet_labels,
    }


def _normalize_mealdb_recipe(raw: dict) -> dict:
    """Convert a TheMealDB recipe to our common schema."""
    ingredients = []
    for i in range(1, 21):
        ing = raw.get(f"strIngredient{i}", "")
        measure = raw.get(f"strMeasure{i}", "")
        if ing and ing.strip():
            entry = f"{measure.strip()} {ing.strip()}".strip()
            ingredients.append(entry)

    instructions_text = raw.get("strInstructions", "")
    instructions = [
        s.strip()
        for s in instructions_text.split("\r\n")
        if s.strip()
    ] if instructions_text else []

    category_raw = raw.get("strCategory", "").lower()
    category_map = {
        "breakfast": "breakfast",
        "dessert": "desserts",
        "starter": "snacks",
        "side": "snacks",
        "beef": "dinner",
        "chicken": "dinner",
        "lamb": "dinner",
        "pork": "dinner",
        "seafood": "dinner",
        "pasta": "lunch",
        "vegetarian": "lunch",
        "vegan": "lunch",
        "miscellaneous": "other",
        "goat": "dinner",
    }

    return {
        "name": raw.get("strMeal", "Unknown"),
        "description": f"A delicious {raw.get('strCategory', '')} recipe from {raw.get('strArea', 'around the world')}.",
        "category": category_map.get(category_raw, "other"),
        "prep_time": "15 min",
        "cook_time": "30 min",
        "servings": 4,
        "ingredients": ingredients,
        "instructions": instructions,
        "image_url": raw.get("strMealThumb"),
        "source": "mealdb",
        "external_id": raw.get("idMeal", ""),
        "allergens": [],
        "diet_labels": ["vegetarian"] if category_raw == "vegetarian" else [],
    }


def _normalize_edamam_recipe(raw: dict) -> dict:
    """Convert an Edamam recipe hit to our common schema."""
    recipe = raw.get("recipe", raw)
    allergens = []
    caution_map = {
        "Gluten": "gluten",
        "Wheat": "wheat",
        "Eggs": "eggs",
        "Milk": "dairy",
        "Peanuts": "peanuts",
        "Tree-Nuts": "tree nuts",
        "Soy": "soy",
        "Fish": "fish",
        "Shellfish": "shellfish",
    }
    for caution in recipe.get("cautions", []):
        mapped = caution_map.get(caution, caution.lower())
        allergens.append(mapped)

    diet_labels = [l.lower() for l in recipe.get("dietLabels", [])]
    health_labels = [l.lower() for l in recipe.get("healthLabels", [])]
    diet_labels.extend(health_labels[:5])

    return {
        "name": recipe.get("label", "Unknown"),
        "description": f"Source: {recipe.get('source', 'Edamam')}",
        "category": _guess_category_from_labels(recipe.get("mealType", [])),
        "prep_time": f"{recipe.get('totalTime', 30)} min",
        "cook_time": "0 min",
        "servings": int(recipe.get("yield", 4)),
        "ingredients": recipe.get("ingredientLines", []),
        "instructions": [f"Visit {recipe.get('url', '')} for full instructions."],
        "image_url": recipe.get("image"),
        "source": "edamam",
        "external_id": recipe.get("uri", "").split("#recipe_")[-1] if recipe.get("uri") else "",
        "allergens": allergens,
        "diet_labels": diet_labels,
    }


def _normalize_tasty_recipe(raw: dict) -> dict:
    """Convert a Tasty recipe to our common schema."""
    ingredients = []
    for section in raw.get("sections", []):
        for component in section.get("components", []):
            ingredients.append(component.get("raw_text", ""))

    instructions = []
    for instr in raw.get("instructions", []):
        instructions.append(instr.get("display_text", ""))

    tags = [t.get("display_name", "").lower() for t in raw.get("tags", [])]
    diet_labels = [t for t in tags if t in (
        "vegetarian", "vegan", "gluten-free", "dairy-free", "keto", "paleo"
    )]

    return {
        "name": raw.get("name", "Unknown"),
        "description": raw.get("description", "")[:500] if raw.get("description") else "",
        "category": _guess_category(tags),
        "prep_time": f"{raw.get('prep_time_minutes', 15)} min",
        "cook_time": f"{raw.get('cook_time_minutes', 30)} min",
        "servings": raw.get("num_servings", 4),
        "ingredients": ingredients,
        "instructions": instructions,
        "image_url": raw.get("thumbnail_url"),
        "source": "tasty",
        "external_id": str(raw.get("id", "")),
        "allergens": [],
        "diet_labels": diet_labels,
    }


def _guess_category(tags: list) -> str:
    """Guess category from a list of tags/dish types."""
    tag_str = " ".join(t.lower() for t in tags)
    if any(w in tag_str for w in ["breakfast", "brunch", "morning"]):
        return "breakfast"
    if any(w in tag_str for w in ["lunch", "main course", "main dish"]):
        return "lunch"
    if any(w in tag_str for w in ["dinner", "supper"]):
        return "dinner"
    if any(w in tag_str for w in ["dessert", "sweet", "baking"]):
        return "desserts"
    if any(w in tag_str for w in ["snack", "appetizer", "starter", "side dish"]):
        return "snacks"
    if any(w in tag_str for w in ["drink", "beverage", "smoothie", "cocktail"]):
        return "drinks"
    if any(w in tag_str for w in ["salad"]):
        return "salads"
    return "other"


def _guess_category_from_labels(meal_types: list) -> str:
    """Guess category from Edamam mealType labels."""
    if not meal_types:
        return "other"
    mt = meal_types[0].lower()
    mapping = {
        "breakfast": "breakfast",
        "lunch/dinner": "lunch",
        "lunch": "lunch",
        "dinner": "dinner",
        "snack": "snacks",
        "teatime": "snacks",
    }
    return mapping.get(mt, "other")


# ---------------------------------------------------------------------------
# Public API functions
# ---------------------------------------------------------------------------

async def search_spoonacular(query: str, number: int = 10) -> list[dict]:
    """Search Spoonacular for recipes matching query."""
    if not settings.SPOONACULAR_API_KEY:
        return []

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                "https://api.spoonacular.com/recipes/complexSearch",
                params={
                    "query": query,
                    "number": number,
                    "addRecipeInformation": True,
                    "fillIngredients": True,
                    "apiKey": settings.SPOONACULAR_API_KEY,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return [_normalize_spoonacular_recipe(r) for r in data.get("results", [])]
    except Exception as e:
        print(f"⚠️  Spoonacular error: {e}")
        return []


async def search_spoonacular_by_ingredients(ingredients: list[str], number: int = 10) -> list[dict]:
    """Search Spoonacular by ingredients."""
    if not settings.SPOONACULAR_API_KEY:
        return []

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Step 1: find recipes by ingredients
            resp = await client.get(
                "https://api.spoonacular.com/recipes/findByIngredients",
                params={
                    "ingredients": ",".join(ingredients),
                    "number": number,
                    "apiKey": settings.SPOONACULAR_API_KEY,
                },
            )
            resp.raise_for_status()
            partial = resp.json()

            # Step 2: get full info for each
            results = []
            for item in partial[:number]:
                detail_resp = await client.get(
                    f"https://api.spoonacular.com/recipes/{item['id']}/information",
                    params={"apiKey": settings.SPOONACULAR_API_KEY},
                )
                if detail_resp.status_code == 200:
                    results.append(_normalize_spoonacular_recipe(detail_resp.json()))

            return results
    except Exception as e:
        print(f"⚠️  Spoonacular ingredient search error: {e}")
        return []


async def search_mealdb(query: str) -> list[dict]:
    """Search TheMealDB for recipes matching query (free, no key needed)."""
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                "https://www.themealdb.com/api/json/v1/1/search.php",
                params={"s": query},
            )
            resp.raise_for_status()
            data = resp.json()
            meals = data.get("meals") or []
            return [_normalize_mealdb_recipe(m) for m in meals]
    except Exception as e:
        print(f"⚠️  MealDB error: {e}")
        return []


async def search_edamam(query: str, number: int = 10) -> list[dict]:
    """Search Edamam for recipes matching query."""
    if not settings.EDAMAM_APP_ID or not settings.EDAMAM_APP_KEY:
        return []

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                "https://api.edamam.com/api/recipes/v2",
                params={
                    "type": "public",
                    "q": query,
                    "app_id": settings.EDAMAM_APP_ID,
                    "app_key": settings.EDAMAM_APP_KEY,
                    "from": 0,
                    "to": number,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return [_normalize_edamam_recipe(hit) for hit in data.get("hits", [])]
    except Exception as e:
        print(f"⚠️  Edamam error: {e}")
        return []


async def search_tasty(query: str, number: int = 10) -> list[dict]:
    """Search Tasty for recipes matching query."""
    if not settings.TASTY_API_KEY:
        return []

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                "https://tasty.p.rapidapi.com/recipes/list",
                params={"from": "0", "size": str(number), "q": query},
                headers={
                    "X-RapidAPI-Key": settings.TASTY_API_KEY,
                    "X-RapidAPI-Host": "tasty.p.rapidapi.com",
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return [_normalize_tasty_recipe(r) for r in data.get("results", [])]
    except Exception as e:
        print(f"⚠️  Tasty error: {e}")
        return []


async def search_all_apis(query: str, number_per_api: int = 5) -> list[dict]:
    """Search all configured APIs in parallel and return combined results."""
    import asyncio

    tasks = [
        search_mealdb(query),
        search_spoonacular(query, number_per_api),
        search_edamam(query, number_per_api),
        search_tasty(query, number_per_api),
    ]

    results_lists = await asyncio.gather(*tasks, return_exceptions=True)

    combined = []
    seen_names = set()
    for result in results_lists:
        if isinstance(result, Exception):
            print(f"⚠️  API search error: {result}")
            continue
        for recipe in result:
            name_key = recipe.get("name", "").lower().strip()
            if name_key not in seen_names:
                seen_names.add(name_key)
                combined.append(recipe)

    return combined


async def search_all_by_ingredients(ingredients: list[str], number: int = 10) -> list[dict]:
    """Search by ingredients across available APIs."""
    # Currently only Spoonacular supports ingredient-based search
    results = await search_spoonacular_by_ingredients(ingredients, number)
    return results
