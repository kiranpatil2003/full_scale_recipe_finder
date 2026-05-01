"""
recipe_enrichment.py
─────────────────────
Enriches recipes in Supabase with:
  • prep_time   – estimated from instructions + ingredients (Ollama LLM)
  • cook_time   – estimated from instructions + ingredients (Ollama LLM)
  • allergens   – rule-based from ingredients
  • diet_labels – rule-based from ingredients

LLM Backend: your local Ollama instance at 192.168.1.37:11434
  • No rate limits, no API keys, no delays
  • Uses /api/chat with format:"json" + stream:false for clean structured output
  • Model is configured via OLLAMA_MODEL env var (default: llama3.2)

Safety checks (nothing is ever overwritten):
  • If ALL four fields are already populated → entire recipe is skipped
  • If a field already has data → excluded from LLM prompt and DB update
  • Rule-based fields (allergens, diet_labels) respect the same guard

Requirements:
    pip install supabase requests python-dotenv

.env file:
    SUPABASE_URL=https://xxxx.supabase.co
    SUPABASE_KEY=your-service-role-key
    OLLAMA_HOST=192.168.1.37          # optional, defaults to value below
    OLLAMA_MODEL=llama3.2             # optional, change to your pulled model
"""

import os
import re
import json
import logging
from typing import Optional

import requests
from dotenv import load_dotenv
from supabase import create_client, Client

# ─── Config ───────────────────────────────────────────────────────────────────

load_dotenv()

SUPABASE_URL: str = os.environ["SUPABASE_URL"]
SUPABASE_KEY: str = os.environ["SUPABASE_KEY"]

OLLAMA_HOST: str  = os.getenv("OLLAMA_HOST",  "192.168.1.37")
OLLAMA_PORT: int  = int(os.getenv("OLLAMA_PORT", "11434"))
OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2")

OLLAMA_BASE_URL   = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}"
OLLAMA_CHAT_URL   = f"{OLLAMA_BASE_URL}/api/chat"
OLLAMA_TAGS_URL   = f"{OLLAMA_BASE_URL}/api/tags"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ─── Allergen rules (EU top-14 + FDA top-9) ───────────────────────────────────

ALLERGEN_RULES: dict[str, list[str]] = {
    "Gluten":     ["flour", "wheat", "bread", "breadcrumb", "pasta", "noodle",
                   "barley", "rye", "oat", "semolina", "spelt", "farro",
                   "cracker", "biscuit", "tortilla", "pita", "couscous", "soy sauce"],
    "Eggs":       ["egg", "eggs", "mayonnaise", "mayo", "meringue"],
    "Dairy":      ["milk", "butter", "cream", "cheese", "yogurt", "yoghurt",
                   "sour cream", "cheddar", "mozzarella", "parmesan", "ricotta",
                   "brie", "gouda", "whey", "lactose", "ghee", "kefir"],
    "Nuts":       ["almond", "walnut", "cashew", "pistachio", "pecan",
                   "hazelnut", "macadamia", "pine nut", "brazil nut", "marzipan"],
    "Peanuts":    ["peanut", "groundnut", "peanut butter", "peanut oil"],
    "Soy":        ["soy", "soya", "tofu", "tempeh", "edamame", "miso", "tamari"],
    "Fish":       ["fish", "salmon", "tuna", "cod", "tilapia", "bass", "trout",
                   "anchovy", "anchovies", "sardine", "mackerel", "halibut",
                   "herring", "snapper", "catfish", "fish sauce"],
    "Shellfish":  ["shrimp", "prawn", "crab", "lobster", "clam", "oyster",
                   "scallop", "mussel", "squid", "octopus", "crayfish"],
    "Sesame":     ["sesame", "tahini", "sesame oil", "sesame seed"],
    "Mustard":    ["mustard"],
    "Celery":     ["celery", "celeriac"],
    "Lupin":      ["lupin", "lupine"],
    "Molluscs":   ["snail", "squid", "octopus", "clam", "mussel", "oyster", "scallop"],
    "Sulphites":  ["wine", "dried fruit", "vinegar", "sulphite", "sulfite", "preserved lemon"],
}


