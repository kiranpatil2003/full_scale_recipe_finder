class UserProfile {
  final String uid;
  final String? email;
  final String? name;
  final String? picture;
  final List<String> dietaryPreferences;
  final List<String> allergies;
  final String? fcmToken;

  UserProfile({
    required this.uid,
    this.email,
    this.name,
    this.picture,
    this.dietaryPreferences = const [],
    this.allergies = const [],
    this.fcmToken,
  });

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      uid: json['uid'] as String? ?? '',
      email: json['email'] as String?,
      name: json['name'] as String?,
      picture: json['picture'] as String?,
      dietaryPreferences: (json['dietary_preferences'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
      allergies: (json['allergies'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
      fcmToken: json['fcm_token'] as String?,
    );
  }
}
