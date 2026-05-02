import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter_html/flutter_html.dart';
import 'package:recipe_finder/models/recipe.dart';
import 'package:recipe_finder/models/user_profile.dart';
import 'package:recipe_finder/services/favorites_service.dart';
import 'package:recipe_finder/services/user_service.dart';

class RecipeDetailPage extends StatefulWidget {
  final Recipe recipe;

  const RecipeDetailPage({super.key, required this.recipe});

  @override
  State<RecipeDetailPage> createState() => _RecipeDetailPageState();
}

class _RecipeDetailPageState extends State<RecipeDetailPage> {
  bool _isFavorite = false;
  bool _loadingFav = false;
  UserProfile? _userProfile;

  @override
  void initState() {
    super.initState();
    _checkFavorite();
    _loadUserProfile();
  }

  Future<void> _loadUserProfile() async {
    try {
      final profile = await UserService.getProfile();
      if (mounted) setState(() => _userProfile = profile);
    } catch (_) {
      // If profile can't be loaded, warnings won't be shown
    }
  }

  /// Returns only the recipe allergens that match the user's saved allergies.
  List<String> _getRelevantAllergens() {
    if (_userProfile == null) return [];
    final userAllergies = _userProfile!.allergies
        .map((a) => a.toLowerCase().trim())
        .toSet();
    final userDietPrefs = _userProfile!.dietaryPreferences
        .map((p) => p.toLowerCase().trim())
        .toSet();
    // Combine allergies + dietary preferences for matching
    // e.g. user has "gluten-free" preference → warn about "gluten" allergen
    final sensitiveTerms = <String>{};
    sensitiveTerms.addAll(userAllergies);
    // Map dietary preferences to their related allergens
    for (final pref in userDietPrefs) {
      if (pref == 'gluten-free') sensitiveTerms.addAll(['gluten', 'wheat']);
      if (pref == 'dairy-free') sensitiveTerms.addAll(['dairy', 'milk', 'lactose']);
      if (pref == 'vegan') sensitiveTerms.addAll(['dairy', 'milk', 'eggs', 'egg', 'fish', 'shellfish', 'honey']);
      if (pref == 'vegetarian') sensitiveTerms.addAll(['fish', 'shellfish']);
    }

    return widget.recipe.allergens.where((allergen) {
      final lowerAllergen = allergen.toLowerCase().trim();
      return sensitiveTerms.any((term) =>
          lowerAllergen.contains(term) || term.contains(lowerAllergen));
    }).toList();
  }

  Future<void> _checkFavorite() async {
    if (widget.recipe.id == null) return;
    try {
      final result = await FavoritesService.isFavorite(widget.recipe.id!);
      if (mounted) setState(() => _isFavorite = result);
    } catch (_) {}
  }