# ─── Diet label rules ─────────────────────────────────────────────────────────

DIET_BLOCKLISTS: dict[str, list[str]] = {
    "Vegan": [
        "chicken", "beef", "pork", "lamb", "turkey", "duck", "veal",
        "bacon", "ham", "sausage", "salami", "pepperoni", "lard",
        "mince", "minced", "ground beef", "ground pork", "steak",
        "liver", "kidney", "offal",
        "fish", "salmon", "tuna", "cod", "shrimp", "prawn", "crab",
        "lobster", "anchovy", "anchovies", "sardine", "fish sauce",
        "milk", "butter", "cream", "cheese", "yogurt", "yoghurt",
        "sour cream", "ghee", "whey", "egg", "honey", "gelatin", "gelatine",
    ],
    "Vegetarian": [
        "chicken", "beef", "pork", "lamb", "turkey", "duck", "veal",
        "bacon", "ham", "sausage", "salami", "pepperoni", "lard",
        "mince", "minced", "ground beef", "ground pork", "steak",
        "liver", "kidney", "offal",
        "fish", "salmon", "tuna", "cod", "shrimp", "prawn", "crab",
        "lobster", "anchovy", "anchovies", "sardine", "fish sauce",
        "gelatin", "gelatine",
    ],
    "Gluten-Free": [
        "flour", "wheat", "bread", "breadcrumb", "pasta", "noodle",
        "barley", "rye", "oat", "semolina", "spelt", "farro",
        "cracker", "biscuit", "tortilla", "pita", "couscous", "soy sauce",
    ],
    "Dairy-Free": [
        "milk", "butter", "cream", "cheese", "yogurt", "yoghurt",
        "sour cream", "cheddar", "mozzarella", "parmesan", "ricotta",
        "brie", "gouda", "whey", "lactose", "ghee", "kefir",
    ],
    "Nut-Free": [
        "almond", "walnut", "cashew", "pistachio", "pecan",
        "hazelnut", "macadamia", "pine nut", "brazil nut",
        "peanut", "groundnut",
    ],
    "Low-Carb": [
        "flour", "bread", "pasta", "rice", "potato", "potatoes",
        "sugar", "corn", "oat", "noodle", "tortilla", "couscous",
        "quinoa", "lentil", "chickpea", "bean", "pea",
    ],
}


# ─── Rule-based helpers ────────────────────────────────────────────────────────

def _norm(text: str) -> str:
    return text.lower().strip()


def detect_allergens(ingredients: list[str]) -> list[str]:
    joined = " | ".join(_norm(i) for i in ingredients)
    return sorted(
        allergen for allergen, triggers in ALLERGEN_RULES.items()
        if any(t in joined for t in triggers)
    )


def detect_diet_labels(ingredients: list[str]) -> list[str]:
    joined = " | ".join(_norm(i) for i in ingredients)
    return sorted(
        label for label, blocklist in DIET_BLOCKLISTS.items()
        if not any(b in joined for b in blocklist)
    )


# ─── Ollama connection check ───────────────────────────────────────────────────

def check_ollama_connection() -> bool:
    """Verify Ollama is reachable and the configured model is available."""
    try:
        resp = requests.get(OLLAMA_TAGS_URL, timeout=5)
        resp.raise_for_status()
        models = [m["name"] for m in resp.json().get("models", [])]
        log.info("✅ Ollama reachable at %s", OLLAMA_BASE_URL)
        log.info("   Available models: %s", models or "(none pulled yet)")

        # Warn if our model isn't in the list (partial match is fine, e.g. "llama3.2:latest")
        if not any(OLLAMA_MODEL in m for m in models):
            log.warning(
                "   Model '%s' not found — run: ollama pull %s",
                OLLAMA_MODEL, OLLAMA_MODEL,
            )
            return False
        return True
    except requests.exceptions.ConnectionError:
        log.error("❌ Cannot connect to Ollama at %s", OLLAMA_BASE_URL)
        log.error("   Make sure Ollama is running and reachable from this machine.")
        return False
    except Exception as exc:
        log.error("❌ Ollama check failed: %s", exc)
        return False


# ─── Ollama LLM call ───────────────────────────────────────────────────────────

