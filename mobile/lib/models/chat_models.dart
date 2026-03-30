import 'dart:convert';

class ChatRequest {
  final String sessionId;
  final String message;
  final String language;

  ChatRequest({
    required this.sessionId,
    required this.message,
    this.language = "en",
  });

  Map<String, dynamic> toJson() => {
        'session_id': sessionId,
        'message': message,
        'language': language,
      };
}

class MessageItem {
  final String role;
  final String content;

  MessageItem({required this.role, required this.content});

  factory MessageItem.fromJson(Map<String, dynamic> json) {
    return MessageItem(
      role: json['role'] as String,
      content: json['content'] as String,
    );
  }

  Map<String, dynamic> toJson() => {
        'role': role,
        'content': content,
      };
}

class AgentStateData {
  final String currentStage;
  final int? helplessnessScore;
  final bool? wantsReport;
  final String? incidentCategory;
  final String? incidentSeverity;
  final String? classificationReasoning;
  final List<String>? recommendedChannels;
  final String? chosenChannel;
  final List<String>? technicalSteps;
  final String? technicalSummary;
  final Map<String, dynamic>? tzcertFields;
  final String? reportTemplate;
  final String? submissionInstructions;
  final String? emotionalResponse;
  final String? resilienceExercise;

  AgentStateData({
    required this.currentStage,
    this.helplessnessScore,
    this.wantsReport,
    this.incidentCategory,
    this.incidentSeverity,
    this.classificationReasoning,
    this.recommendedChannels,
    this.chosenChannel,
    this.technicalSteps,
    this.technicalSummary,
    this.tzcertFields,
    this.reportTemplate,
    this.submissionInstructions,
    this.emotionalResponse,
    this.resilienceExercise,
  });

  factory AgentStateData.fromJson(Map<String, dynamic> json) {
    return AgentStateData(
      currentStage: json['current_stage'] as String? ?? '1_classification',
      helplessnessScore: json['helplessness_score'] as int?,
      wantsReport: json['wants_report'] as bool?,
      incidentCategory: json['incident_category'] as String?,
      incidentSeverity: json['incident_severity'] as String?,
      classificationReasoning: json['classification_reasoning'] as String?,
      recommendedChannels: (json['recommended_channels'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList(),
      chosenChannel: json['chosen_channel'] as String?,
      technicalSteps: (json['technical_steps'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList(),
      technicalSummary: json['technical_summary'] as String?,
      tzcertFields: json['tzcert_fields'] as Map<String, dynamic>?,
      reportTemplate: json['report_template'] as String?,
      submissionInstructions: json['submission_instructions'] as String?,
      emotionalResponse: json['emotional_response'] as String?,
      resilienceExercise: json['resilience_exercise'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
        'current_stage': currentStage,
        'helplessness_score': helplessnessScore,
        'wants_report': wantsReport,
        'incident_category': incidentCategory,
        'incident_severity': incidentSeverity,
        'classification_reasoning': classificationReasoning,
        'recommended_channels': recommendedChannels,
        'chosen_channel': chosenChannel,
        'technical_steps': technicalSteps,
        'technical_summary': technicalSummary,
        'tzcert_fields': tzcertFields,
        'report_template': reportTemplate,
        'submission_instructions': submissionInstructions,
        'emotional_response': emotionalResponse,
        'resilience_exercise': resilienceExercise,
      };
}

class ChatResponse {
  final String sessionId;
  final List<MessageItem> messages;
  final AgentStateData state;

  ChatResponse({
    required this.sessionId,
    required this.messages,
    required this.state,
  });

  factory ChatResponse.fromJson(Map<String, dynamic> json) {
    return ChatResponse(
      sessionId: json['session_id'] as String,
      messages: (json['messages'] as List<dynamic>)
          .map((e) => MessageItem.fromJson(e as Map<String, dynamic>))
          .toList(),
      state: AgentStateData.fromJson(json['state'] as Map<String, dynamic>),
    );
  }
}
