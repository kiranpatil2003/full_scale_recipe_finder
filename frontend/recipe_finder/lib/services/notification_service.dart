import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:recipe_finder/services/user_service.dart';

class NotificationService {
  static final FirebaseMessaging _messaging = FirebaseMessaging.instance;

  /// Initialize FCM and send token to backend
  static Future<void> initialize() async {
    try {
      // Request permission
      final settings = await _messaging.requestPermission(
        alert: true,
        badge: true,
        sound: true,
      );

      if (settings.authorizationStatus == AuthorizationStatus.authorized) {
        // Get FCM token
        final token = await _messaging.getToken();
        if (token != null) {
          try {
            await UserService.updateFcmToken(token);
          } catch (_) {
            // Token update may fail if user is not yet verified, that's OK
          }
        }

        // Listen for token refresh
        _messaging.onTokenRefresh.listen((newToken) async {
          try {
            await UserService.updateFcmToken(newToken);
          } catch (_) {}
        });
      }
    } catch (e) {
      print('FCM initialization error: $e');
    }
  }

  /// Handle foreground messages
  static void setupForegroundHandler() {
    FirebaseMessaging.onMessage.listen((RemoteMessage message) {
      print('Foreground message: ${message.notification?.title}');
    });
  }
}
