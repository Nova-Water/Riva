import { afterEach, describe, expect, it, vi } from 'vitest';
import { useAssistantStore } from '../src/stores/useAssistantStore';
import * as apiModule from '../src/services/api';
import type { ConfigStatus } from '../src/types';

const initialState = useAssistantStore.getState();

afterEach(() => {
  vi.restoreAllMocks();
  useAssistantStore.setState(initialState, true);
});

function makeConfigStatus(overrides: Partial<ConfigStatus> = {}): ConfigStatus {
  return {
    llm: { configured: true, provider: 'openai_compatible', detail: 'gpt-4o-mini' },
    voice: { configured: false, provider: 'elevenlabs', detail: 'Not configured' },
    stt: { configured: true, provider: 'faster_whisper', detail: 'base' },
    myska: { configured: false, provider: 'myska_pay', detail: 'Not connected' },
    novacore: { configured: false, provider: 'novacore', detail: 'Not connected' },
    allowed_file_roots: [],
    allowed_applications: [],
    ...overrides,
  };
}

describe('Text-only fallback', () => {
  it('does not attempt speech synthesis when the voice provider is not configured', async () => {
    const synthesizeSpy = vi.spyOn(apiModule.api, 'synthesizeSpeech');
    useAssistantStore.setState({ configStatus: makeConfigStatus() });

    await useAssistantStore.getState().speakIfEnabled('Here is your answer in text.');

    expect(synthesizeSpy).not.toHaveBeenCalled();
    expect(useAssistantStore.getState().avatarState).not.toBe('speaking');
  });

  it('does not attempt speech synthesis when voice is muted by the user', async () => {
    const synthesizeSpy = vi.spyOn(apiModule.api, 'synthesizeSpeech');
    useAssistantStore.setState({ configStatus: makeConfigStatus({ voice: { configured: true, provider: 'elevenlabs', detail: 'abcd****' } }), voiceEnabled: false });

    await useAssistantStore.getState().speakIfEnabled('Here is your answer in text.');

    expect(synthesizeSpy).not.toHaveBeenCalled();
  });

  it('falls back to text gracefully if speech synthesis throws', async () => {
    vi.spyOn(apiModule.api, 'synthesizeSpeech').mockRejectedValue(new apiModule.ApiError('Voice unavailable'));
    useAssistantStore.setState({
      configStatus: makeConfigStatus({ voice: { configured: true, provider: 'elevenlabs', detail: 'abcd****' } }),
      voiceEnabled: true,
      autoPlayVoice: true,
    });

    await expect(useAssistantStore.getState().speakIfEnabled('Text response')).resolves.not.toThrow();
    expect(useAssistantStore.getState().avatarState).not.toBe('speaking');
  });
});
