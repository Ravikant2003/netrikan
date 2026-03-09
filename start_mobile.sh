#!/bin/bash

# Netrikan Mobile App Startup Script  
# Date: 9 March 2026

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║          📱 STARTING NETRIKAN MOBILE APP 📱                   ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Navigate to mobile app
cd "/Users/bighnesh/Desktop/Netrikan copy/mobile_app"

# Check Flutter
echo "✓ Checking Flutter installation..."
flutter --version | head -1

# Get dependencies
echo ""
echo "✓ Getting Flutter dependencies..."
flutter pub get > /dev/null 2>&1

# Start app
echo ""
echo "✓ Starting Flutter app..."
echo "✓ Make sure you have an emulator running or device connected"
echo "✓ Press Ctrl+C to stop the app"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Run the app
flutter run
