
import 'package:flet/flet.dart';
import 'package:flutter/foundation.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_auth/firebase_auth.dart' as fb;
import 'package:cloud_firestore/cloud_firestore.dart';
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

    debugPrint('VibeGram: Firebase initialized');
  }

  Map<String, dynamic> _userData(fb.User user) {
    return {
      'success': true,
      'authenticated': true,
      'uid': user.uid,
      'email': user.email ?? '',
      'displayName': user.displayName ?? '',
      'photoURL': user.photoURL ?? '',
    };
  }

  Future<void> _ensureUserDocument(fb.User user) async {
    final ref = FirebaseFirestore.instance
        .collection('users')
        .doc(user.uid);

    final snapshot = await ref.get();

    final data = <String, dynamic>{
      'uid': user.uid,
      'email': user.email ?? '',
      'displayName': user.displayName ?? '',
      'avatarUrl': user.photoURL ?? '',
      'updatedAt': FieldValue.serverTimestamp(),
    };

    if (!snapshot.exists) {
      data['username'] = '';
      data['about'] = '';
      data['backgroundUrl'] = '';
      data['createdAt'] = FieldValue.serverTimestamp();
    }

    await ref.set(data, SetOptions(merge: true));
  }

  Future<dynamic> _onInvokeMethod(
    String name,
    dynamic args,
  ) async {
    try {
      await _ensureInitialized();

      if (name == 'get_auth_state') {
        final user = fb.FirebaseAuth.instance.currentUser;

        if (user == null) {
          return {
            'success': true,
            'authenticated': false,
          };
        }

        await _ensureUserDocument(user);

        return _userData(user);
      }

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

        await _ensureUserDocument(user);

        return _userData(user);
      }

      if (name == 'get_user_profile') {
        final user = fb.FirebaseAuth.instance.currentUser;

        if (user == null) {
          throw Exception('User is not authenticated');
        }

        final snapshot = await FirebaseFirestore.instance
            .collection('users')
            .doc(user.uid)
            .get();

        return {
          'success': true,
          'profile': snapshot.data() ?? {},
        };
      }

      if (name == 'save_user_profile') {
        final user = fb.FirebaseAuth.instance.currentUser;

        if (user == null) {
          throw Exception('User is not authenticated');
        }

        final profile = Map<String, dynamic>.from(
          args as Map,
        );

        await FirebaseFirestore.instance
            .collection('users')
            .doc(user.uid)
            .set({
          'username': profile['username'] ?? '',
          'displayName': profile['displayName'] ?? '',
          'about': profile['about'] ?? '',
          'updatedAt': FieldValue.serverTimestamp(),
        }, SetOptions(merge: true));

        return {'success': true};
      }

      if (name == 'sign_out') {
        await fb.FirebaseAuth.instance.signOut();
        await GoogleSignIn.instance.signOut();

        return {'success': true};
      }

      return {
        'success': false,
        'error': 'Unknown method: $name',
      };
    } catch (e) {
      debugPrint('VibeGram Firebase error: $e');

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
