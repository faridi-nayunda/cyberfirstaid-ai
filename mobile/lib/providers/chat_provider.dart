import 'package:flutter/foundation.dart';
import 'package:uuid/uuid.dart';
import '../models/chat_models.dart';
import '../services/api_service.dart';

class ChatMessage {
  final String id;
  final String role;
  final String content;
  final DateTime timestamp;

  ChatMessage({
    String? id,
    required this.role,
    required this.content,
    DateTime? timestamp,
  })  : id = id ?? const Uuid().v4(),
        timestamp = timestamp ?? DateTime.now();

  bool get isUser => role == 'user';
  bool get isAssistant => role == 'assistant';
}

class ChatProvider extends ChangeNotifier {
  final ApiService _apiService;
  
  String _sessionId;
  String _language = 'en';
  List<ChatMessage> _messages = [];
  AgentStateData? _currentState;
  bool _isLoading = false;
  String? _error;
  String? _apiKey;

  ChatProvider({ApiService? apiService})
      : _apiService = apiService ?? ApiService(),
        _sessionId = const Uuid().v4();

  List<ChatMessage> get messages => List.unmodifiable(_messages);
  AgentStateData? get currentState => _currentState;
  bool get isLoading => _isLoading;
  String? get error => _error;
  String get language => _language;
  String get sessionId => _sessionId;
  String? get apiKey => _apiKey;

  void setApiKey(String key) {
    _apiKey = key;
    _apiService.updateApiKey(key);
    notifyListeners();
  }

  void setBaseUrl(String url) {
    _apiService.updateBaseUrl(url);
  }

  void setLanguage(String lang) {
    _language = lang;
    notifyListeners();
  }

  void addWelcomeMessage() {
    final welcomeText = _language == 'en'
        ? "Hello. I am CyberFirstAid AI. How can I help you today? Do you need to report a cyber incident?"
        : "Hujambo. Mimi ni msaidizi wa CyberFirstAid AI. Nikusaidie nini leo? Je, unahitaji kuripoti tukio la kimtandao?";
    
    _messages = [
      ChatMessage(role: 'assistant', content: welcomeText),
    ];
    notifyListeners();
  }

  Future<void> sendMessage(String text) async {
    if (text.trim().isEmpty) return;

    // Add user message optimistically
    final userMessage = ChatMessage(role: 'user', content: text.trim());
    _messages.add(userMessage);
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final request = ChatRequest(
        sessionId: _sessionId,
        message: text.trim(),
        language: _language,
      );

      final response = await _apiService.sendMessage(request);
      
      // Update state
      _currentState = response.state;
      
      // Add assistant messages from response
      for (final msg in response.messages) {
        _messages.add(ChatMessage(
          role: msg.role,
          content: msg.content,
        ));
      }

      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _isLoading = false;
      _error = e.toString();
      // Remove the optimistic user message on error
      if (_messages.last == userMessage) {
        _messages.removeLast();
      }
      notifyListeners();
    }
  }

  void clearConversation() {
    _sessionId = const Uuid().v4();
    _currentState = null;
    _error = null;
    addWelcomeMessage();
  }

  void dismissError() {
    _error = null;
    notifyListeners();
  }
}
