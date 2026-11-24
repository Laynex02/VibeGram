
import 'package:flet/flet.dart';
import 'package:flutter/foundation.dart';
import 'package:firebase_core/firebase_core.dart';

class FirebaseAuthService extends FletService {
  FirebaseAuthService({required super.control});

  @override
  void init() {
    _initializeFirebase();
  }

  Future<void> _initializeFirebase() async {
    try {
      if (Firebase.apps.isEmpty) {
        await Firebase.initializeApp();
      }

      debugPrint('VibeGram: Firebase initialized successfully');
    } catch (e) {
      debugPrint('VibeGram Firebase initialization error: $e');
    }
  }

  @override
  void update() {}

  @override
  void dispose() {
    super.dispose();
  }
}
