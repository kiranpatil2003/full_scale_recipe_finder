"""
recipe_nutrition_sync.py
────────────────────────
Reads the `recipes` table from Supabase (ingredients column is a JSON array
of strings like "3 Eggs"), looks up each ingredient on USDA FoodData Central,
aggregates nutrition per recipe, and upserts the results into a `nutritions`
table in Supabase.

Requirements:
    pip install supabase requests python-dotenv

Environment variables (put in a .env file or export them):
    SUPABASE_URL        = https://xxxx.supabase.co
    SUPABASE_KEY        = your-service-role-or-anon-key
    USDA_API_KEY        = your-usda-api-key  (get free at https://fdc.nal.usda.gov/api-key-signup.html)

USDA rate limit: 3 600 requests / hour per API key (1 req/sec sustained is safe).
We add a 0.35-second delay between every ingredient lookup to stay well under.
"""

import os
import re
import time
import logging
from typing import Optional

import requests
from dotenv import load_dotenv
from supabase import create_client, Client

# ─── Configuration ────────────────────────────────────────────────────────────

load_dotenv()

SUPABASE_URL: str = os.environ["SUPABASE_URL"]
SUPABASE_KEY: str = os.environ["SUPABASE_KEY"]
USDA_API_KEY: str = os.environ["USDA_API_KEY"]

USDA_SEARCH_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"

# USDA allows ~3 600 req/hr → ~1 req/sec.
# We use 0.35 s to be safe while still being reasonably fast.
USDA_DELAY_SECONDS = 0.35