# System prompt: tight instructions so the model stays on-task
SYSTEM_PROMPT = """\
You are a culinary data extraction assistant.
Your sole task is to read a recipe and return a JSON object containing \
only the specific fields you are asked for.

Strict rules:
1. Output ONLY a raw JSON object — no markdown fences, no explanation, \
no preamble, no trailing text.
2. Include only the exact keys requested — nothing more.
3. Time values must be plain English strings such as "15 minutes", \
"1 hour", "1 hour 30 minutes". Use "Unknown" only if truly impossible.
4. Do not invent data. Base estimates on the ingredients and instructions provided."""


def build_user_prompt(
    name: str,
    ingredients: list[str],
    instructions: list[str],
    need_prep: bool,
    need_cook: bool,
) -> tuple[str, list[str]]:
    """
    Build a tight, structured user message.
    Returns (prompt_string, list_of_expected_keys).
    Only requests the fields that are missing from the DB.
    """
    wanted_keys: list[str] = []
    schema_lines: list[str] = []

    if need_prep:
        wanted_keys.append("prep_time")
        schema_lines.append(
            '  "prep_time": "<total hands-on prep time: peeling, '
            'chopping, measuring, marinating, mixing — before heat is applied>"'
        )
    if need_cook:
        wanted_keys.append("cook_time")
        schema_lines.append(
            '  "cook_time": "<total active cooking time: frying, '
            'baking, boiling, simmering, grilling — from heat-on to done>"'
        )

    schema_block = ",\n".join(schema_lines)

    prompt = f"""Return ONLY this JSON object (fill in the values):
{{
{schema_block}
}}

---
Recipe: {name}

Ingredients:
{json.dumps(ingredients, indent=2)}

Instructions:
{chr(10).join(f"{i+1}. {step}" for i, step in enumerate(instructions))}
---

Output the JSON object only. No other text."""

    return prompt, wanted_keys


# ─── Core LLM call ────────────────────────────────────────────────────────────

def call_ollama(system_prompt: str, user_prompt: str) -> Optional[dict]:
    """
    POST to Ollama /api/chat.
    - format:"json"  → model is forced to emit valid JSON
    - stream:false   → full response in one shot, no streaming to parse
    - temperature:0  → deterministic, consistent output
    """
    payload = {
        "model":   OLLAMA_MODEL,
        "stream":  False,
        "format":  "json",
        "options": {
            "temperature": 0,
            "num_predict": 128,   # time fields are short — keep output tight
        },
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
    }

    try:
        resp = requests.post(OLLAMA_CHAT_URL, json=payload, timeout=120)
        resp.raise_for_status()

        raw = resp.json()["message"]["content"].strip()

        # Belt-and-suspenders: strip any markdown fences some models still sneak in
        raw = re.sub(r"```(?:json)?|```", "", raw).strip()

        return json.loads(raw)

    except json.JSONDecodeError:
        log.error("  Ollama returned non-JSON content.")
        return None
    except requests.exceptions.ConnectionError:
        log.error("  Lost connection to Ollama at %s.", OLLAMA_BASE_URL)
        return None
    except KeyError:
        log.error("  Unexpected Ollama response structure.")
        return None
    except Exception as exc:
        log.error("  Ollama call failed: %s", exc)
        return None


# ─── Supabase helpers ──────────────────────────────────────────────────────────

def fetch_recipes(client: Client) -> list[dict]:
    resp = (
        client.table("recipes")
        .select("id, name, ingredients, instructions, prep_time, cook_time, allergens, diet_labels")
        .execute()
    )
    return resp.data or []


def is_non_empty(value) -> bool:
    """True when a field already contains real data."""
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip().lower() not in ("", "null", "none", "unknown", "n/a")
    if isinstance(value, list):
        return len(value) > 0
    return bool(value)


def is_fully_enriched(recipe: dict) -> bool:
    """True only when every target field is already populated."""
    return all(
        is_non_empty(recipe.get(f))
        for f in ("prep_time", "cook_time", "allergens", "diet_labels")
    )


def update_recipe(client: Client, recipe_id: int, updates: dict) -> None:
    if updates:
        client.table("recipes").update(updates).eq("id", recipe_id).execute()


