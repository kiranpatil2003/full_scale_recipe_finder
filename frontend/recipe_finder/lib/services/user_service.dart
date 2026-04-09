import 'dart:convert';
import 'package:recipe_finder/models/user_profile.dart';
import 'package:recipe_finder/services/api_service.dart';

class UserService {
  /// Verify token and get user profile
  static Future<UserProfile> verifyAndGetProfile() async {
    final response = await ApiService.post('/auth/verify');
    if (response.statusCode == 200) {
      return UserProfile.fromJson(jsonDecode(response.body));
    }
    throw Exception('Failed to verify user: ${response.statusCode}');
  }

  /// Get user profile with dietary info
  static Future<UserProfile> getProfile() async {
    final response = await ApiService.get('/user/profile');
    if (response.statusCode == 200) {
      return UserProfile.fromJson(jsonDecode(response.body));
    }
    throw Exception('Failed to load profile: ${response.statusCode}');
  }

  /// Update user display name and photo
  static Future<void> updateProfile({String? name, String? picture}) async {
    final body = <String, dynamic>{};
    if (name != null) body['name'] = name;
    if (picture != null) body['picture'] = picture;
    await ApiService.put('/user/profile', body: body);
  }

  /// Set dietary preferences
  static Future<void> updateDietaryPreferences(
      List<String> preferences) async {
    await ApiService.put('/user/dietary-preferences', body: {
      'preferences': preferences,
    });
  }

  /// Get allergies
  static Future<List<String>> getAllergies() async {
    final response = await ApiService.get('/user/allergies');
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return (data['allergies'] as List<dynamic>)
          .map((e) => e.toString())
          .toList();
    }
    throw Exception('Failed to load allergies: ${response.statusCode}');
  }

  /// Add an allergy
  static Future<void> addAllergy(String allergen) async {
    await ApiService.post('/user/allergies', body: {'allergen': allergen});
  }

  /// Remove an allergy
  static Future<void> removeAllergy(String allergen) async {
    await ApiService.delete('/user/allergies/$allergen');
  }

  /// Update FCM token
  static Future<void> updateFcmToken(String token) async {
    await ApiService.put('/user/fcm-token', body: {'token': token});
  }
}
