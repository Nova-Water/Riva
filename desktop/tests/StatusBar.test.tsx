import { render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it } from 'vitest';
import { StatusBar } from '../src/components/StatusBar';
import { useAssistantStore } from '../src/stores/useAssistantStore';
import type { ConfigStatus } from '../src/types';

const initialState = useAssistantStore.getState();

afterEach(() => {
  useAssistantStore.setState(initialState, true);
});

function makeConfigStatus(overrides: Partial<ConfigStatus> = {}): ConfigStatus {
  return {
    llm: { configured: false, provider: 'openai_compatible', detail: 'Not configured' },
    voice: { configured: false, provider: 'elevenlabs', detail: 'Not configured' },
    stt: { configured: true, provider: 'faster_whisper', detail: 'base' },
    myska: { configured: false, provider: 'myska_pay', detail: 'Not connected' },
    novacore: { configured: false, provider: 'novacore', detail: 'Not connected' },
    allowed_file_roots: [],
    allowed_applications: [],
    ...overrides,
  };
}

describe('StatusBar provider indicators', () => {
  it('shows "Not configured" for LLM when no API key is set', () => {
    useAssistantStore.setState({ backendState: 'connected', configStatus: makeConfigStatus() });
    render(<StatusBar />);
    expect(screen.getByText(/LLM Not configured/)).toBeInTheDocument();
  });

  it('shows "Text-only mode" for voice when not configured (text-only fallback)', () => {
    useAssistantStore.setState({ backendState: 'connected', configStatus: makeConfigStatus() });
    render(<StatusBar />);
    expect(screen.getByText(/Voice Text-only mode/)).toBeInTheDocument();
  });

  it('shows "Connected" for providers once configured', () => {
    useAssistantStore.setState({
      backendState: 'connected',
      configStatus: makeConfigStatus({
        llm: { configured: true, provider: 'openai_compatible', detail: 'gpt-4o-mini' },
        voice: { configured: true, provider: 'elevenlabs', detail: 'abcd****' },
      }),
    });
    render(<StatusBar />);
    expect(screen.getByText(/LLM Connected/)).toBeInTheDocument();
    expect(screen.getByText(/Voice Connected/)).toBeInTheDocument();
  });

  it('reflects backend connection state', () => {
    useAssistantStore.setState({ backendState: 'error' });
    render(<StatusBar />);
    expect(screen.getByText(/Backend Offline/)).toBeInTheDocument();
  });
});
