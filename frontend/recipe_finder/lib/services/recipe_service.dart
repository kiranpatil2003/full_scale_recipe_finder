import 'dart:convert';
import 'package:recipe_finder/models/recipe.dart';
import 'package:recipe_finder/models/category.dart';
import 'package:recipe_finder/services/api_service.dart';

class RecipeService {
  /// Get all recipes with optional category filter and pagination
  static Future<List<Recipe>> getRecipes({
    int limit = 20,
    int offset = 0,
    String? category,
  }) async {
    final params = {
      'limit': limit.toString(),
      'offset': offset.toString(),
      if (category != null) 'category': category,
    };
    final response = await ApiService.get('/recipes/', queryParams: params);
    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((json) => Recipe.fromJson(json)).toList();
    }
    throw Exception('Failed to load recipes: ${response.statusCode}');
  }

  /// Search recipes by query
  static Future<List<Recipe>> searchRecipes(String query) async {
    final response =
        await ApiService.get('/recipes/search', queryParams: {'q': query});
    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((json) => Recipe.fromJson(json)).toList();
    }
    throw Exception('Search failed: ${response.statusCode}');
  }

  /// Search recipes by ingredients
  static Future<List<Recipe>> searchByIngredients(
      List<String> ingredients) async {
    final response = await ApiService.get('/recipes/search-by-ingredients',
        queryParams: {'ingredients': ingredients.join(',')});
    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((json) => Recipe.fromJson(json)).toList();
    }
    throw Exception('Ingredient search failed: ${response.statusCode}');
  }

  /// Search recipes by nutrition filters (min/max values)
  static Future<List<Recipe>> searchByNutrition(
      Map<String, String> filters) async {
    final response = await ApiService.get('/recipes/search-by-nutrition',
        queryParams: filters);
    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((json) => Recipe.fromJson(json)).toList();
    }
    throw Exception('Nutrition search failed: ${response.statusCode}');
  }

  /// Get a single recipe by ID
  static Future<Recipe> getRecipeById(int id) async {
    final response = await ApiService.get('/recipes/$id');
    if (response.statusCode == 200) {
      return Recipe.fromJson(jsonDecode(response.body));
    }
    throw Exception('Recipe not found: ${response.statusCode}');
  }

  /// Get all categories
  static Future<List<RecipeCategory>> getCategories() async {
    final response = await ApiService.get('/categories/');
    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((json) => RecipeCategory.fromJson(json)).toList();
    }
    throw Exception('Failed to load categories: ${response.statusCode}');
  }
}
