"""
Sample recipe data for the Recipe Finder API.
In production, this would be replaced with a database.
"""

RECIPES = [
    {
        "id": 1,
        "name": "Classic Pancakes",
        "description": "Fluffy golden pancakes perfect for a weekend breakfast.",
        "category": "breakfast",
        "prep_time": "10 min",
        "cook_time": "15 min",
        "servings": 4,
        "ingredients": [
            "1½ cups all-purpose flour",
            "3½ tsp baking powder",
            "1 tbsp sugar",
            "¼ tsp salt",
            "1¼ cups milk",
            "1 egg",
            "3 tbsp melted butter",
        ],
        "instructions": [
            "Mix flour, baking powder, sugar, and salt in a bowl.",
            "Make a well in the center, pour in milk, egg, and melted butter.",
            "Mix until smooth.",
            "Heat a griddle over medium-high heat and pour batter.",
            "Cook until bubbles form, then flip and cook until golden brown.",
        ],
        "image_url": None,
    },
    {
        "id": 2,
        "name": "Avocado Toast",
        "description": "Simple and nutritious avocado toast with a twist.",
        "category": "breakfast",
        "prep_time": "5 min",
        "cook_time": "5 min",
        "servings": 2,
        "ingredients": [
            "2 slices sourdough bread",
            "1 ripe avocado",
            "1 tbsp lemon juice",
            "Salt and pepper to taste",
            "Red pepper flakes",
            "2 poached eggs (optional)",
        ],
        "instructions": [
            "Toast the bread until golden and crispy.",
            "Mash the avocado with lemon juice, salt, and pepper.",
            "Spread avocado mixture on toast.",
            "Top with red pepper flakes and poached eggs if desired.",
        ],
        "image_url": None,
    },
    {
        "id": 3,
        "name": "Grilled Chicken Caesar Salad",
        "description": "A hearty salad with grilled chicken and creamy Caesar dressing.",
        "category": "salads",
        "prep_time": "15 min",
        "cook_time": "10 min",
        "servings": 2,
        "ingredients": [
            "2 chicken breasts",
            "1 head romaine lettuce",
            "½ cup Caesar dressing",
            "¼ cup grated Parmesan",
            "1 cup croutons",
            "Salt and pepper",
        ],
        "instructions": [
            "Season chicken breasts with salt and pepper.",
            "Grill chicken for 5-6 minutes per side until cooked through.",
            "Chop romaine lettuce and place in a large bowl.",
            "Slice grilled chicken and add to the salad.",
            "Toss with Caesar dressing, top with Parmesan and croutons.",
        ],
        "image_url": None,
    },
    {
        "id": 4,
        "name": "Spaghetti Bolognese",
        "description": "Classic Italian pasta with a rich and meaty Bolognese sauce.",
        "category": "lunch",
        "prep_time": "10 min",
        "cook_time": "40 min",
        "servings": 4,
        "ingredients": [
            "400g spaghetti",
            "500g ground beef",
            "1 onion, diced",
            "3 cloves garlic, minced",
            "400g canned tomatoes",
            "2 tbsp tomato paste",
            "1 tsp dried oregano",
            "Salt and pepper",
            "Parmesan cheese for serving",
        ],
        "instructions": [
            "Cook spaghetti according to package directions.",
            "Brown ground beef in a large pan, drain excess fat.",
            "Add onion and garlic, cook until softened.",
            "Stir in canned tomatoes, tomato paste, and oregano.",
            "Simmer for 25 minutes, season with salt and pepper.",
            "Serve sauce over spaghetti, topped with Parmesan.",
        ],
        "image_url": None,
    },
    {
        "id": 5,
        "name": "Chicken Tikka Masala",
        "description": "Creamy and spiced Indian curry with tender chicken pieces.",
        "category": "dinner",
        "prep_time": "20 min",
        "cook_time": "30 min",
        "servings": 4,
        "ingredients": [
            "500g chicken breast, cubed",
            "1 cup yogurt",
            "2 tbsp tikka masala paste",
            "1 onion, diced",
            "3 cloves garlic, minced",
            "400g canned tomatoes",
            "1 cup heavy cream",
            "2 tbsp butter",
            "Fresh cilantro",
            "Basmati rice for serving",
        ],
        "instructions": [
            "Marinate chicken in yogurt and tikka masala paste for 30 minutes.",
            "Cook marinated chicken in a hot pan until browned.",
            "In the same pan, sauté onion and garlic in butter.",
            "Add canned tomatoes and simmer for 10 minutes.",
            "Stir in heavy cream and add the chicken back.",
            "Simmer for 15 minutes, garnish with cilantro.",
            "Serve with basmati rice.",
        ],
        "image_url": None,
    },
    {
        "id": 6,
        "name": "Mango Smoothie",
        "description": "Refreshing tropical smoothie with mango and yogurt.",
        "category": "drinks",
        "prep_time": "5 min",
        "cook_time": "0 min",
        "servings": 2,
        "ingredients": [
            "2 ripe mangoes, peeled and chopped",
            "1 cup yogurt",
            "½ cup milk",
            "2 tbsp honey",
            "Ice cubes",
        ],
        "instructions": [
            "Add mango, yogurt, milk, and honey to a blender.",
            "Blend until smooth and creamy.",
            "Add ice cubes and blend again briefly.",
            "Pour into glasses and serve immediately.",
        ],
        "image_url": None,
    },
    {
        "id": 7,
        "name": "Crispy Spring Rolls",
        "description": "Golden fried spring rolls stuffed with vegetables.",
        "category": "snacks",
        "prep_time": "20 min",
        "cook_time": "10 min",
        "servings": 6,
        "ingredients": [
            "12 spring roll wrappers",
            "2 cups shredded cabbage",
            "1 cup shredded carrots",
            "1 cup bean sprouts",
            "2 tbsp soy sauce",
            "1 tsp sesame oil",
            "Oil for frying",
        ],
        "instructions": [
            "Mix cabbage, carrots, and bean sprouts with soy sauce and sesame oil.",
            "Place filling on each spring roll wrapper and roll tightly.",
            "Seal edges with water.",
            "Deep fry in hot oil until golden brown and crispy.",
            "Serve with sweet chili sauce.",
        ],
        "image_url": None,
    },
    {
        "id": 8,
        "name": "Chocolate Lava Cake",
        "description": "Decadent chocolate cake with a molten center.",
        "category": "desserts",
        "prep_time": "15 min",
        "cook_time": "12 min",
        "servings": 4,
        "ingredients": [
            "200g dark chocolate",
            "100g butter",
            "2 eggs",
            "2 egg yolks",
            "¼ cup sugar",
            "2 tbsp flour",
            "Cocoa powder for dusting",
        ],
        "instructions": [
            "Melt chocolate and butter together.",
            "Whisk eggs, egg yolks, and sugar until thick.",
            "Fold in the chocolate mixture and flour.",
            "Pour into greased ramekins.",
            "Bake at 220°C (425°F) for 12 minutes.",
            "Invert onto plates and dust with cocoa powder.",
        ],
        "image_url": None,
    },
    {
        "id": 9,
        "name": "Greek Salad",
        "description": "Fresh Mediterranean salad with feta and olives.",
        "category": "salads",
        "prep_time": "10 min",
        "cook_time": "0 min",
        "servings": 2,
        "ingredients": [
            "2 tomatoes, chopped",
            "1 cucumber, sliced",
            "½ red onion, sliced",
            "100g feta cheese",
            "½ cup Kalamata olives",
            "2 tbsp olive oil",
            "1 tbsp red wine vinegar",
            "Dried oregano",
        ],
        "instructions": [
            "Combine tomatoes, cucumber, and red onion in a bowl.",
            "Add olives and crumbled feta cheese.",
            "Drizzle with olive oil and red wine vinegar.",
            "Sprinkle with dried oregano and toss gently.",
        ],
        "image_url": None,
    },
    {
        "id": 10,
        "name": "Butter Chicken",
        "description": "Rich and creamy North Indian butter chicken curry.",
        "category": "dinner",
        "prep_time": "15 min",
        "cook_time": "25 min",
        "servings": 4,
        "ingredients": [
            "500g chicken thighs, cubed",
            "2 tbsp butter",
            "1 onion, diced",
            "3 cloves garlic, minced",
            "1 tbsp ginger paste",
            "400g canned tomatoes",
            "1 cup heavy cream",
            "2 tsp garam masala",
            "1 tsp turmeric",
            "1 tsp chili powder",
            "Fresh cilantro",
        ],
        "instructions": [
            "Cook chicken in butter until browned.",
            "Add onion, garlic, and ginger, cook until fragrant.",
            "Stir in spices and cook for 1 minute.",
            "Add canned tomatoes and simmer for 15 minutes.",
            "Stir in heavy cream and simmer for 5 more minutes.",
            "Garnish with cilantro and serve with naan or rice.",
        ],
        "image_url": None,
    },
    {
        "id": 11,
        "name": "Masala Chai",
        "description": "Aromatic Indian spiced tea with milk.",
        "category": "drinks",
        "prep_time": "5 min",
        "cook_time": "10 min",
        "servings": 2,
        "ingredients": [
            "2 cups water",
            "1 cup milk",
            "2 tsp loose black tea",
            "2 cardamom pods, crushed",
            "1 small cinnamon stick",
            "2 cloves",
            "1 inch ginger, sliced",
            "2 tbsp sugar",
        ],
        "instructions": [
            "Bring water to a boil with cardamom, cinnamon, cloves, and ginger.",
            "Add tea leaves and simmer for 3 minutes.",
            "Add milk and sugar, bring to a boil again.",
            "Strain into cups and serve hot.",
        ],
        "image_url": None,
    },
    {
        "id": 12,
        "name": "Samosa",
        "description": "Crispy fried pastry filled with spiced potatoes and peas.",
        "category": "snacks",
        "prep_time": "30 min",
        "cook_time": "15 min",
        "servings": 8,
        "ingredients": [
            "2 cups all-purpose flour",
            "4 tbsp oil",
            "Water for dough",
            "3 potatoes, boiled and mashed",
            "½ cup green peas",
            "1 tsp cumin seeds",
            "1 tsp garam masala",
            "1 tsp chili powder",
            "Salt to taste",
            "Oil for frying",
        ],
        "instructions": [
            "Make dough with flour, oil, salt, and water. Rest for 20 minutes.",
            "Cook peas with cumin seeds and spices.",
            "Mix with mashed potatoes for the filling.",
            "Roll dough into circles, cut in half, form cones and fill.",
            "Deep fry on medium heat until golden and crispy.",
            "Serve with mint and tamarind chutney.",
        ],
        "image_url": None,
    },
    {
        "id": 13,
        "name": "Tiramisu",
        "description": "Classic Italian layered dessert with coffee and mascarpone.",
        "category": "desserts",
        "prep_time": "30 min",
        "cook_time": "0 min",
        "servings": 6,
        "ingredients": [
            "6 egg yolks",
            "¾ cup sugar",
            "500g mascarpone cheese",
            "2 cups heavy cream",
            "2 cups strong espresso, cooled",
            "3 tbsp coffee liqueur (optional)",
            "24 ladyfinger biscuits",
            "Cocoa powder for dusting",
        ],
        "instructions": [
            "Whisk egg yolks and sugar until thick and pale.",
            "Add mascarpone and mix until smooth.",
            "Whip heavy cream and fold into mascarpone mixture.",
            "Mix espresso with coffee liqueur.",
            "Dip ladyfingers briefly in espresso and layer in a dish.",
            "Spread half the mascarpone mixture over the ladyfingers.",
            "Repeat layers and refrigerate for at least 4 hours.",
            "Dust with cocoa powder before serving.",
        ],
        "image_url": None,
    },
    {
        "id": 14,
        "name": "Chicken Wrap",
        "description": "Quick and delicious grilled chicken wrap for lunch.",
        "category": "lunch",
        "prep_time": "10 min",
        "cook_time": "10 min",
        "servings": 2,
        "ingredients": [
            "2 large tortillas",
            "2 grilled chicken breasts, sliced",
            "1 cup lettuce, shredded",
            "1 tomato, sliced",
            "½ cup shredded cheese",
            "2 tbsp ranch dressing",
        ],
        "instructions": [
            "Warm tortillas on a skillet.",
            "Layer lettuce, sliced chicken, tomato, and cheese on each tortilla.",
            "Drizzle with ranch dressing.",
            "Fold and roll tightly.",
            "Slice in half and serve.",
        ],
        "image_url": None,
    },
]