# ─── Per-recipe pipeline ───────────────────────────────────────────────────────

def process_recipe(client: Client, recipe: dict) -> None:
    recipe_id = recipe["id"]
    name      = recipe.get("name") or f"Recipe #{recipe_id}"

    # Guard: skip entirely if all fields already populated
    if is_fully_enriched(recipe):
        log.info("⏭  #%s '%s' — fully enriched, skipping.", recipe_id, name)
        return

    log.info("🍳 #%s '%s'", recipe_id, name)

    # Normalise to lists (Supabase may return raw JSON strings)
    ingredients  = recipe.get("ingredients")  or []
    instructions = recipe.get("instructions") or []
    if isinstance(ingredients,  str): ingredients  = json.loads(ingredients)
    if isinstance(instructions, str): instructions = json.loads(instructions)

    updates: dict = {}

    # ── Rule-based: allergens ─────────────────────────────────────────────────
    if not is_non_empty(recipe.get("allergens")):
        allergens = detect_allergens(ingredients)
        updates["allergens"] = allergens
        log.info("  allergens   → %s", allergens if allergens else "[]  (none found)")
    else:
        log.info("  allergens   → already set, leaving untouched.")

    # ── Rule-based: diet_labels ───────────────────────────────────────────────
    if not is_non_empty(recipe.get("diet_labels")):
        diet_labels = detect_diet_labels(ingredients)
        updates["diet_labels"] = diet_labels
        log.info("  diet_labels → %s", diet_labels if diet_labels else "[]  (none apply)")
    else:
        log.info("  diet_labels → already set, leaving untouched.")

    # ── LLM: prep_time / cook_time ────────────────────────────────────────────
    need_prep = not is_non_empty(recipe.get("prep_time"))
    need_cook = not is_non_empty(recipe.get("cook_time"))

    if need_prep or need_cook:
        if not ingredients and not instructions:
            log.warning("  No ingredients or instructions — cannot estimate times.")
        else:
            requesting = " + ".join(
                (["prep_time"] if need_prep else []) +
                (["cook_time"] if need_cook else [])
            )
            log.info("  Asking Ollama for: %s", requesting)

            user_prompt, expected_keys = build_user_prompt(
                name, ingredients, instructions, need_prep, need_cook
            )
            result = call_ollama(SYSTEM_PROMPT, user_prompt)

            if result:
                for key in expected_keys:
                    val = str(result.get(key, "")).strip()
                    if val and val.lower() not in ("unknown", "null", "none", "", "n/a"):
                        updates[key] = val
                        log.info("  %-13s → %s", key, val)
                    else:
                        log.warning("  %-13s → model returned no usable value.", key)
            else:
                log.warning("  Ollama returned no usable result for this recipe.")
    else:
        log.info("  prep/cook   → both already set, leaving untouched.")

    # ── Persist to DB ─────────────────────────────────────────────────────────
    if updates:
        update_recipe(client, recipe_id, updates)
        log.info("  ✓ Saved: %s", list(updates.keys()))
    else:
        log.info("  ✓ No new data to save.")

    print()


# ─── Entry point ──────────────────────────────────────────────────────────────

def main() -> None:
    # Step 1: verify Ollama is up before touching the DB
    if not check_ollama_connection():
        log.error("Aborting — fix the Ollama connection first.")
        return

    print()

    # Step 2: connect to Supabase
    log.info("Connecting to Supabase …")
    client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Step 3: load recipes
    log.info("Fetching recipes …")
    recipes = fetch_recipes(client)
    log.info("Found %d recipe(s).", len(recipes))

    done_count    = sum(1 for r in recipes if is_fully_enriched(r))
    pending_count = len(recipes) - done_count

    log.info("Already complete : %d", done_count)
    log.info("To process       : %d\n", pending_count)

    if pending_count == 0:
        log.info("Nothing to do — all recipes are already enriched.")
        return

    # Step 4: enrich each recipe
    for recipe in recipes:
        process_recipe(client, recipe)

    log.info("Done. %d/%d recipes processed.", pending_count, len(recipes))


if __name__ == "__main__":
    main()