class Recipe {
  final int? id;
  final String name;
  final String description;
  final String category;
  final String prepTime;
  final String cookTime;
  final int servings;
  final List<String> ingredients;
  final List<String> instructions;
  final String? imageUrl;
  final String source;
  final String externalId;
  final List<String> allergens;
  final List<String> dietLabels;
  final double? matchScore;
  final List<String>? matchedIngredients;
  final List<String>? missingIngredients;

  Recipe({
    this.id,
    required this.name,
    this.description = '',
    this.category = 'other',
    this.prepTime = '',
    this.cookTime = '',
    this.servings = 1,
    this.ingredients = const [],
    this.instructions = const [],
    this.imageUrl,
    this.source = 'manual',
    this.externalId = '',
    this.allergens = const [],
    this.dietLabels = const [],
    this.matchScore,
    this.matchedIngredients,
    this.missingIngredients,
  });

  factory Recipe.fromJson(Map<String, dynamic> json) {
    return Recipe(
      id: json['id'] as int?,
      name: json['name'] as String? ?? 'Unknown',
      description: json['description'] as String? ?? '',
      category: json['category'] as String? ?? 'other',
      prepTime: json['prep_time'] as String? ?? '',
      cookTime: json['cook_time'] as String? ?? '',
      servings: json['servings'] as int? ?? 1,
      ingredients: (json['ingredients'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
      instructions: (json['instructions'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
      imageUrl: json['image_url'] as String?,
      source: json['source'] as String? ?? 'manual',
      externalId: json['external_id'] as String? ?? '',
      allergens: (json['allergens'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
      dietLabels: (json['diet_labels'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
      matchScore: (json['match_score'] as num?)?.toDouble(),
      matchedIngredients: (json['matched_ingredients'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList(),
      missingIngredients: (json['missing_ingredients'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'category': category,
      'prep_time': prepTime,
      'cook_time': cookTime,
      'servings': servings,
      'ingredients': ingredients,
      'instructions': instructions,
      'image_url': imageUrl,
      'source': source,
      'external_id': externalId,
      'allergens': allergens,
      'diet_labels': dietLabels,
      'match_score': matchScore,
      'matched_ingredients': matchedIngredients,
      'missing_ingredients': missingIngredients,
    };
  }
}
