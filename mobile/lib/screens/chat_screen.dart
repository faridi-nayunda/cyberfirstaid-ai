import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/chat_provider.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final _textController = TextEditingController();
  final _scrollController = ScrollController();
  final _focusNode = FocusNode();

  @override
  void dispose() {
    _textController.dispose();
    _scrollController.dispose();
    _focusNode.dispose();
    super.dispose();
  }

  void _scrollToBottom() {
    if (_scrollController.hasClients) {
      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent,
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeOut,
      );
    }
  }

  Future<void> _handleSend() async {
    final text = _textController.text;
    if (text.trim().isEmpty) return;

    _textController.clear();
    _focusNode.requestFocus();

    await context.read<ChatProvider>().sendMessage(text);
    _scrollToBottom();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.primaryContainer,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(
                Icons.shield_rounded,
                color: Theme.of(context).colorScheme.onPrimaryContainer,
                size: 20,
              ),
            ),
            const SizedBox(width: 10),
            const Text('CyberFirstAid AI'),
          ],
        ),
        actions: [
          Consumer<ChatProvider>(
            builder: (context, chat, _) => IconButton(
              icon: const Icon(Icons.delete_outline_rounded),
              tooltip: chat.language == 'en' ? 'Clear chat' : 'Futa mazungumzo',
              onPressed: () {
                chat.clearConversation();
                _scrollToBottom();
              },
            ),
          ),
          _buildSettingsButton(),
        ],
      ),
      drawer: _buildDrawer(),
      body: Column(
        children: [
          // Error banner
          Consumer<ChatProvider>(
            builder: (context, chat, _) {
              if (chat.error == null) return const SizedBox.shrink();
              return Container(
                width: double.infinity,
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                color: Theme.of(context).colorScheme.errorContainer,
                child: Row(
                  children: [
                    Icon(
                      Icons.error_outline,
                      color: Theme.of(context).colorScheme.onErrorContainer,
                      size: 20,
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        chat.error!,
                        style: TextStyle(
                          color: Theme.of(context).colorScheme.onErrorContainer,
                        ),
                      ),
                    ),
                    IconButton(
                      icon: const Icon(Icons.close, size: 18),
                      onPressed: chat.dismissError,
                      color: Theme.of(context).colorScheme.onErrorContainer,
                      padding: EdgeInsets.zero,
                      constraints: const BoxConstraints(),
                    ),
                  ],
                ),
              );
            },
          ),
          // Chat messages
          Expanded(
            child: Consumer<ChatProvider>(
              builder: (context, chat, _) {
                WidgetsBinding.instance.addPostFrameCallback((_) => _scrollToBottom());
                
                if (chat.messages.isEmpty) {
                  return _buildEmptyState(chat);
                }

                return ListView.builder(
                  controller: _scrollController,
                  padding: const EdgeInsets.all(16),
                  itemCount: chat.messages.length,
                  itemBuilder: (context, index) {
                    final message = chat.messages[index];
                    return _buildMessageBubble(message, chat);
                  },
                );
              },
            ),
          ),
          // Input area
          _buildInputArea(),
        ],
      ),
    );
  }

  Widget _buildSettingsButton() {
    return Builder(
      builder: (context) => IconButton(
        icon: const Icon(Icons.settings_outlined),
        tooltip: 'Settings',
        onPressed: () => Scaffold.of(context).openDrawer(),
      ),
    );
  }

  Widget _buildDrawer() {
    return Consumer<ChatProvider>(
      builder: (context, chat, _) {
        final apiKeyController = TextEditingController(text: chat.apiKey ?? '');
        final urlController = TextEditingController(
          text: 'http://10.0.2.2:8000',
        );

        return Drawer(
          child: SafeArea(
            child: ListView(
              padding: const EdgeInsets.all(16),
              children: [
                Text(
                  'Settings / Mipangilio',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                const SizedBox(height: 24),
                // Language selector
                Text(
                  'Language / Lugha',
                  style: Theme.of(context).textTheme.labelLarge,
                ),
                const SizedBox(height: 8),
                SegmentedButton<String>(
                  segments: const [
                    ButtonSegment(value: 'en', label: Text('English')),
                    ButtonSegment(value: 'sw', label: Text('Kiswahili')),
                  ],
                  selected: {chat.language},
                  onSelectionChanged: (Set<String> selection) {
                    chat.setLanguage(selection.first);
                    chat.clearConversation();
                  },
                ),
                const SizedBox(height: 24),
                // API Key input
                TextField(
                  controller: apiKeyController,
                  decoration: const InputDecoration(
                    labelText: 'Groq API Key',
                    hintText: 'Enter your Groq API key',
                    border: OutlineInputBorder(),
                    helperText: 'Get free key at console.groq.com',
                  ),
                  obscureText: true,
                  onChanged: (value) => chat.setApiKey(value),
                ),
                const SizedBox(height: 16),
                // Base URL input
                TextField(
                  controller: urlController,
                  decoration: const InputDecoration(
                    labelText: 'Backend URL',
                    border: OutlineInputBorder(),
                    helperText: 'Android emulator: 10.0.2.2',
                  ),
                  onChanged: (value) => chat.setBaseUrl(value),
                ),
                const SizedBox(height: 24),
                const Divider(),
                const SizedBox(height: 16),
                // Status info
                Text(
                  'Session ID',
                  style: Theme.of(context).textTheme.labelMedium,
                ),
                const SizedBox(height: 4),
                Text(
                  chat.sessionId.substring(0, 8) + '...',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
                if (chat.currentState != null) ...[
                  const SizedBox(height: 16),
                  _buildStateInfo(chat),
                ],
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildStateInfo(ChatProvider chat) {
    final state = chat.currentState!;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Incident Status',
          style: Theme.of(context).textTheme.labelMedium,
        ),
        const SizedBox(height: 8),
        if (state.incidentCategory != null)
          _buildInfoChip(
            'Category',
            state.incidentCategory!.replaceAll('_', ' ').split(' ').map(
              (w) => '${w[0].toUpperCase()}${w.substring(1)}',
            ).join(' '),
          ),
        if (state.incidentSeverity != null)
          _buildInfoChip('Severity', state.incidentSeverity!.toUpperCase()),
        if (state.recommendedChannels?.isNotEmpty == true)
          _buildInfoChip('Channels', state.recommendedChannels!.join(', ').toUpperCase()),
      ],
    );
  }

  Widget _buildInfoChip(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Row(
        children: [
          Text(
            '$label: ',
            style: Theme.of(context).textTheme.bodySmall,
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.secondaryContainer,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(
              value,
              style: TextStyle(
                fontSize: 12,
                color: Theme.of(context).colorScheme.onSecondaryContainer,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState(ChatProvider chat) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.shield_rounded,
            size: 64,
            color: Theme.of(context).colorScheme.primary.withAlpha(100),
          ),
          const SizedBox(height: 16),
          Text(
            chat.language == 'en'
                ? 'CyberFirstAid AI'
                : 'Msaidizi wa CyberFirstAid AI',
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 8),
          Text(
            chat.language == 'en'
                ? 'Immediate help after a cyber attack'
                : 'Msaada wa haraka baada ya shambulio la mtandao',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Theme.of(context).colorScheme.outline,
                ),
          ),
        ],
      ),
    );
  }

  Widget _buildMessageBubble(ChatMessage message, ChatProvider chat) {
    final isUser = message.isUser;
    
    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.8,
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (!isUser) ...[
              CircleAvatar(
                radius: 16,
                backgroundColor: Theme.of(context).colorScheme.primaryContainer,
                child: Icon(
                  Icons.shield_rounded,
                  size: 18,
                  color: Theme.of(context).colorScheme.onPrimaryContainer,
                ),
              ),
              const SizedBox(width: 8),
            ],
            Flexible(
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                decoration: BoxDecoration(
                  color: isUser
                      ? Theme.of(context).colorScheme.primaryContainer
                      : Theme.of(context).colorScheme.surfaceContainerHighest,
                  borderRadius: BorderRadius.only(
                    topLeft: const Radius.circular(16),
                    topRight: const Radius.circular(16),
                    bottomLeft: Radius.circular(isUser ? 16 : 4),
                    bottomRight: Radius.circular(isUser ? 4 : 16),
                  ),
                ),
                child: SelectableText(
                  message.content,
                  style: TextStyle(
                    color: isUser
                        ? Theme.of(context).colorScheme.onPrimaryContainer
                        : Theme.of(context).colorScheme.onSurface,
                  ),
                ),
              ),
            ),
            if (isUser) ...[
              const SizedBox(width: 8),
              CircleAvatar(
                radius: 16,
                backgroundColor: Theme.of(context).colorScheme.secondaryContainer,
                child: Icon(
                  Icons.person,
                  size: 18,
                  color: Theme.of(context).colorScheme.onSecondaryContainer,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildInputArea() {
    return Container(
      padding: EdgeInsets.only(
        left: 16,
        right: 16,
        top: 8,
        bottom: MediaQuery.of(context).padding.bottom + 8,
      ),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surface,
        border: Border(
          top: BorderSide(
            color: Theme.of(context).colorScheme.outlineVariant,
          ),
        ),
      ),
      child: Consumer<ChatProvider>(
        builder: (context, chat, _) {
          return Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _textController,
                  focusNode: _focusNode,
                  textInputAction: TextInputAction.send,
                  onSubmitted: (_) => _handleSend(),
                  enabled: !chat.isLoading,
                  decoration: InputDecoration(
                    hintText: chat.language == 'en'
                        ? 'Type your message...'
                        : 'Andika ujumbe wako...',
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(24),
                    ),
                    contentPadding: const EdgeInsets.symmetric(
                      horizontal: 20,
                      vertical: 12,
                    ),
                    filled: true,
                    fillColor: Theme.of(context).colorScheme.surfaceContainerHighest,
                  ),
                  maxLines: 4,
                  minLines: 1,
                ),
              ),
              const SizedBox(width: 8),
              AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                child: chat.isLoading
                    ? Container(
                        width: 48,
                        height: 48,
                        decoration: BoxDecoration(
                          color: Theme.of(context).colorScheme.primaryContainer,
                          shape: BoxShape.circle,
                        ),
                        child: Padding(
                          padding: const EdgeInsets.all(12),
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: Theme.of(context).colorScheme.onPrimaryContainer,
                          ),
                        ),
                      )
                    : IconButton.filled(
                        onPressed: _handleSend,
                        icon: const Icon(Icons.send_rounded),
                        style: IconButton.styleFrom(
                          backgroundColor: Theme.of(context).colorScheme.primary,
                          foregroundColor: Theme.of(context).colorScheme.onPrimary,
                        ),
                      ),
              ),
            ],
          );
        },
      ),
    );
  }
}
