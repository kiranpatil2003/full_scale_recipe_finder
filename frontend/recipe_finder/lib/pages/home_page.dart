import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:recipe_finder/models/recipe.dart';
import 'package:recipe_finder/services/recipe_service.dart';
import 'package:recipe_finder/services/favorites_service.dart';
import 'package:recipe_finder/widgets/recipe_card.dart';
import 'package:recipe_finder/widgets/category_chip.dart';
import 'package:recipe_finder/pages/recipe_detail_page.dart';
import 'package:recipe_finder/pages/category_recipes_page.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  List<Recipe> _recipes = [];
  bool _isLoading = true;
  String? _error;
  String _selectedCategory = 'all';
  final Set<int> _favoriteIds = {};

  final List<String> _categories = [
    'all', 'breakfast', 'lunch', 'dinner', 'snacks', 'desserts', 'drinks', 'salads'
  ];

  @override
  void initState() {
    super.initState();
    _loadRecipes();
    _loadFavorites();
  }

  Future<void> _loadRecipes() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });
    try {
      final recipes = await RecipeService.getRecipes(
        category: _selectedCategory == 'all' ? null : _selectedCategory,
        limit: 50,
      );
      if (mounted) {
        setState(() {
          _recipes = recipes;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString();
          _isLoading = false;
        });
      }
    }
  }

  Future<void> _loadFavorites() async {
    try {
      final favorites = await FavoritesService.getFavorites();
      if (mounted) {
        setState(() {
          _favoriteIds.clear();
          for (var r in favorites) {
            if (r.id != null) _favoriteIds.add(r.id!);
          }
        });
      }
    } catch (_) {}
  }

  Future<void> _toggleFavorite(Recipe recipe) async {
    if (recipe.id == null) return;
    try {
      if (_favoriteIds.contains(recipe.id)) {
        await FavoritesService.removeFavorite(recipe.id!);
        setState(() => _favoriteIds.remove(recipe.id));
      } else {
        await FavoritesService.addFavorite(recipe.id!);
        setState(() => _favoriteIds.add(recipe.id!));
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
    final user = FirebaseAuth.instance.currentUser;

    return Scaffold(
      backgroundColor: const Color(0xFFF8F9FA),
      body: SafeArea(
        child: RefreshIndicator(
          color: const Color(0xFFFF6B35),
          onRefresh: () async {
            await _loadRecipes();
            await _loadFavorites();
          },
          child: CustomScrollView(
            slivers: [
              // Header
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(20, 20, 20, 0),
                  child: Row(
                    children: [
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Hello, ${user?.displayName?.split(' ').first ?? 'Chef'} 👋',
                              style: const TextStyle(
                                fontSize: 24,
                                fontWeight: FontWeight.w800,
                                color: Color(0xFF1F2937),
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              'What would you like to cook today?',
                              style: TextStyle(
                                fontSize: 14,
                                color: Colors.grey.shade500,
                              ),
                            ),
                          ],
                        ),
                      ),
                      CircleAvatar(
                        radius: 22,
                        backgroundColor: const Color(0xFFFF6B35).withValues(alpha: 0.1),
                        backgroundImage: user?.photoURL != null
                            ? NetworkImage(user!.photoURL!)
                            : null,
                        child: user?.photoURL == null
                            ? const Icon(Icons.person, color: Color(0xFFFF6B35))
                            : null,
                      ),
                    ],
                  ),
                ),
              ),

              // Category Chips
              SliverToBoxAdapter(
                child: SizedBox(
                  height: 60,
                  child: ListView.separated(
                    scrollDirection: Axis.horizontal,
                    padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
                    itemCount: _categories.length,
                    separatorBuilder: (_, __) => const SizedBox(width: 8),
                    itemBuilder: (context, index) {
                      final cat = _categories[index];
                      return CategoryChip(
                        label: cat,
                        isSelected: cat == _selectedCategory,
                        onTap: () {
                          setState(() => _selectedCategory = cat);
                          _loadRecipes();
                        },
                      );
                    },
                  ),
                ),
              ),

              // Section header
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(20, 12, 20, 8),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        _selectedCategory == 'all'
                            ? 'All Recipes'
                            : '${_selectedCategory[0].toUpperCase()}${_selectedCategory.substring(1)} Recipes',
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.w700,
                          color: Color(0xFF1F2937),
                        ),
                      ),
                      if (_selectedCategory != 'all')
                        GestureDetector(
                          onTap: () {
                            Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (_) => CategoryRecipesPage(
                                  category: _selectedCategory,
                                ),
                              ),
                            );
                          },
                          child: const Text(
                            'See All →',
                            style: TextStyle(
                              fontSize: 13,
                              fontWeight: FontWeight.w600,
                              color: Color(0xFFFF6B35),
                            ),
                          ),
                        ),
                    ],
                  ),
                ),
              ),

              // Content
              if (_isLoading)
                const SliverFillRemaining(
                  child: Center(
                    child: CircularProgressIndicator(color: Color(0xFFFF6B35)),
                  ),
                )
              else if (_error != null)
                SliverFillRemaining(
                  child: Center(
                    child: Padding(
                      padding: const EdgeInsets.all(32),
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(Icons.cloud_off, size: 64, color: Colors.grey.shade300),
                          const SizedBox(height: 16),
                          Text(
                            'Could not load recipes',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w600,
                              color: Colors.grey.shade600,
                            ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            _error!,
                            textAlign: TextAlign.center,
                            style: TextStyle(fontSize: 12, color: Colors.grey.shade400),
                          ),
                          const SizedBox(height: 20),
                          ElevatedButton(
                            onPressed: _loadRecipes,
                            style: ElevatedButton.styleFrom(
                              backgroundColor: const Color(0xFFFF6B35),
                              foregroundColor: Colors.white,
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(12),
                              ),
                            ),
                            child: const Text('Retry'),
                          ),
                        ],
                      ),
                    ),
                  ),
                )
              else if (_recipes.isEmpty)
                SliverFillRemaining(
                  child: Center(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.restaurant_menu, size: 64, color: Colors.grey.shade300),
                        const SizedBox(height: 16),
                        Text(
                          'No recipes found',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w600,
                            color: Colors.grey.shade600,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Try searching or changing the category',
                          style: TextStyle(fontSize: 13, color: Colors.grey.shade400),
                        ),
                      ],
                    ),
                  ),
                )
              else
                SliverPadding(
                  padding: const EdgeInsets.fromLTRB(20, 0, 20, 20),
                  sliver: SliverGrid(
                    gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                      crossAxisCount: 2,
                      mainAxisSpacing: 14,
                      crossAxisSpacing: 14,
                      childAspectRatio: 0.68,
                    ),
                    delegate: SliverChildBuilderDelegate(
                      (context, index) {
                        final recipe = _recipes[index];
                        return RecipeCard(
                          recipe: recipe,
                          isFavorite: recipe.id != null && _favoriteIds.contains(recipe.id),
                          onTap: () async {
                            await Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (_) => RecipeDetailPage(recipe: recipe),
                              ),
                            );
                            _loadFavorites();
                          },
                          onFavorite: () => _toggleFavorite(recipe),
                        );
                      },
                      childCount: _recipes.length,
                    ),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}
