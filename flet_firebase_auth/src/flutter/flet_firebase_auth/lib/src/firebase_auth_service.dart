
import 'package:flet/flet.dart';
import 'package:flutter/foundation.dart';

class FirebaseAuthService extends FletService {
  FirebaseAuthService({required super.control});

  @override
  void init() {
    debugPrint('VibeGram Firebase Auth service initialized');
  }

  @override
  void update() {}

  @override
  void dispose() {
    super.dispose();
  }
}
