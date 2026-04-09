import 'package:flutter/material.dart';
import 'package:recipe_finder/models/recipe.dart';
import 'package:recipe_finder/services/recipe_service.dart';
import 'package:recipe_finder/widgets/recipe_card.dart';
import 'package:recipe_finder/pages/recipe_detail_page.dart';

class SearchPage extends StatefulWidget {
  const SearchPage({super.key});

  @override
  State<SearchPage> createState() => _SearchPageState();
}

class _SearchPageState extends State<SearchPage> {
  final TextEditingController _searchController = TextEditingController();
  final TextEditingController _ingredientController = TextEditingController();
  List<Recipe> _results = [];
  bool _isLoading = false;
  String? _error;
  bool _isIngredientMode = false;
  List<String> _selectedIngredients = [];

  final List<String> _commonIngredients = [
    'Chicken', 'Rice', 'Tomato', 'Onion', 'Garlic',
    'Potato', 'Egg', 'Cheese', 'Butter', 'Milk',
    'Pasta', 'Beef', 'Carrot', 'Ginger', 'Lemon',
  ];

  Future<void> _searchByName() async {
    final query = _searchController.text.trim();
    if (query.isEmpty) return;

    setState(() { _isLoading = true; _error = null; });
    try {
      final results = await RecipeService.searchRecipes(query);
      if (mounted) setState(() { _results = results; _isLoading = false; });
    } catch (e) {
      if (mounted) setState(() { _error = e.toString(); _isLoading = false; });
    }
  }

  Future<void> _searchByIngredients() async {
    if (_selectedIngredients.isEmpty) return;

    setState(() { _isLoading = true; _error = null; });
    try {
      final results = await RecipeService.searchByIngredients(_selectedIngredients);
      if (mounted) setState(() { _results = results; _isLoading = false; });
    } catch (e) {
      if (mounted) setState(() { _error = e.toString(); _isLoading = false; });
    }
  }

