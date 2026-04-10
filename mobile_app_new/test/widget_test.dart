import 'package:flutter_test/flutter_test.dart';
import 'package:netrikan_mobile/theme/app_theme.dart';

void main() {
  test('AppTheme.dark builds', () {
    final theme = AppTheme.dark;
    expect(theme.brightness, isNotNull);
  });
}