  Future<void> _toggleFavorite() async {
    if (widget.recipe.id == null || _loadingFav) return;
    setState(() => _loadingFav = true);
    try {
      if (_isFavorite) {
        await FavoritesService.removeFavorite(widget.recipe.id!);
      } else {
        await FavoritesService.addFavorite(widget.recipe.id!);
      }
      if (mounted) setState(() => _isFavorite = !_isFavorite);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('Error: $e')));
      }
    } finally {
      if (mounted) setState(() => _loadingFav = false);
    }
  }

  /// Detects if [text] contains HTML tags.
  static final _htmlTagRegex = RegExp(r'<[a-zA-Z][^>]*>');

  /// Renders the description as rich HTML if tags are detected,
  /// otherwise falls back to a plain Text widget.
  Widget _buildDescription(String text) {
    if (_htmlTagRegex.hasMatch(text)) {
      return Html(
        data: text,
        style: {
          'body': Style(
            fontSize: FontSize(14),
            color: Colors.grey.shade600,
            lineHeight: LineHeight(1.5),
            margin: Margins.zero,
            padding: HtmlPaddings.zero,
          ),
          'a': Style(
            color: const Color(0xFFFF6B35),
            textDecoration: TextDecoration.none,
          ),
        },
      );
    }
    return Text(
      text,
      style: TextStyle(
        fontSize: 14,
        color: Colors.grey.shade600,
        height: 1.5,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final recipe = widget.recipe;

    return Scaffold(
      backgroundColor: Colors.white,
      body: CustomScrollView(
        slivers: [
          // Hero image
          SliverAppBar(
            expandedHeight: 280,
            pinned: true,
            backgroundColor: const Color(0xFFFF6B35),
            leading: IconButton(
              icon: Container(
                padding: const EdgeInsets.all(6),
                decoration: BoxDecoration(
                  color: Colors.black.withValues(alpha: 0.3),
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.arrow_back,
                  color: Colors.white,
                  size: 20,
                ),
              ),
              onPressed: () => Navigator.pop(context),
            ),
            actions: [
              IconButton(
                icon: Container(
                  padding: const EdgeInsets.all(6),
                  decoration: BoxDecoration(
                    color: Colors.black.withValues(alpha: 0.3),
                    shape: BoxShape.circle,
                  ),
                  child: Icon(
                    _isFavorite ? Icons.favorite : Icons.favorite_border,
                    color: _isFavorite ? const Color(0xFFEF4444) : Colors.white,
                    size: 20,
                  ),
                ),
                onPressed: _toggleFavorite,
              ),
            ],
            flexibleSpace: FlexibleSpaceBar(
              background: recipe.imageUrl != null && recipe.imageUrl!.isNotEmpty
                  ? CachedNetworkImage(
                      imageUrl: recipe.imageUrl!,
                      fit: BoxFit.cover,
                      placeholder: (_, __) => Container(
                        color: const Color(0xFFFF6B35).withValues(alpha: 0.2),
                        child: const Center(
                          child: CircularProgressIndicator(color: Colors.white),
                        ),
                      ),
                      errorWidget: (_, __, ___) => Container(
                        color: const Color(0xFFFF6B35).withValues(alpha: 0.2),
                        child: const Icon(
                          Icons.restaurant,
                          size: 64,
                          color: Colors.white54,
                        ),
                      ),
                    )
                  : Container(
                      decoration: const BoxDecoration(
                        gradient: LinearGradient(
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                          colors: [Color(0xFFFF6B35), Color(0xFFF7C948)],
                        ),
                      ),
                      child: const Center(
                        child: Icon(
                          Icons.restaurant_menu,
                          size: 80,
                          color: Colors.white54,
                        ),
                      ),
                    ),
            ),
          ),

          // Content
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Title + source badge
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Expanded(
                        child: Text(
                          recipe.name,
                          style: const TextStyle(
                            fontSize: 24,
                            fontWeight: FontWeight.w800,
                            color: Color(0xFF1F2937),
                            height: 1.2,
                          ),
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 10,
                          vertical: 4,
                        ),
                        decoration: BoxDecoration(
                          color: const Color(0xFFFF6B35).withValues(alpha: 0.1),
                          borderRadius: BorderRadius.circular(20),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),

                  // ─── Match score badge (only from ingredient search) ────
                  if (recipe.matchScore != null) ...[
                    Builder(builder: (_) {
                      final score = recipe.matchScore!;
                      String badgeLabel;
                      Color badgeColor;
                      IconData badgeIcon;
                      if (score == 1.0) {
                        badgeLabel = '🟢 Can make now';
                        badgeColor = const Color(0xFF10B981);
                        badgeIcon = Icons.check_circle;
                      } else if (score >= 0.5) {
                        badgeLabel = '🟡 Almost there';
                        badgeColor = const Color(0xFFF59E0B);
                        badgeIcon = Icons.timelapse;
                      } else {
                        badgeLabel = '🔵 Inspiration';
                        badgeColor = const Color(0xFF3B82F6);
                        badgeIcon = Icons.lightbulb_outline;
                      }
                      final matchedCount = recipe.matchedIngredients?.length ?? 0;
                      final totalNonStaple = matchedCount + (recipe.missingIngredients?.length ?? 0);

                      return Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: badgeColor.withValues(alpha: 0.08),
                          borderRadius: BorderRadius.circular(14),
                          border: Border.all(color: badgeColor.withValues(alpha: 0.25)),
                        ),
                        child: Row(
                          children: [
                            Icon(badgeIcon, color: badgeColor, size: 22),
                            const SizedBox(width: 10),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    badgeLabel,
                                    style: TextStyle(
                                      fontSize: 14,
                                      fontWeight: FontWeight.w700,
                                      color: badgeColor,
                                    ),
                                  ),
                                  const SizedBox(height: 2),
                                  Text(
                                    '$matchedCount of $totalNonStaple ingredients matched  •  ${(score * 100).toInt()}%',
                                    style: TextStyle(
                                      fontSize: 11,
                                      color: badgeColor.withValues(alpha: 0.8),
                                      fontWeight: FontWeight.w500,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      );
                    }),
                    const SizedBox(height: 8),
                  ],

                  _buildDescription(recipe.description),
                  const SizedBox(height: 20),

                  // Info chips
                  Row(
                    children: [
                      _InfoChip(
                        icon: Icons.timer_outlined,
                        label: 'Prep',
                        value: recipe.prepTime,
                      ),
                      const SizedBox(width: 12),
                      _InfoChip(
                        icon: Icons.local_fire_department,
                        label: 'Cook',
                        value: recipe.cookTime,
                      ),
                      const SizedBox(width: 12),
                      _InfoChip(
                        icon: Icons.people_outline,
                        label: 'Serves',
                        value: '${recipe.servings}',
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),

                  // Diet labels
                  if (recipe.dietLabels.isNotEmpty) ...[
                    const Text(
                      'Diet Labels',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w700,
                        color: Color(0xFF1F2937),
                      ),
                    ),
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 6,
                      runSpacing: 6,
                      children: recipe.dietLabels.map((label) {
                        return Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 10,
                            vertical: 5,
                          ),
                          decoration: BoxDecoration(
                            color: const Color(
                              0xFF10B981,
                            ).withValues(alpha: 0.1),
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Text(
                            label,
                            style: const TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.w600,
                              color: Color(0xFF10B981),
                            ),
                          ),
                        );
                      }).toList(),
                    ),
                    const SizedBox(height: 20),
                  ],

                  // Allergens warning — only shown if they match user's profile
                  Builder(builder: (_) {
                    final relevantAllergens = _getRelevantAllergens();
                    if (relevantAllergens.isEmpty) return const SizedBox.shrink();
                    return Padding(
                      padding: const EdgeInsets.only(bottom: 20),
                      child: Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: const Color(0xFFFEF3C7),
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(
                            color: const Color(0xFFF59E0B).withValues(alpha: 0.3),
                          ),
                        ),
                        child: Row(
                          children: [
                            const Icon(
                              Icons.warning_amber,
                              color: Color(0xFFF59E0B),
                              size: 20,
                            ),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                '⚠️ Warning: Contains ${relevantAllergens.join(", ")}',
                                style: const TextStyle(
                                  fontSize: 12,
                                  fontWeight: FontWeight.w600,
                                  color: Color(0xFF92400E),
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    );
                  }),

                  // ─── Ingredients section ─────────────────────────────────
                  // If we have match data, show matched/missing breakdown
                  if (recipe.matchedIngredients != null && recipe.missingIngredients != null) ...[
                    // Available ingredients
                    if (recipe.matchedIngredients!.isNotEmpty) ...[
                      Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.all(6),
                            decoration: BoxDecoration(
                              color: const Color(0xFF10B981).withValues(alpha: 0.12),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: const Icon(Icons.check_circle, size: 16, color: Color(0xFF10B981)),
                          ),
                          const SizedBox(width: 10),
                          Text(
                            'Available Ingredients (${recipe.matchedIngredients!.length})',
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w700,
                              color: Color(0xFF10B981),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 10),
                      ...recipe.matchedIngredients!.map((ing) {
                        return Padding(
                          padding: const EdgeInsets.only(bottom: 7),
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Container(
                                margin: const EdgeInsets.only(top: 6),
                                width: 7,
                                height: 7,
                                decoration: const BoxDecoration(
                                  color: Color(0xFF10B981),
                                  shape: BoxShape.circle,
                                ),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Text(
                                  ing,
                                  style: TextStyle(
                                    fontSize: 14,
                                    color: Colors.grey.shade700,
                                    height: 1.4,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        );
                      }),
                      const SizedBox(height: 18),
                    ],

                    // Missing ingredients
                    if (recipe.missingIngredients!.isNotEmpty) ...[
                      Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.all(6),
                            decoration: BoxDecoration(
                              color: const Color(0xFFEF4444).withValues(alpha: 0.12),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: const Icon(Icons.cancel, size: 16, color: Color(0xFFEF4444)),
                          ),
                          const SizedBox(width: 10),
                          Text(
                            'Missing Ingredients (${recipe.missingIngredients!.length})',
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w700,
                              color: Color(0xFFEF4444),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 10),
                      ...recipe.missingIngredients!.map((ing) {
                        return Padding(
                          padding: const EdgeInsets.only(bottom: 7),
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Container(
                                margin: const EdgeInsets.only(top: 6),
                                width: 7,
                                height: 7,
                                decoration: const BoxDecoration(
                                  color: Color(0xFFEF4444),
                                  shape: BoxShape.circle,
                                ),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Text(
                                  ing,
                                  style: TextStyle(
                                    fontSize: 14,
                                    color: Colors.grey.shade500,
                                    height: 1.4,
                                    decoration: TextDecoration.lineThrough,
                                    decorationColor: Colors.grey.shade400,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        );
                      }),
                      const SizedBox(height: 18),
                    ],
                  ] else ...[
                    // Standard ingredients list (no match data)
                    const Text(
                      'Ingredients',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.w700,
                        color: Color(0xFF1F2937),
                      ),
                    ),
                    const SizedBox(height: 12),
                    ...recipe.ingredients.asMap().entries.map((entry) {
                      return Padding(
                        padding: const EdgeInsets.only(bottom: 8),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Container(
                              margin: const EdgeInsets.only(top: 6),
                              width: 6,
                              height: 6,
                              decoration: const BoxDecoration(
                                color: Color(0xFFFF6B35),
                                shape: BoxShape.circle,
                              ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Text(
                                entry.value,
                                style: TextStyle(
                                  fontSize: 14,
                                  color: Colors.grey.shade700,
                                  height: 1.4,
                                ),
                              ),
                            ),
                          ],
                        ),
                      );
                    }),
                  ],
                  const SizedBox(height: 24),

                  // Instructions
                  const Text(
                    'Instructions',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w700,
                      color: Color(0xFF1F2937),
                    ),
                  ),
                  const SizedBox(height: 12),
                  ...recipe.instructions
                      .where((inst) =>
                          !inst.trim().toLowerCase().startsWith('step'))
                      .toList()
                      .asMap()
                      .entries
                      .map((entry) {
                    return Padding(
                      padding: const EdgeInsets.only(bottom: 14),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Container(
                            width: 28,
                            height: 28,
                            decoration: BoxDecoration(
                              color: const Color(
                                0xFFFF6B35,
                              ).withValues(alpha: 0.1),
                              shape: BoxShape.circle,
                            ),
                            child: Center(
                              child: Text(
                                '${entry.key + 1}',
                                style: const TextStyle(
                                  fontSize: 12,
                                  fontWeight: FontWeight.w700,
                                  color: Color(0xFFFF6B35),
                                ),
                              ),
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Text(
                              entry.value,
                              style: TextStyle(
                                fontSize: 14,
                                color: Colors.grey.shade700,
                                height: 1.5,
                              ),
                            ),
                          ),
                        ],
                      ),
                    );
                  }),
                  const SizedBox(height: 40),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _InfoChip extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;

  const _InfoChip({
    required this.icon,
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 12),
        decoration: BoxDecoration(
          color: const Color(0xFFF8F9FA),
          borderRadius: BorderRadius.circular(14),
        ),
        child: Column(
          children: [
            Icon(icon, size: 20, color: const Color(0xFFFF6B35)),
            const SizedBox(height: 4),
            Text(
              value.isNotEmpty ? value : 'N/A',
              style: const TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w700,
                color: Color(0xFF1F2937),
              ),
            ),
            Text(
              label,
              style: TextStyle(fontSize: 10, color: Colors.grey.shade500),
            ),
          ],
        ),
      ),
    );
  }
}
