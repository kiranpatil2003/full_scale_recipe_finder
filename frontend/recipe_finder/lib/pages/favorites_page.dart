import 'package:flutter/material.dart';
import 'package:recipe_finder/models/recipe.dart';
import 'package:recipe_finder/services/favorites_service.dart';
import 'package:recipe_finder/widgets/recipe_card.dart';
import 'package:recipe_finder/pages/recipe_detail_page.dart';

class FavoritesPage extends StatefulWidget {
  const FavoritesPage({super.key});

  @override
  State<FavoritesPage> createState() => _FavoritesPageState();
}

class _FavoritesPageState extends State<FavoritesPage> {
  List<Recipe> _favorites = [];
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadFavorites();
  }

  Future<void> _loadFavorites() async {
    setState(() { _isLoading = true; _error = null; });
    try {
      final favorites = await FavoritesService.getFavorites();
      if (mounted) setState(() { _favorites = favorites; _isLoading = false; });
    } catch (e) {
      if (mounted) setState(() { _error = e.toString(); _isLoading = false; });
    }
  }

  Future<void> _removeFavorite(Recipe recipe) async {
    if (recipe.id == null) return;
    try {
      await FavoritesService.removeFavorite(recipe.id!);
      setState(() => _favorites.removeWhere((r) => r.id == recipe.id));
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Removed "${recipe.name}" from favorites'),
            behavior: SnackBarBehavior.floating,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8F9FA),
      body: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Padding(
              padding: EdgeInsets.fromLTRB(20, 20, 20, 16),
              child: Text(
                'My Favorites ❤️',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.w800,
                  color: Color(0xFF1F2937),
                ),
              ),
            ),
            Expanded(
              child: RefreshIndicator(
                color: const Color(0xFFFF6B35),
                onRefresh: _loadFavorites,
                child: _isLoading
                    ? const Center(child: CircularProgressIndicator(color: Color(0xFFFF6B35)))
                    : _error != null
                        ? Center(
                            child: Column(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Icon(Icons.error_outline, size: 48, color: Colors.grey.shade300),
                                const SizedBox(height: 12),
                                Text('Failed to load favorites',
                                    style: TextStyle(color: Colors.grey.shade600)),
                                const SizedBox(height: 12),
                                ElevatedButton(
                                  onPressed: _loadFavorites,
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: const Color(0xFFFF6B35),
                                    foregroundColor: Colors.white,
                                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                                  ),
                                  child: const Text('Retry'),
                                ),
                              ],
                            ),
                          )
                        : _favorites.isEmpty
                            ? Center(
                                child: Column(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    Icon(Icons.favorite_border, size: 64, color: Colors.grey.shade300),
                                    const SizedBox(height: 16),
                                    Text(
                                      'No favorites yet',
                                      style: TextStyle(
                                        fontSize: 16,
                                        fontWeight: FontWeight.w600,
                                        color: Colors.grey.shade600,
                                      ),
                                    ),
                                    const SizedBox(height: 8),
                                    Text(
                                      'Start adding recipes you love!',
                                      style: TextStyle(fontSize: 13, color: Colors.grey.shade400),
                                    ),
                                  ],
                                ),
                              )
                            : GridView.builder(
                                padding: const EdgeInsets.fromLTRB(20, 0, 20, 20),
                                gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                                  crossAxisCount: 2,
                                  mainAxisSpacing: 14,
                                  crossAxisSpacing: 14,
                                  childAspectRatio: 0.68,
                                ),
                                itemCount: _favorites.length,
                                itemBuilder: (context, index) {
                                  final recipe = _favorites[index];
                                  return RecipeCard(
                                    recipe: recipe,
                                    isFavorite: true,
                                    onTap: () async {
                                      await Navigator.push(
                                        context,
                                        MaterialPageRoute(
                                          builder: (_) => RecipeDetailPage(recipe: recipe),
                                        ),
                                      );
                                      _loadFavorites();
                                    },
                                    onFavorite: () => _removeFavorite(recipe),
                                  );
                                },
                              ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
