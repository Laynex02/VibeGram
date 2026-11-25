
import 'package:flet/flet.dart';
import 'package:flutter/foundation.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_auth/firebase_auth.dart' as fb;
import 'package:google_sign_in/google_sign_in.dart';

class FirebaseAuthService extends FletService {
  FirebaseAuthService({required super.control});

  Future<void>? _initialization;

  @override
  void init() {
    super.init();
    control.addInvokeMethodListener(_onInvokeMethod);
    _ensureInitialized();
  }

  Future<void> _ensureInitialized() {
    return _initialization ??= _initializeFirebase();
  }

  Future<void> _initializeFirebase() async {
    if (Firebase.apps.isEmpty) {
      await Firebase.initializeApp();
    }

    await GoogleSignIn.instance.initialize();

    debugPrint('VibeGram: Firebase and Google initialized');
  }

  Future<dynamic> _onInvokeMethod(
    String name,
    dynamic args,
  ) async {
    try {
      await _ensureInitialized();

      if (name == 'sign_in') {
        final googleUser =
            await GoogleSignIn.instance.authenticate();

        final googleAuth = googleUser.authentication;

        final idToken = googleAuth.idToken;

        if (idToken == null) {
          throw Exception('Google ID token is missing');
        }

        final credential =
            fb.GoogleAuthProvider.credential(
          idToken: idToken,
        );

        final result =
            await fb.FirebaseAuth.instance
                .signInWithCredential(credential);

        final user = result.user;

        if (user == null) {
          throw Exception('Firebase user not found');
        }

        return {
          'success': true,
          'uid': user.uid,
          'email': user.email ?? '',
          'displayName': user.displayName ?? '',
          'photoURL': user.photoURL ?? '',
        };
      }

      if (name == 'sign_out') {
        await fb.FirebaseAuth.instance.signOut();
        await GoogleSignIn.instance.signOut();

        return {'success': true};
      }

      return {
        'success': false,
        'error': 'Unknown method',
      };
    } catch (e) {
      debugPrint('VibeGram auth error: $e');

      return {
        'success': false,
        'error': e.toString(),
      };
    }
  }

  @override
  void update() {}

  @override
  void dispose() {
    control.removeInvokeMethodListener(_onInvokeMethod);
    super.dispose();
  }
}
