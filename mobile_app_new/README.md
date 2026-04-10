# netrikan_mobile

A new Flutter project.

## Backend config
- Default backend base URL is set in `lib/services/api_service.dart`.
- Override at build/run time using:
  - `--dart-define=NETRIKAN_API_BASE_URL=http://<YOUR_IP>:8000`

## Simulation UI
- Open **Home** or **Stats** and tap the **science** icon to open Simulation.
- Pick a scenario and press **Run** to see:
  - Layer2 decision + weighted risk
  - Allowed vs blocked actions (policy audit)

## Getting Started

This project is a starting point for a Flutter application.

A few resources to get you started if this is your first Flutter project:

- [Learn Flutter](https://docs.flutter.dev/get-started/learn-flutter)
- [Write your first Flutter app](https://docs.flutter.dev/get-started/codelab)
- [Flutter learning resources](https://docs.flutter.dev/reference/learning-resources)

For help getting started with Flutter development, view the
[online documentation](https://docs.flutter.dev/), which offers tutorials,
samples, guidance on mobile development, and a full API reference.
