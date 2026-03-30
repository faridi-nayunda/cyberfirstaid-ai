import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/chat_models.dart';

class ApiService {
  String baseUrl;
  String? groqApiKey;

  ApiService({
    this.baseUrl = 'http://127.0.0.1:8000', // Default for Android emulator
    this.groqApiKey,
  });

  void updateBaseUrl(String url) {
    baseUrl = url;
  }

  void updateApiKey(String key) {
    groqApiKey = key;
  }

  Future<ChatResponse> sendMessage(ChatRequest request) async {
    final uri = Uri.parse('$baseUrl/chat');
    
    final headers = {
      'Content-Type': 'application/json',
      if (groqApiKey != null) 'X-Groq-API-Key': groqApiKey!,
    };

    try {
      final response = await http.post(
        uri,
        headers: headers,
        body: jsonEncode(request.toJson()),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        return ChatResponse.fromJson(data);
      } else {
        final errorData = jsonDecode(response.body) as Map<String, dynamic>;
        throw Exception(
            'API Error ${response.statusCode}: ${errorData['detail'] ?? 'Unknown error'}');
      }
    } catch (e) {
      if (e is Exception) rethrow;
      throw Exception('Network error: $e');
    }
  }

  Future<ChatResponse> getSession(String sessionId) async {
    final uri = Uri.parse('$baseUrl/session/$sessionId');
    
    final headers = {
      'Content-Type': 'application/json',
      if (groqApiKey != null) 'X-Groq-API-Key': groqApiKey!,
    };

    try {
      final response = await http.get(uri, headers: headers);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        return ChatResponse.fromJson(data);
      } else if (response.statusCode == 404) {
        throw Exception('Session not found');
      } else {
        throw Exception('API Error: ${response.statusCode}');
      }
    } catch (e) {
      if (e is Exception) rethrow;
      throw Exception('Network error: $e');
    }
  }
}
