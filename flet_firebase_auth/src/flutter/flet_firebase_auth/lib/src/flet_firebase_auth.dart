
import 'package:flet/flet.dart';
import 'package:flutter/widgets.dart';

class FletFirebaseAuthControl extends StatelessWidget {
  final Control control;

  const FletFirebaseAuthControl({
    super.key,
    required this.control,
  });

  @override
  Widget build(BuildContext context) {
    return LayoutControl(
      control: control,
      child: const SizedBox.shrink(),
    );
  }
}
