import 'package:flutter/material.dart';
import 'package:recipe_finder/models/recipe.dart';
import 'package:recipe_finder/services/recipe_service.dart';
import 'package:recipe_finder/widgets/recipe_card.dart';
import 'package:recipe_finder/pages/recipe_detail_page.dart';

// ─── Nutrition field definition ──────────────────────────────────────────────

class _NutrientField {
  final String key;      // matches the backend column name
  final String label;    // human-readable
  final String unit;     // display unit
  final String group;    // category grouping

  const _NutrientField(this.key, this.label, this.unit, this.group);
}

const _nutrientFields = [
  // Macros
  _NutrientField('calories_kcal', 'Calories', 'kcal', 'Macros'),
  _NutrientField('protein_g', 'Protein', 'g', 'Macros'),
  _NutrientField('fat_total_g', 'Total Fat', 'g', 'Macros'),
  _NutrientField('carbohydrates_g', 'Carbs', 'g', 'Macros'),
  // Sugars & Fiber
  _NutrientField('fiber_g', 'Fiber', 'g', 'Sugars & Fiber'),
  _NutrientField('sugar_g', 'Sugar', 'g', 'Sugars & Fiber'),
  // Vitamins
  _NutrientField('vitamin_a_iu', 'Vitamin A', 'IU', 'Vitamins'),
  _NutrientField('vitamin_c_mg', 'Vitamin C', 'mg', 'Vitamins'),
  _NutrientField('vitamin_d_iu', 'Vitamin D', 'IU', 'Vitamins'),
  _NutrientField('vitamin_b12_mcg', 'Vitamin B12', 'mcg', 'Vitamins'),
  _NutrientField('folate_mcg', 'Folate', 'mcg', 'Vitamins'),
  // Minerals
  _NutrientField('sodium_mg', 'Sodium', 'mg', 'Minerals'),
  _NutrientField('potassium_mg', 'Potassium', 'mg', 'Minerals'),
  _NutrientField('calcium_mg', 'Calcium', 'mg', 'Minerals'),
  _NutrientField('iron_mg', 'Iron', 'mg', 'Minerals'),
  _NutrientField('zinc_mg', 'Zinc', 'mg', 'Minerals'),
  _NutrientField('magnesium_mg', 'Magnesium', 'mg', 'Minerals'),
  _NutrientField('phosphorus_mg', 'Phosphorus', 'mg', 'Minerals'),
  // Other
  _NutrientField('cholesterol_mg', 'Cholesterol', 'mg', 'Other'),
  _NutrientField('saturated_fat_g', 'Saturated Fat', 'g', 'Other'),
];

// ─── Search mode enum ────────────────────────────────────────────────────────

enum _SearchMode { name, ingredients, nutrition }

