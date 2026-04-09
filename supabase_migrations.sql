-- ============================================================
-- Recipe Finder — Supabase Database Migration
-- Run this in your Supabase SQL Editor (Dashboard > SQL Editor)
-- ============================================================

-- 1. USERS TABLE
CREATE TABLE IF NOT EXISTS users (
    uid TEXT PRIMARY KEY,
    email TEXT,
    display_name TEXT,
    photo_url TEXT,
    fcm_token TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. RECIPES TABLE
CREATE TABLE IF NOT EXISTS recipes (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    category TEXT DEFAULT 'other',
    prep_time TEXT DEFAULT '',
    cook_time TEXT DEFAULT '',
    servings INTEGER DEFAULT 1,
    ingredients TEXT[] DEFAULT '{}',
    instructions TEXT[] DEFAULT '{}',
    image_url TEXT,
    source TEXT DEFAULT 'manual',
    external_id TEXT DEFAULT '',
    allergens TEXT[] DEFAULT '{}',
    diet_labels TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Unique constraint to prevent duplicate imports
CREATE UNIQUE INDEX IF NOT EXISTS idx_recipes_source_external
    ON recipes (source, external_id)
    WHERE external_id != '';

-- Index for search
CREATE INDEX IF NOT EXISTS idx_recipes_name ON recipes USING gin (to_tsvector('english', name));
CREATE INDEX IF NOT EXISTS idx_recipes_category ON recipes (category);

-- 3. USER FAVORITES
CREATE TABLE IF NOT EXISTS user_favorites (
    id BIGSERIAL PRIMARY KEY,
    user_uid TEXT NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    recipe_id BIGINT NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_uid, recipe_id)
);

CREATE INDEX IF NOT EXISTS idx_favorites_user ON user_favorites (user_uid);

-- 4. USER DIETARY PREFERENCES
CREATE TABLE IF NOT EXISTS user_dietary_preferences (
    id BIGSERIAL PRIMARY KEY,
    user_uid TEXT NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    preference TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_uid, preference)
);

CREATE INDEX IF NOT EXISTS idx_dietary_user ON user_dietary_preferences (user_uid);

-- 5. USER ALLERGIES
CREATE TABLE IF NOT EXISTS user_allergies (
    id BIGSERIAL PRIMARY KEY,
    user_uid TEXT NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    allergen TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_uid, allergen)
);

CREATE INDEX IF NOT EXISTS idx_allergies_user ON user_allergies (user_uid);

-- 6. Enable Row Level Security (RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_favorites ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_dietary_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_allergies ENABLE ROW LEVEL SECURITY;
ALTER TABLE recipes ENABLE ROW LEVEL SECURITY;

-- 7. RLS Policies — Allow full access for service role (our backend uses service role key)
-- These policies allow the backend (using service_role key) to access everything.
-- If you use anon key instead, you'd need more restrictive policies.

CREATE POLICY "Service role full access on users"
    ON users FOR ALL
    USING (true) WITH CHECK (true);

CREATE POLICY "Service role full access on recipes"
    ON recipes FOR ALL
    USING (true) WITH CHECK (true);

CREATE POLICY "Service role full access on user_favorites"
    ON user_favorites FOR ALL
    USING (true) WITH CHECK (true);

CREATE POLICY "Service role full access on user_dietary_preferences"
    ON user_dietary_preferences FOR ALL
    USING (true) WITH CHECK (true);

CREATE POLICY "Service role full access on user_allergies"
    ON user_allergies FOR ALL
    USING (true) WITH CHECK (true);

-- 8. Seed some initial recipes (optional — your app will fetch from APIs)
INSERT INTO recipes (name, description, category, prep_time, cook_time, servings, ingredients, instructions, image_url, source) VALUES
(
    'Classic Pancakes',
    'Fluffy golden pancakes perfect for a weekend breakfast.',
    'breakfast', '10 min', '15 min', 4,
    ARRAY['1½ cups all-purpose flour', '3½ tsp baking powder', '1 tbsp sugar', '¼ tsp salt', '1¼ cups milk', '1 egg', '3 tbsp melted butter'],
    ARRAY['Mix flour, baking powder, sugar, and salt.', 'Make a well, pour in milk, egg, and butter.', 'Mix until smooth.', 'Cook on griddle until golden.'],
    NULL, 'manual'
),
(
    'Avocado Toast',
    'Simple and nutritious avocado toast with a twist.',
    'breakfast', '5 min', '5 min', 2,
    ARRAY['2 slices sourdough bread', '1 ripe avocado', '1 tbsp lemon juice', 'Salt and pepper', 'Red pepper flakes'],
    ARRAY['Toast bread until golden.', 'Mash avocado with lemon juice, salt, pepper.', 'Spread on toast.', 'Top with red pepper flakes.'],
    NULL, 'manual'
),
(
    'Chicken Tikka Masala',
    'Creamy and spiced Indian curry with tender chicken pieces.',
    'dinner', '20 min', '30 min', 4,
    ARRAY['500g chicken breast', '1 cup yogurt', '2 tbsp tikka masala paste', '1 onion', '3 cloves garlic', '400g canned tomatoes', '1 cup heavy cream', '2 tbsp butter', 'Cilantro', 'Basmati rice'],
    ARRAY['Marinate chicken in yogurt and paste.', 'Cook chicken until browned.', 'Sauté onion and garlic in butter.', 'Add tomatoes, simmer 10 min.', 'Add cream and chicken, simmer 15 min.', 'Serve with rice.'],
    NULL, 'manual'
),
(
    'Mango Smoothie',
    'Refreshing tropical smoothie with mango and yogurt.',
    'drinks', '5 min', '0 min', 2,
    ARRAY['2 ripe mangoes', '1 cup yogurt', '½ cup milk', '2 tbsp honey', 'Ice cubes'],
    ARRAY['Add all ingredients to blender.', 'Blend until smooth.', 'Add ice and blend again.', 'Serve immediately.'],
    NULL, 'manual'
),
(
    'Greek Salad',
    'Fresh Mediterranean salad with feta and olives.',
    'salads', '10 min', '0 min', 2,
    ARRAY['2 tomatoes', '1 cucumber', '½ red onion', '100g feta cheese', '½ cup olives', '2 tbsp olive oil', '1 tbsp red wine vinegar', 'Oregano'],
    ARRAY['Combine tomatoes, cucumber, and onion.', 'Add olives and feta.', 'Drizzle with oil and vinegar.', 'Sprinkle oregano and toss.'],
    NULL, 'manual'
),
(
    'Chocolate Lava Cake',
    'Decadent chocolate cake with a molten center.',
    'desserts', '15 min', '12 min', 4,
    ARRAY['200g dark chocolate', '100g butter', '2 eggs', '2 egg yolks', '¼ cup sugar', '2 tbsp flour', 'Cocoa powder'],
    ARRAY['Melt chocolate and butter.', 'Whisk eggs, yolks, sugar until thick.', 'Fold in chocolate and flour.', 'Bake at 220°C for 12 min.', 'Invert and dust with cocoa.'],
    NULL, 'manual'
)
ON CONFLICT DO NOTHING;
