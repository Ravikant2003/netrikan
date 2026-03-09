# Netrikan Mobile App

A production-ready Flutter mobile app for safe route navigation with real-time safety alerts and emergency response in Bengaluru.

## Features

- **Smart Routes**: AI-powered route selection based on real-time crime and traffic data
- **Emergency Alert**: One-tap SOS to notify guardians and authorities instantly
- **Live Tracking**: Share location with trusted contacts in real-time
- **Safety Score**: Real-time safety metrics and analytics
- **Dark/Light Mode**: Full theme support with glassmorphism UI
- **Responsive Design**: Optimized for all device sizes

## Project Structure

```
lib/
├── main.dart                 # App entry point and navigation
├── theme/
│   └── app_theme.dart       # Theming system with dark/light modes
├── providers/
│   └── theme_provider.dart  # Theme state management
├── widgets/
│   ├── button.dart          # Custom button widget
│   ├── card.dart            # Glassmorphic card widget
│   ├── input.dart           # Text input widget
│   ├── badge.dart           # Status badge widget
│   ├── simple_map.dart      # Interactive map visualization
│   └── index.dart           # Widget exports
├── screens/
│   ├── home_screen.dart     # Home/landing screen
│   ├── route_map_screen.dart # Route selection screen
│   ├── emergency_screen.dart # Emergency alert screen
│   ├── safety_score_screen.dart # Safety analytics screen
│   ├── live_tracking_screen.dart # Location sharing screen
│   └── index.dart           # Screen exports
├── services/
│   └── api_client.dart      # Backend API client (Dio)
└── models/
    ├── route_model.dart
    ├── safety_model.dart
    └── user_model.dart
```

## Setup & Installation

### Prerequisites
- Flutter 3.0+
- Dart 3.0+
- Android SDK or iOS development tools

### Install Dependencies

```bash
flutter pub get
```

### Run the App

```bash
# Debug mode
flutter run

# Release mode
flutter run --release
```

## Architecture

- **State Management**: Provider package for theme management
- **API Integration**: Dio HTTP client with error handling
- **UI Framework**: Material 3 with custom glassmorphism design
- **Theming**: Dual-mode (light/dark) with CSS-like variable system

## Key Components

### Widgets
- **NetrikanButton**: Animated button with multiple variants
- **NetrikanCard**: Glassmorphic card with interactive states
- **NetrikanInput**: Custom text field with focus states
- **NetrikanBadge**: Status indicator badges
- **SimpleMap**: Custom SVG-based route visualization

### Screens
1. **HomeScreen**: Landing page with stats and features
2. **RouteMapScreen**: Route selection with map preview
3. **EmergencyScreen**: SOS alert with emergency types
4. **SafetyScoreScreen**: Safety analytics dashboard
5. **LiveTrackingScreen**: Location sharing controls

## API Integration

The app connects to a FastAPI backend at `http://localhost:8000`:

- `/health` - Health check
- `/api/analyze` - Analyze location
- `/api/route` - Get best route
- `/api/risk` - Assess risk
- `/api/emergency` - Report emergency
- `/api/users` - User management
- `/api/guardian` - Guardian management

## Theme System

The app supports automatic dark/light mode switching:
- Primary Colors: Purple (#6c5ce7) and Bright Purple (#a29bfe)
- Secondary Colors: Green (#00b894) and Bright Green (#55efc4)
- Full glassmorphism with backdrop blur effects

## Testing

```bash
# Run tests
flutter test
```

## Building APK/iOS

```bash
# Android APK
flutter build apk --release

# iOS build
flutter build ios --release
```

## Next Steps

- Integrate real Google Maps API
- Add push notifications (Firebase Cloud Messaging)
- Implement real location services (Geolocator)
- Add camera and microphone for emergency video
- Persistent local database (SQLite/Hive)
- Authentication system

## Tech Stack

- **Flutter** 3.0+ (Mobile framework)
- **Dart** 3.0+ (Language)
- **Provider** (State management)
- **Dio** (HTTP client)
- **Material 3** (UI design system)

## License

Proprietary - Ravikant2003/Netrikan
