class RecipeCategory {
  final String name;
  final String description;
  final int recipeCount;

  RecipeCategory({
    required this.name,
    this.description = '',
    this.recipeCount = 0,
  });

  factory RecipeCategory.fromJson(Map<String, dynamic> json) {
    return RecipeCategory(
      name: json['name'] as String? ?? 'other',
      description: json['description'] as String? ?? '',
      recipeCount: json['recipe_count'] as int? ?? 0,
    );
  }
}