# Pre-compute categories from recipe data
def get_all_categories():
    """Get all unique categories with their recipe counts."""
    category_counts = {}
    for recipe in RECIPES:
        cat = recipe["category"]
        if cat not in category_counts:
            category_counts[cat] = 0
        category_counts[cat] += 1

    category_descriptions = {
        "breakfast": "Start your day right with delicious breakfast recipes.",
        "lunch": "Satisfying midday meals to keep you going.",
        "dinner": "Hearty dinner recipes for the whole family.",
        "snacks": "Quick and tasty bites for any time of day.",
        "desserts": "Sweet treats and indulgent desserts.",
        "drinks": "Refreshing beverages and warm drinks.",
        "salads": "Fresh and healthy salad recipes.",
    }

    return [
        {
            "name": cat,
            "description": category_descriptions.get(cat, f"Delicious {cat} recipes."),
            "recipe_count": count,
        }
        for cat, count in sorted(category_counts.items())
    ]


def get_recipes_by_category(category: str):
    """Get all recipes in a specific category."""
    return [r for r in RECIPES if r["category"].lower() == category.lower()]


def get_recipe_by_id(recipe_id: int):
    """Get a single recipe by its ID."""
    for recipe in RECIPES:
        if recipe["id"] == recipe_id:
            return recipe
    return None


def search_recipes(query: str):
    """Search recipes by name or description."""
    query_lower = query.lower()
    return [
        r
        for r in RECIPES
        if query_lower in r["name"].lower() or query_lower in r["description"].lower()
    ]
