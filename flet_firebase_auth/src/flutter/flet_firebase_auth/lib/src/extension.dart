
import 'package:flet/flet.dart';
import 'package:flutter/widgets.dart';

import 'flet_firebase_auth.dart';
import 'firebase_auth_service.dart';

class Extension extends FletExtension {
  @override
  void ensureInitialized() {
    // Firebase initialization will be handled by the service.
  }

  @override
  FletService? createService(Control control) {
    switch (control.type) {
      case "FirebaseAuth":
        return FirebaseAuthService(control: control);
      default:
        return null;
    }
  }

  @override
  Widget? createWidget(Key? key, Control control) {
    switch (control.type) {
      case "FletFirebaseAuth":
        return FletFirebaseAuthControl(control: control);
      default:
        return null;
    }
  }
}
