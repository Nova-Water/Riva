import type { ConversationMessage } from '../types';

interface MessageBubbleProps {
  message: ConversationMessage;
}

function formatTime(iso: string): string {
  try {
    return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  } catch {
    return '';
  }
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const handleCopy = () => {
    navigator.clipboard?.writeText(message.content).catch(() => undefined);
  };

  return (
    <div className={`message-row role-${message.role}`} data-testid="message-row" data-role={message.role}>
      <div className={`message-bubble type-${message.messageType}`}>{message.content}</div>
      <div className="message-meta">
        <span>{formatTime(message.createdAt)}</span>
        {message.role !== 'tool' && (
          <button className="copy-button" onClick={handleCopy} aria-label="Copy message">
            Copy
          </button>
        )}
      </div>
    </div>
  );
}
