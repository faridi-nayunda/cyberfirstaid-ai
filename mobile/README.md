# CyberFirstAid AI Mobile App

A Flutter mobile app for chatting with the CyberFirstAid AI assistant.

## Features

- 🛡️ Chat interface similar to ChatGPT
- 🌍 Bilingual support (English/Kiswahili)
- 📱 Works on Android, iOS, and Web
- 🔐 API key configuration in settings

## Prerequisites

1. **Flutter SDK** - Install from [flutter.dev](https://flutter.dev)
2. **Backend running** - The CyberFirstAid backend must be running
3. **Groq API Key** - Get free at [console.groq.com](https://console.groq.com)

## Getting Started

### 1. Install Dependencies

```bash
cd mobile
flutter pub get
```

### 2. Run the Backend

```bash
cd ../backend
pip install -r requirements.txt
# Set your Groq API key
set GROQ_API_KEY=your_key_here  # Windows
# or
export GROQ_API_KEY=your_key_here  # Linux/Mac

python api.py
```

The backend will run on `http://localhost:8000`

### 3. Run the Mobile App

**For Web (easiest for testing):**
```bash
flutter run -d chrome
```

**For Android Emulator:**
```bash
flutter run -d android
```
The app defaults to `http://10.0.2.2:8000` for Android emulator (this maps to localhost on the host machine).

**For iOS Simulator:**
```bash
flutter run -d ios
```
Change the backend URL in settings to `http://localhost:8000`.

## Configuration

Open the settings drawer (gear icon) to configure:

- **Language**: English or Kiswahili
- **Groq API Key**: Your API key (required if not set on backend)
- **Backend URL**: The URL where the backend API is running

### URL Reference

| Platform | Default URL |
|----------|-------------|
| Android Emulator | `http://10.0.2.2:8000` |
| iOS Simulator | `http://localhost:8000` |
| Web | `http://localhost:8000` |
| Physical Device | `http://<your-computer-ip>:8000` |

## Project Structure

```
mobile/
├── lib/
│   ├── main.dart              # App entry point
│   ├── models/
│   │   └── chat_models.dart   # Data models
│   ├── providers/
│   │   └── chat_provider.dart # State management
│   ├── screens/
│   │   └── chat_screen.dart   # Main chat UI
│   └── services/
│       └── api_service.dart   # Backend API client
├── android/                   # Android config
├── ios/                       # iOS config
├── web/                       # Web config
└── pubspec.yaml              # Dependencies
```

## API Endpoint

The app calls the backend's `/chat` endpoint:

```dart
POST /chat
{
  "session_id": "uuid-string",
  "message": "user message",
  "language": "en" // or "sw"
}

Headers:
  X-Groq-API-Key: your_api_key (optional if set on backend)
```

## Troubleshooting

**Connection refused:**
- Ensure backend is running on the correct port
- Check the backend URL in settings matches your platform

**API Key error:**
- Enter your Groq API key in the settings drawer
- Or set `GROQ_API_KEY` environment variable on the backend

**Build errors:**
- Run `flutter clean && flutter pub get`
- Ensure Flutter SDK is properly installed
