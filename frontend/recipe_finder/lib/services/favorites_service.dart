import 'dart:convert';
import 'package:recipe_finder/models/recipe.dart';
import 'package:recipe_finder/services/api_service.dart';

class FavoritesService {
  /// Get all favorites
  static Future<List<Recipe>> getFavorites() async {
    final response = await ApiService.get('/favorites/');
    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((json) => Recipe.fromJson(json)).toList();
    }
    throw Exception('Failed to load favorites: ${response.statusCode}');
  }

  /// Add a recipe to favorites
  static Future<String> addFavorite(int recipeId) async {
    final response = await ApiService.post('/favorites/$recipeId');
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['message'];
    }
    throw Exception('Failed to add favorite: ${response.statusCode}');
  }

  /// Remove a recipe from favorites
  static Future<String> removeFavorite(int recipeId) async {
    final response = await ApiService.delete('/favorites/$recipeId');
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['message'];
    }
    throw Exception('Failed to remove favorite: ${response.statusCode}');
  }

  /// Check if a recipe is favorited
  static Future<bool> isFavorite(int recipeId) async {
    final response = await ApiService.get('/favorites/check/$recipeId');
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['is_favorite'] ?? false;
    }
    return false;
  }
}
