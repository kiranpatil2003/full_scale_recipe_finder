import 'package:flutter/material.dart';
import 'package:recipe_finder/models/recipe.dart';
import 'package:recipe_finder/services/recipe_service.dart';
import 'package:recipe_finder/widgets/recipe_card.dart';
import 'package:recipe_finder/pages/recipe_detail_page.dart';

class CategoryRecipesPage extends StatefulWidget {
  final String category;

  const CategoryRecipesPage({super.key, required this.category});

  @override
  State<CategoryRecipesPage> createState() => _CategoryRecipesPageState();
}

class _CategoryRecipesPageState extends State<CategoryRecipesPage> {
  final ScrollController _scrollController = ScrollController();
  List<Recipe> _recipes = [];
  bool _isLoading = true;
  bool _isLoadingMore = false;
  bool _hasMore = true;
  int _offset = 0;
  final int _limit = 30;
  String? _error;

  @override
  void initState() {
    super.initState();
    _scrollController.addListener(_onScroll);
    _loadRecipes();
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  void _onScroll() {
    if (_scrollController.position.extentAfter < 500) {
      _loadMoreRecipes();
    }
  }

  Future<void> _loadRecipes() async {
    setState(() {
      _isLoading = true;
      _error = null;
      _offset = 0;
      _hasMore = true;
    });
    try {
      final recipes = await RecipeService.getRecipes(
        category: widget.category,
        limit: _limit,
        offset: _offset,
      );
      if (mounted) {
        setState(() {
          _recipes = recipes;
          _isLoading = false;
          _offset += recipes.length;
          // Only stop if we get absolutely nothing back
          if (recipes.isEmpty) _hasMore = false;
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

  Future<void> _loadMoreRecipes() async {
    if (_isLoadingMore || !_hasMore) return;

    setState(() => _isLoadingMore = true);

    try {
      final recipes = await RecipeService.getRecipes(
        category: widget.category,
        limit: _limit,
        offset: _offset,
      );
      if (mounted) {
        setState(() {
          _recipes.addAll(recipes);
          _isLoadingMore = false;
          _offset += recipes.length;
          // Only stop if we get absolutely nothing back
          if (recipes.isEmpty) _hasMore = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isLoadingMore = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final title = '${widget.category[0].toUpperCase()}${widget.category.substring(1)} Recipes';

    return Scaffold(
      backgroundColor: const Color(0xFFF8F9FA),
      appBar: AppBar(
        backgroundColor: Colors.white,
        foregroundColor: const Color(0xFF1F2937),
        elevation: 0,
        title: Text(
          title,
          style: const TextStyle(fontWeight: FontWeight.w700),
        ),
      ),
      body: RefreshIndicator(
        color: const Color(0xFFFF6B35),
        onRefresh: _loadRecipes,
        child: _isLoading
            ? const Center(child: CircularProgressIndicator(color: Color(0xFFFF6B35)))
            : _error != null
                ? Center(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.error_outline, size: 48, color: Colors.grey.shade300),
                        const SizedBox(height: 12),
                        Text('Failed to load', style: TextStyle(color: Colors.grey.shade600)),
                        ElevatedButton(
                          onPressed: _loadRecipes,
                          child: const Text('Retry'),
                        ),
                      ],
                    ),
                  )
                : _recipes.isEmpty
                    ? Center(
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(Icons.restaurant, size: 64, color: Colors.grey.shade300),
                            const SizedBox(height: 16),
                            Text(
                              'No $title found',
                              style: TextStyle(fontSize: 16, color: Colors.grey.shade600),
                            ),
                          ],
                        ),
                      )
                    : CustomScrollView(
                        controller: _scrollController,
                        physics: const AlwaysScrollableScrollPhysics(),
                        slivers: [
                          SliverPadding(
                            padding: const EdgeInsets.all(20),
                            sliver: SliverGrid(
                              gridDelegate:
                                  const SliverGridDelegateWithFixedCrossAxisCount(
                                crossAxisCount: 2,
                                mainAxisSpacing: 14,
                                crossAxisSpacing: 14,
                                childAspectRatio: 0.68,
                              ),
                              delegate: SliverChildBuilderDelegate(
                                (context, index) {
                                  return RecipeCard(
                                    recipe: _recipes[index],
                                    onTap: () {
                                      Navigator.push(
                                        context,
                                        MaterialPageRoute(
                                          builder: (_) => RecipeDetailPage(
                                              recipe: _recipes[index]),
                                        ),
                                      );
                                    },
                                  );
                                },
                                childCount: _recipes.length,
                              ),
                            ),
                          ),
                          if (_isLoadingMore)
                            const SliverToBoxAdapter(
                              child: Padding(
                                padding: EdgeInsets.symmetric(vertical: 20),
                                child: Center(
                                  child: CircularProgressIndicator(
                                      color: Color(0xFFFF6B35)),
                                ),
                              ),
                            ),
                          const SliverToBoxAdapter(child: SizedBox(height: 20)),
                        ],
                      ),
      ),
    );
  }
}