// ─── Search Page ─────────────────────────────────────────────────────────────

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
  _SearchMode _mode = _SearchMode.name;
  List<String> _selectedIngredients = [];
  bool _nutritionFiltersCollapsed = false;

  // Nutrition filter controllers (min & max for each field)
  final Map<String, TextEditingController> _minControllers = {};
  final Map<String, TextEditingController> _maxControllers = {};

  final List<String> _commonIngredients = [
    'Chicken', 'Rice', 'Tomato', 'Onion', 'Garlic',
    'Potato', 'Egg', 'Cheese', 'Butter', 'Milk',
    'Pasta', 'Beef', 'Carrot', 'Ginger', 'Lemon',
  ];

  @override
  void initState() {
    super.initState();
    for (final f in _nutrientFields) {
      _minControllers[f.key] = TextEditingController();
      _maxControllers[f.key] = TextEditingController();
    }
  }

  @override
  void dispose() {
    _searchController.dispose();
    _ingredientController.dispose();
    for (final c in _minControllers.values) {
      c.dispose();
    }
    for (final c in _maxControllers.values) {
      c.dispose();
    }
    super.dispose();
  }

  // ─── Search handlers ─────────────────────────────────────────────────────

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

  Future<void> _searchByNutrition() async {
    final filters = <String, String>{};
    for (final f in _nutrientFields) {
      final minVal = _minControllers[f.key]!.text.trim();
      final maxVal = _maxControllers[f.key]!.text.trim();
      if (minVal.isNotEmpty) filters['min_${f.key}'] = minVal;
      if (maxVal.isNotEmpty) filters['max_${f.key}'] = maxVal;
    }
    if (filters.isEmpty) {
      setState(() => _error = 'Please enter at least one nutrition filter.');
      return;
    }

    setState(() { _isLoading = true; _error = null; });
    try {
      final results = await RecipeService.searchByNutrition(filters);
      if (mounted) {
        setState(() {
          _results = results;
          _isLoading = false;
          _nutritionFiltersCollapsed = true;
        });
      }
    } catch (e) {
      if (mounted) setState(() { _error = e.toString(); _isLoading = false; });
    }
  }

  void _clearNutritionFilters() {
    for (final c in _minControllers.values) {
      c.clear();
    }
    for (final c in _maxControllers.values) {
      c.clear();
    }
    setState(() {});
  }

  void _addIngredient(String ingredient) {
    if (!_selectedIngredients.contains(ingredient)) {
      setState(() => _selectedIngredients.add(ingredient));
    }
  }

  // ─── Build ────────────────────────────────────────────────────────────────

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
                  SingleChildScrollView(
                    scrollDirection: Axis.horizontal,
                    child: Row(
                      children: [
                        _ModeChip(
                          label: 'By Name',
                          icon: Icons.text_fields,
                          isSelected: _mode == _SearchMode.name,
                          onTap: () => setState(() => _mode = _SearchMode.name),
                        ),
                        const SizedBox(width: 10),
                        _ModeChip(
                          label: 'By Ingredients',
                          icon: Icons.shopping_basket,
                          isSelected: _mode == _SearchMode.ingredients,
                          onTap: () => setState(() => _mode = _SearchMode.ingredients),
                        ),
                        const SizedBox(width: 10),
                        _ModeChip(
                          label: 'By Nutrition',
                          icon: Icons.monitor_heart,
                          isSelected: _mode == _SearchMode.nutrition,
                          onTap: () => setState(() => _mode = _SearchMode.nutrition),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 14),
                ],
              ),
            ),

            // ─── Search inputs area ─────────────────────────────────────
            if (_mode == _SearchMode.name) ...[
              _buildNameSearch(),
            ] else if (_mode == _SearchMode.ingredients) ...[
              _buildIngredientSearch(),
            ],

            // Nutrition mode gets a scrollable Expanded area
            if (_mode == _SearchMode.nutrition)
              Expanded(child: _buildNutritionSearch())
            else ...[
              const SizedBox(height: 16),
              // Results
              Expanded(child: _buildResults()),
            ],
          ],
        ),
      ),
    );
  }

  // ─── Name search bar ──────────────────────────────────────────────────────

  Widget _buildNameSearch() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: TextField(
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
    );
  }

  // ─── Ingredient search ────────────────────────────────────────────────────

  Widget _buildIngredientSearch() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: Column(
        children: [
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
                    prefixIcon: IconButton(
                      icon: const Icon(Icons.add_circle_outline, color: Color(0xFFFF6B35)),
                      onPressed: () {
                        final val = _ingredientController.text.trim();
                        if (val.isNotEmpty) {
                          _addIngredient(val);
                          _ingredientController.clear();
                        }
                      },
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
      ),
    );
  }

  // ─── Nutrition search ─────────────────────────────────────────────────────

  Widget _buildNutritionSearch() {
    // If collapsed (after a search), show filter button + results
    if (_nutritionFiltersCollapsed) {
      return Column(
        children: [
          // Compact filter bar
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20),
            child: Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () => setState(() => _nutritionFiltersCollapsed = false),
                    icon: const Icon(Icons.tune, size: 18),
                    label: Text(
                      'Filters (${_activeFilterCount()} active)',
                      style: const TextStyle(fontSize: 13),
                    ),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFFFF6B35).withValues(alpha: 0.1),
                      foregroundColor: const Color(0xFFFF6B35),
                      elevation: 0,
                      padding: const EdgeInsets.symmetric(vertical: 12),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(14),
                        side: const BorderSide(color: Color(0xFFFF6B35), width: 1),
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                OutlinedButton.icon(
                  onPressed: () {
                    _clearNutritionFilters();
                    setState(() {
                      _results = [];
                      _error = null;
                      _nutritionFiltersCollapsed = false;
                    });
                  },
                  icon: const Icon(Icons.clear_all, size: 18),
                  label: const Text('Reset'),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: Colors.grey.shade600,
                    side: BorderSide(color: Colors.grey.shade300),
                    padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(14),
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 12),
          // Results take the rest
          Expanded(child: _buildResults()),
        ],
      );
    }

    // Expanded: show full filter form
    // Group fields
    final groups = <String, List<_NutrientField>>{};
    for (final f in _nutrientFields) {
      groups.putIfAbsent(f.group, () => []).add(f);
    }

    return ListView(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      children: [
        for (final group in groups.entries) ...[
          _buildGroupHeader(group.key),
          ...group.value.map((f) => _buildNutrientRow(f)),
          const SizedBox(height: 8),
        ],
        const SizedBox(height: 12),
        // Search & Clear buttons
        Row(
          children: [
            Expanded(
              child: ElevatedButton.icon(
                onPressed: _isLoading ? null : _searchByNutrition,
                icon: _isLoading
                    ? const SizedBox(
                        width: 18,
                        height: 18,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: Colors.white,
                        ),
                      )
                    : const Icon(Icons.search, size: 18),
                label: Text(_isLoading ? 'Searching...' : 'Search'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFFFF6B35),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14),
                  ),
                  elevation: 0,
                ),
              ),
            ),
            const SizedBox(width: 12),
            OutlinedButton.icon(
              onPressed: _clearNutritionFilters,
              icon: const Icon(Icons.clear_all, size: 18),
              label: const Text('Clear'),
              style: OutlinedButton.styleFrom(
                foregroundColor: Colors.grey.shade600,
                side: BorderSide(color: Colors.grey.shade300),
                padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 20),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(14),
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
      ],
    );
  }

  int _activeFilterCount() {
    int count = 0;
    for (final f in _nutrientFields) {
      if (_minControllers[f.key]!.text.trim().isNotEmpty) count++;
      if (_maxControllers[f.key]!.text.trim().isNotEmpty) count++;
    }
    return count;
  }

  Widget _buildGroupHeader(String title) {
    IconData icon;
    Color color;
    switch (title) {
      case 'Macros':
        icon = Icons.local_fire_department;
        color = const Color(0xFFFF6B35);
        break;
      case 'Sugars & Fiber':
        icon = Icons.grain;
        color = const Color(0xFF8B5CF6);
        break;
      case 'Vitamins':
        icon = Icons.wb_sunny;
        color = const Color(0xFF10B981);
        break;
      case 'Minerals':
        icon = Icons.diamond;
        color = const Color(0xFF3B82F6);
        break;
      default:
        icon = Icons.science;
        color = const Color(0xFF6B7280);
    }

    return Padding(
      padding: const EdgeInsets.only(top: 12, bottom: 8),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(6),
            decoration: BoxDecoration(
              color: color.withValues(alpha: 0.12),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(icon, size: 16, color: color),
          ),
          const SizedBox(width: 10),
          Text(
            title,
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w700,
              color: color,
              letterSpacing: 0.5,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildNutrientRow(_NutrientField field) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Row(
        children: [
          // Label
          SizedBox(
            width: 110,
            child: Text(
              '${field.label} (${field.unit})',
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey.shade700,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
          const SizedBox(width: 8),
          // Min field
          Expanded(
            child: _NutrientTextField(
              controller: _minControllers[field.key]!,
              hint: 'Min',
            ),
          ),
          const SizedBox(width: 8),
          Icon(Icons.remove, size: 14, color: Colors.grey.shade400),
          const SizedBox(width: 8),
          // Max field
          Expanded(
            child: _NutrientTextField(
              controller: _maxControllers[field.key]!,
              hint: 'Max',
            ),
          ),
        ],
      ),
    );
  }

  // ─── Results grid ─────────────────────────────────────────────────────────

  Widget _buildResults() {
    if (_isLoading) {
      return const Center(
        child: CircularProgressIndicator(color: Color(0xFFFF6B35)),
      );
    }

    if (_error != null) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.error_outline, size: 48, color: Colors.grey.shade300),
            const SizedBox(height: 12),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 32),
              child: Text(
                _error!.replaceAll('Exception: ', ''),
                textAlign: TextAlign.center,
                style: TextStyle(color: Colors.grey.shade600, fontSize: 13),
              ),
            ),
          ],
        ),
      );
    }

    if (_results.isEmpty) {
      IconData emptyIcon;
      String emptyText;
      switch (_mode) {
        case _SearchMode.ingredients:
          emptyIcon = Icons.shopping_basket;
          emptyText = 'Add ingredients & search';
          break;
        case _SearchMode.nutrition:
          emptyIcon = Icons.monitor_heart;
          emptyText = 'Set nutrition filters & search';
          break;
        default:
          emptyIcon = Icons.search;
          emptyText = 'Search for your favorite recipes';
      }
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(emptyIcon, size: 64, color: Colors.grey.shade300),
            const SizedBox(height: 16),
            Text(
              emptyText,
              style: TextStyle(fontSize: 15, color: Colors.grey.shade500),
            ),
          ],
        ),
      );
    }

    return GridView.builder(
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
    );
  }
}

// ─── Shared widgets ──────────────────────────────────────────────────────────

class _NutrientTextField extends StatelessWidget {
  final TextEditingController controller;
  final String hint;

  const _NutrientTextField({required this.controller, required this.hint});

  @override
  Widget build(BuildContext context) {
    return TextField(
      controller: controller,
      keyboardType: const TextInputType.numberWithOptions(decimal: true),
      style: const TextStyle(fontSize: 13),
      decoration: InputDecoration(
        hintText: hint,
        hintStyle: TextStyle(fontSize: 12, color: Colors.grey.shade400),
        filled: true,
        fillColor: Colors.white,
        isDense: true,
        contentPadding: const EdgeInsets.symmetric(horizontal: 10, vertical: 10),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: BorderSide(color: Colors.grey.shade200),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: BorderSide(color: Colors.grey.shade200),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: const BorderSide(color: Color(0xFFFF6B35), width: 1.5),
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
