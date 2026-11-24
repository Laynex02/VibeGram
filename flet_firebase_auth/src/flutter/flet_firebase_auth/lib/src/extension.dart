import 'package:flet/flet.dart';
import 'package:flutter/widgets.dart';

import 'flet_firebase_auth.dart';

class Extension extends FletExtension {
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
