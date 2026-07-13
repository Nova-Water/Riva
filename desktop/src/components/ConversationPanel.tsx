import { useEffect, useRef } from 'react';
import { useAssistantStore } from '../stores/useAssistantStore';
import { MessageBubble } from './MessageBubble';

export function ConversationPanel() {
  const messages = useAssistantStore((s) => s.messages);
  const clearConversation = useAssistantStore((s) => s.clearConversation);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages.length]);

  return (
    <div className="panel conversation-panel">
      <div className="conversation-header">
        <div className="panel-title">Conversation</div>
        <div className="conversation-header-actions">
          <button className="icon-button" onClick={clearConversation} disabled={messages.length === 0}>
            Clear conversation
          </button>
        </div>
      </div>

      <div className="scroll-region message-list" ref={scrollRef} data-testid="message-list">
        {messages.length === 0 ? (
          <div className="empty-conversation">
            <strong>RIVA is ready.</strong>
            <span>Type a message or press the microphone button to begin.</span>
          </div>
        ) : (
          messages.map((message) => <MessageBubble key={message.id} message={message} />)
        )}
      </div>
    </div>
  );
}