  void _addIngredient(String ingredient) {
    if (!_selectedIngredients.contains(ingredient)) {
      setState(() => _selectedIngredients.add(ingredient));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8F9FA),
      body: SafeArea(
        child: Column(
          children: [
            // Header
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 20, 20, 0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Search Recipes 🔍',
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.w800,
                      color: Color(0xFF1F2937),
                    ),
                  ),
                  const SizedBox(height: 16),
                  // Mode toggle
                  Row(
                    children: [
                      _ModeChip(
                        label: 'By Name',
                        icon: Icons.text_fields,
                        isSelected: !_isIngredientMode,
                        onTap: () => setState(() => _isIngredientMode = false),
                      ),
                      const SizedBox(width: 10),
                      _ModeChip(
                        label: 'By Ingredients',
                        icon: Icons.shopping_basket,
                        isSelected: _isIngredientMode,
                        onTap: () => setState(() => _isIngredientMode = true),
                      ),
                    ],
                  ),
                  const SizedBox(height: 14),

                  if (!_isIngredientMode) ...[
                    // Name search bar
                    TextField(
                      controller: _searchController,
                      onSubmitted: (_) => _searchByName(),
                      decoration: InputDecoration(
                        hintText: 'Search for pasta, chicken, cake...',
                        hintStyle: TextStyle(color: Colors.grey.shade400),
                        prefixIcon: const Icon(Icons.search, color: Color(0xFFFF6B35)),
                        suffixIcon: IconButton(
                          icon: const Icon(Icons.arrow_forward, color: Color(0xFFFF6B35)),
                          onPressed: _searchByName,
                        ),
                        filled: true,
                        fillColor: Colors.white,
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(16),
                          borderSide: BorderSide.none,
                        ),
                        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                      ),
                    ),
                  ] else ...[
                    // Ingredient input
                    Row(
                      children: [
                        Expanded(
                          child: TextField(
                            controller: _ingredientController,
                            onSubmitted: (val) {
                              if (val.trim().isNotEmpty) {
                                _addIngredient(val.trim());
                                _ingredientController.clear();
                              }
                            },
                            decoration: InputDecoration(
                              hintText: 'Add an ingredient...',
                              hintStyle: TextStyle(color: Colors.grey.shade400),
                              prefixIcon: const Icon(Icons.add_circle_outline, color: Color(0xFFFF6B35)),
                              filled: true,
                              fillColor: Colors.white,
                              border: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(16),
                                borderSide: BorderSide.none,
                              ),
                              contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                            ),
                          ),
                        ),
                        const SizedBox(width: 10),
                        ElevatedButton(
                          onPressed: _searchByIngredients,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFFFF6B35),
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.all(14),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                          ),
                          child: const Icon(Icons.search),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),
                    // Selected ingredients
                    if (_selectedIngredients.isNotEmpty)
                      Wrap(
                        spacing: 6,
                        runSpacing: 6,
                        children: _selectedIngredients.map((ing) {
                          return Chip(
                            label: Text(ing, style: const TextStyle(fontSize: 12)),
                            deleteIcon: const Icon(Icons.close, size: 16),
                            onDeleted: () {
                              setState(() => _selectedIngredients.remove(ing));
                            },
                            backgroundColor: const Color(0xFFFF6B35).withValues(alpha: 0.1),
                            side: BorderSide.none,
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
                          );
                        }).toList(),
                      ),
                    const SizedBox(height: 10),
                    // Quick ingredient suggestions
                    SizedBox(
                      height: 34,
                      child: ListView.separated(
                        scrollDirection: Axis.horizontal,
                        itemCount: _commonIngredients.length,
                        separatorBuilder: (_, __) => const SizedBox(width: 6),
                        itemBuilder: (context, index) {
                          final ing = _commonIngredients[index];
                          final isAdded = _selectedIngredients.contains(ing);
                          return GestureDetector(
                            onTap: isAdded ? null : () => _addIngredient(ing),
                            child: Container(
                              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                              decoration: BoxDecoration(
                                color: isAdded ? Colors.grey.shade200 : Colors.white,
                                borderRadius: BorderRadius.circular(20),
                                border: Border.all(color: Colors.grey.shade300),
                              ),
                              child: Text(
                                ing,
                                style: TextStyle(
                                  fontSize: 12,
                                  color: isAdded ? Colors.grey.shade400 : Colors.grey.shade700,
                                ),
                              ),
                            ),
                          );
                        },
                      ),
                    ),
                  ],
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Results
            Expanded(
              child: _isLoading
                  ? const Center(child: CircularProgressIndicator(color: Color(0xFFFF6B35)))
                  : _error != null
                      ? Center(
                          child: Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(Icons.error_outline, size: 48, color: Colors.grey.shade300),
                              const SizedBox(height: 12),
                              Text('Search failed', style: TextStyle(color: Colors.grey.shade600)),
                            ],
                          ),
                        )
                      : _results.isEmpty
                          ? Center(
                              child: Column(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Icon(
                                    _isIngredientMode ? Icons.shopping_basket : Icons.search,
                                    size: 64,
                                    color: Colors.grey.shade300,
                                  ),
                                  const SizedBox(height: 16),
                                  Text(
                                    _isIngredientMode
                                        ? 'Add ingredients & search'
                                        : 'Search for your favorite recipes',
                                    style: TextStyle(
                                      fontSize: 15,
                                      color: Colors.grey.shade500,
                                    ),
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
                              itemCount: _results.length,
                              itemBuilder: (context, index) {
                                return RecipeCard(
                                  recipe: _results[index],
                                  onTap: () {
                                    Navigator.push(
                                      context,
                                      MaterialPageRoute(
                                        builder: (_) => RecipeDetailPage(recipe: _results[index]),
                                      ),
                                    );
                                  },
                                );
                              },
                            ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ModeChip extends StatelessWidget {
  final String label;
  final IconData icon;
  final bool isSelected;
  final VoidCallback onTap;

  const _ModeChip({
    required this.label,
    required this.icon,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
        decoration: BoxDecoration(
          color: isSelected ? const Color(0xFFFF6B35) : Colors.white,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: isSelected ? const Color(0xFFFF6B35) : Colors.grey.shade300,
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 16, color: isSelected ? Colors.white : Colors.grey.shade600),
            const SizedBox(width: 6),
            Text(
              label,
              style: TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w600,
                color: isSelected ? Colors.white : Colors.grey.shade600,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
