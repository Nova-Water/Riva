import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { MessageBubble } from '../src/components/MessageBubble';
import type { ConversationMessage } from '../src/types';

function makeMessage(overrides: Partial<ConversationMessage> = {}): ConversationMessage {
  return {
    id: '1',
    role: 'assistant',
    content: 'Hello from RIVA',
    messageType: 'message',
    createdAt: new Date().toISOString(),
    ...overrides,
  };
}

describe('MessageBubble', () => {
  it('renders user message content aligned as a user row', () => {
    render(<MessageBubble message={makeMessage({ role: 'user', content: 'What is the PC status?' })} />);
    const row = screen.getByTestId('message-row');
    expect(row).toHaveAttribute('data-role', 'user');
    expect(screen.getByText('What is the PC status?')).toBeInTheDocument();
  });

  it('renders assistant messages', () => {
    render(<MessageBubble message={makeMessage({ role: 'assistant', content: 'Here is your PC status.' })} />);
    expect(screen.getByText('Here is your PC status.')).toBeInTheDocument();
  });

  it('renders tool activity messages without a copy button', () => {
    render(
      <MessageBubble
        message={makeMessage({ role: 'tool', content: 'get_pc_status: Retrieved status.', messageType: 'tool_activity' })}
      />
    );
    expect(screen.getByText('get_pc_status: Retrieved status.')).toBeInTheDocument();
    expect(screen.queryByLabelText('Copy message')).not.toBeInTheDocument();
  });

  it('renders error messages with the error type class', () => {
    render(<MessageBubble message={makeMessage({ role: 'system', content: 'Something failed.', messageType: 'error' })} />);
    const bubble = screen.getByText('Something failed.');
    expect(bubble.className).toContain('type-error');
  });
});