# Nutrient IDs we care about from USDA FoodData Central
# Full list: https://fdc.nal.usda.gov/fdc-app.html#/?query=nutrients
NUTRIENT_MAP = {
    "calories_kcal":         1008,   # Energy (kcal)
    "protein_g":             1003,   # Protein
    "fat_total_g":           1004,   # Total lipid (fat)
    "carbohydrates_g":       1005,   # Carbohydrate, by difference
    "fiber_g":               1079,   # Fiber, total dietary
    "sugar_g":               2000,   # Sugars, total including NLEA
    "sodium_mg":             1093,   # Sodium
    "cholesterol_mg":        1253,   # Cholesterol
    "saturated_fat_g":       1258,   # Fatty acids, total saturated
    "potassium_mg":          1092,   # Potassium
    "calcium_mg":            1087,   # Calcium
    "iron_mg":               1089,   # Iron
    "vitamin_c_mg":          1162,   # Vitamin C
    "vitamin_a_iu":          1104,   # Vitamin A, IU
    "vitamin_d_iu":          1110,   # Vitamin D (D2 + D3), International Units
    "vitamin_b12_mcg":       1178,   # Vitamin B-12
    "folate_mcg":            1177,   # Folate, total
    "zinc_mg":               1095,   # Zinc
    "magnesium_mg":          1090,   # Magnesium
    "phosphorus_mg":         1091,   # Phosphorus
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ─── Ingredient parser ─────────────────────────────────────────────────────────

# Common cooking units we strip so the food-name search is cleaner
_UNITS = (
    r"cups?|tablespoons?|tbsp|teaspoons?|tsp|pounds?|lbs?|ounces?|oz|"
    r"grams?|g|kilograms?|kg|milliliters?|ml|liters?|l|pinch(?:es)?|"
    r"slices?|pieces?|cloves?|cans?|packages?|pkg|bunches?|stalks?|"
    r"heads?|sprigs?|sheets?|strips?|fillets?|servings?"
)

_AMOUNT_UNIT_RE = re.compile(
    r"^\s*"
    r"(?P<qty>[\d]+(?:[./]\d+)?(?:\s*-\s*[\d]+(?:[./]\d+)?)?)"   # quantity
    r"\s*"
    r"(?P<unit>" + _UNITS + r")?"                                   # optional unit
    r"\.?\s*",
    re.IGNORECASE,
)


def parse_ingredient(raw: str) -> tuple[float, str]:
    """
    Split a raw ingredient string into (quantity_in_grams_approx, food_name).

    The quantity is used only to scale the per-100g USDA values.
    We attempt a rough gram conversion; if the unit is unknown we fall
    back to 1 serving (treated as 100 g for scaling purposes).

    Returns
    -------
    quantity_g : float   – estimated grams of the food
    food_name  : str     – cleaned food name for the USDA search
    """
    # Rough unit → gram conversions (all very approximate)
    UNIT_TO_G = {
        "cup": 240, "cups": 240,
        "tablespoon": 15, "tablespoons": 15, "tbsp": 15,
        "teaspoon": 5, "teaspoons": 5, "tsp": 5,
        "pound": 454, "pounds": 454, "lb": 454, "lbs": 454,
        "ounce": 28, "ounces": 28, "oz": 28,
        "gram": 1, "grams": 1, "g": 1,
        "kilogram": 1000, "kilograms": 1000, "kg": 1000,
        "milliliter": 1, "milliliters": 1, "ml": 1,
        "liter": 1000, "liters": 1000, "l": 1000,
    }

    m = _AMOUNT_UNIT_RE.match(raw)
    if not m:
        return 100.0, raw.strip()

    qty_str = m.group("qty").replace(" ", "")
    unit_str = (m.group("unit") or "").lower().rstrip("s") + (
        "s" if (m.group("unit") or "").lower().endswith("s") else ""
    )

    # Evaluate fractions like "1/2"
    try:
        if "/" in qty_str:
            num, den = qty_str.split("/")
            qty = float(num) / float(den)
        elif "-" in qty_str:          # range like "1-2" → take the midpoint
            lo, hi = qty_str.split("-")
            qty = (float(lo) + float(hi)) / 2
        else:
            qty = float(qty_str)
    except ValueError:
        qty = 1.0

    unit_key = (m.group("unit") or "").lower()
    g_per_unit = UNIT_TO_G.get(unit_key, 100)   # default: treat as 100 g
    quantity_g = qty * g_per_unit

    food_name = raw[m.end():].strip()
    # Drop trailing parenthetical notes like "(diced)", "(grated)", etc.
    food_name = re.sub(r"\(.*?\)", "", food_name).strip()
    # Drop trailing descriptors separated by comma: "Zucchini, grated" → "Zucchini"
    food_name = food_name.split(",")[0].strip()

    return quantity_g, food_name


# ─── USDA helpers ─────────────────────────────────────────────────────────────

def usda_search(food_name: str, api_key: str) -> Optional[dict]:
    """
    Search USDA FoodData Central for `food_name`.
    Returns the best-matching food dict or None.
    Respects the rate limit via USDA_DELAY_SECONDS sleep BEFORE the call.
    """
    time.sleep(USDA_DELAY_SECONDS)   # rate-limit guard

    params = {
        "query": food_name,
        "api_key": api_key,
        "dataType": ["SR Legacy", "Foundation", "Survey (FNDDS)"],
        "pageSize": 1,
    }
    try:
        resp = requests.get(USDA_SEARCH_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        foods = data.get("foods", [])
        if not foods:
            log.warning("  USDA: no result for '%s'", food_name)
            return None
        return foods[0]
    except requests.RequestException as exc:
        log.error("  USDA request failed for '%s': %s", food_name, exc)
        return None


def extract_nutrients(food: dict) -> dict[str, float]:
    """
    Given a USDA food dict, return a mapping of our nutrient keys → value per 100 g.
    """
    # Build id → value lookup from the food's foodNutrients list
    id_to_value: dict[int, float] = {}
    for n in food.get("foodNutrients", []):
        nid = n.get("nutrientId") or n.get("nutrient", {}).get("id")
        val = n.get("value") or n.get("amount") or 0.0
        if nid:
            id_to_value[int(nid)] = float(val)

    result = {}
    for key, nid in NUTRIENT_MAP.items():
        result[key] = id_to_value.get(nid, 0.0)
    return result


def scale_nutrients(nutrients_per_100g: dict[str, float], quantity_g: float) -> dict[str, float]:
    """Scale nutrients from per-100g to the actual ingredient quantity."""
    factor = quantity_g / 100.0
    return {k: round(v * factor, 4) for k, v in nutrients_per_100g.items()}


# ─── Supabase helpers ──────────────────────────────────────────────────────────

def ensure_nutritions_table(client: Client) -> None:
    """
    Creates the `nutritions` table if it doesn't exist.
    We attempt it via raw SQL through the rpc endpoint; if your Supabase
    project doesn't allow that, create the table manually with the SQL below.
    """
    create_sql = """
    CREATE TABLE IF NOT EXISTS nutritions (
        id                  BIGSERIAL PRIMARY KEY,
        recipe_id           BIGINT NOT NULL UNIQUE,
        calories_kcal       NUMERIC(10,4) DEFAULT 0,
        protein_g           NUMERIC(10,4) DEFAULT 0,
        fat_total_g         NUMERIC(10,4) DEFAULT 0,
        carbohydrates_g     NUMERIC(10,4) DEFAULT 0,
        fiber_g             NUMERIC(10,4) DEFAULT 0,
        sugar_g             NUMERIC(10,4) DEFAULT 0,
        sodium_mg           NUMERIC(10,4) DEFAULT 0,
        cholesterol_mg      NUMERIC(10,4) DEFAULT 0,
        saturated_fat_g     NUMERIC(10,4) DEFAULT 0,
        potassium_mg        NUMERIC(10,4) DEFAULT 0,
        calcium_mg          NUMERIC(10,4) DEFAULT 0,
        iron_mg             NUMERIC(10,4) DEFAULT 0,
        vitamin_c_mg        NUMERIC(10,4) DEFAULT 0,
        vitamin_a_iu        NUMERIC(10,4) DEFAULT 0,
        vitamin_d_iu        NUMERIC(10,4) DEFAULT 0,
        vitamin_b12_mcg     NUMERIC(10,4) DEFAULT 0,
        folate_mcg          NUMERIC(10,4) DEFAULT 0,
        zinc_mg             NUMERIC(10,4) DEFAULT 0,
        magnesium_mg        NUMERIC(10,4) DEFAULT 0,
        phosphorus_mg       NUMERIC(10,4) DEFAULT 0,
        ingredients_count   INT DEFAULT 0,
        matched_count       INT DEFAULT 0,
        created_at          TIMESTAMPTZ DEFAULT NOW(),
        updated_at          TIMESTAMPTZ DEFAULT NOW()
    );
    """
    try:
        client.rpc("exec_sql", {"query": create_sql}).execute()
        log.info("nutritions table ensured via rpc.")
    except Exception:
        log.warning(
            "Could not auto-create table via rpc. "
            "Please run the SQL in ensure_nutritions_table() manually in Supabase SQL editor."
        )


def fetch_all_recipes(client: Client) -> list[dict]:
    """Fetch all rows from the recipes table (id + ingredients columns)."""
    response = client.table("recipes").select("id, ingredients").execute()
    return response.data or []


def fetch_existing_nutrition_ids(client: Client) -> set[int]:
    """Fetch the recipe_ids already present in the nutritions table."""
    try:
        response = client.table("nutritions").select("recipe_id").execute()
        return {row["recipe_id"] for row in response.data} if response.data else set()
    except Exception as e:
        log.warning("Could not fetch existing nutrition IDs (table might not exist yet): %s", e)
        return set()


def upsert_nutrition(client: Client, recipe_id: int, nutrition: dict) -> None:
    """Insert or update a nutrition row for the given recipe."""
    nutrition["recipe_id"] = recipe_id
    nutrition["updated_at"] = "now()"
    client.table("nutritions").upsert(nutrition, on_conflict="recipe_id").execute()


# ─── Core pipeline ─────────────────────────────────────────────────────────────

def aggregate_recipe_nutrition(
    ingredients: list[str],
    api_key: str,
) -> dict:
    """
    Given a list of raw ingredient strings, return aggregated nutrition totals.
    """
    totals: dict[str, float] = {k: 0.0 for k in NUTRIENT_MAP}
    matched = 0

    for raw in ingredients:
        if not raw or not raw.strip():
            continue

        quantity_g, food_name = parse_ingredient(raw)
        log.info("    → '%s'  (%.0f g)", food_name, quantity_g)

        food = usda_search(food_name, api_key)
        if food is None:
            continue

        per_100g = extract_nutrients(food)
        scaled   = scale_nutrients(per_100g, quantity_g)

        for key in totals:
            totals[key] += scaled.get(key, 0.0)

        matched += 1

    # Round final totals
    totals = {k: round(v, 4) for k, v in totals.items()}
    totals["ingredients_count"] = len(ingredients)
    totals["matched_count"]     = matched
    return totals


def main() -> None:
    log.info("Connecting to Supabase …")
    client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    ensure_nutritions_table(client)

    log.info("Fetching recipes …")
    recipes = fetch_all_recipes(client)
    log.info("Found %d recipe(s) in database.", len(recipes))

    log.info("Checking for existing nutrition records …")
    existing_ids = fetch_existing_nutrition_ids(client)
    if existing_ids:
        initial_count = len(recipes)
        recipes = [r for r in recipes if r["id"] not in existing_ids]
        skipped = initial_count - len(recipes)
        if skipped > 0:
            log.info("Skipping %d recipe(s) that already have nutrition data.", skipped)

    if not recipes:
        log.info("No new recipes to process.")
        return

    log.info("Processing %d recipe(s) …", len(recipes))

    for recipe in recipes:
        recipe_id   = recipe["id"]
        ingredients = recipe.get("ingredients") or []

        # Supabase may return a JSON string instead of a parsed list
        if isinstance(ingredients, str):
            import json
            ingredients = json.loads(ingredients)

        log.info("Recipe #%s  (%d ingredients)", recipe_id, len(ingredients))

        nutrition = aggregate_recipe_nutrition(ingredients, USDA_API_KEY)

        log.info(
            "  → %.1f kcal | %.1f g protein | %.1f g carbs | %.1f g fat  "
            "(%d/%d ingredients matched)",
            nutrition.get("calories_kcal", 0),
            nutrition.get("protein_g", 0),
            nutrition.get("carbohydrates_g", 0),
            nutrition.get("fat_total_g", 0),
            nutrition["matched_count"],
            nutrition["ingredients_count"],
        )

        upsert_nutrition(client, recipe_id, nutrition)
        log.info("  ✓ Upserted nutrition for recipe #%s", recipe_id)

    log.info("Done. All recipes processed.")


if __name__ == "__main__":
    main()