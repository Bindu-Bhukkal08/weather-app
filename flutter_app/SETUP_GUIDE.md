# WeatherNow Flutter App - Setup Guide

## Apne PC par setup karne ke steps:

### Step 1: Flutter Install karein
- Flutter official site: https://flutter.dev/docs/get-started/install
- Android Studio install karein
- `flutter doctor` command run karein sab kuch check karne ke liye

### Step 2: Project files copy karein
Replit se poora `flutter_app` folder download karein ya copy karein apne PC par.

### Step 3: API URL update karein
`lib/services/weather_service.dart` file mein apna Replit URL paste karein:

```dart
static const String baseUrl = 'YOUR_REPLIT_URL_HERE';
```

Aapka current Replit URL:
`https://396dd695-6fa3-4664-b64f-6154ab57789e-00-326g0bx2s0gy1.pike.replit.dev`

### Step 4: Dependencies install karein
```bash
flutter pub get
```

### Step 5: Android phone connect karein aur run karein
```bash
flutter run
```

### Step 6: APK build karein (phone par install karne ke liye)
```bash
flutter build apk --release
```
APK milega: `build/app/outputs/flutter-apk/app-release.apk`

---

## Features:
- Current weather for any Indian state/district/village
- GPS real location detection
- 5-day forecast
- Beautiful dark UI
- 20+ Indian city quick buttons
