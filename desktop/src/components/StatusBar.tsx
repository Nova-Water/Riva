import { useAssistantStore } from '../stores/useAssistantStore';

function dotClass(ok: boolean | undefined): string {
  return ok ? 'ok' : 'warn';
}

export function StatusBar() {
  const backendState = useAssistantStore((s) => s.backendState);
  const configStatus = useAssistantStore((s) => s.configStatus);
  const avatarState = useAssistantStore((s) => s.avatarState);
  const isRecording = useAssistantStore((s) => s.isRecording);
  const micError = useAssistantStore((s) => s.micError);

  const backendConnected = backendState === 'connected';
  const llmConnected = !!configStatus?.llm.configured;
  const voiceConnected = !!configStatus?.voice.configured;

  return (
    <div className="status-bar" data-testid="status-bar">
      <span className="status-chip">
        <span className={`status-dot ${backendConnected ? 'ok' : backendState === 'error' ? 'error' : 'warn'}`} />
        Backend {backendConnected ? 'Connected' : backendState === 'error' ? 'Offline' : 'Connecting'}
      </span>
      <span className="status-chip">
        <span className={`status-dot ${dotClass(llmConnected)}`} />
        LLM {llmConnected ? 'Connected' : 'Not configured'}
      </span>
      <span className="status-chip">
        <span className={`status-dot ${dotClass(voiceConnected)}`} />
        Voice {voiceConnected ? 'Connected' : 'Text-only mode'}
      </span>
      <span className="status-chip">
        <span className={`status-dot ${micError ? 'error' : isRecording ? 'ok' : ''}`} />
        Mic {micError ? 'Error' : isRecording ? 'Recording' : 'Idle'}
      </span>
      <span className="status-chip">
        <span className={`status-dot ${avatarState === 'error' ? 'error' : 'ok'}`} />
        {avatarState[0].toUpperCase() + avatarState.slice(1)}
      </span>
    </div>
  );
}
