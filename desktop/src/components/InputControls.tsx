import { useState } from 'react';
import { useAssistantStore } from '../stores/useAssistantStore';

interface InputControlsProps {
  onOpenSettings: () => void;
}

export function InputControls({ onOpenSettings }: InputControlsProps) {
  const [text, setText] = useState('');
  const isRecording = useAssistantStore((s) => s.isRecording);
  const isSending = useAssistantStore((s) => s.isSending);
  const micError = useAssistantStore((s) => s.micError);
  const voiceEnabled = useAssistantStore((s) => s.voiceEnabled);
  const avatarState = useAssistantStore((s) => s.avatarState);
  const sendText = useAssistantStore((s) => s.sendText);
  const startRecording = useAssistantStore((s) => s.startRecording);
  const stopRecordingAndSend = useAssistantStore((s) => s.stopRecordingAndSend);
  const cancelRecording = useAssistantStore((s) => s.cancelRecording);
  const cancelTask = useAssistantStore((s) => s.cancelTask);
  const stopSpeaking = useAssistantStore((s) => s.stopSpeaking);
  const toggleVoiceEnabled = useAssistantStore((s) => s.toggleVoiceEnabled);

  const handleSend = () => {
    if (!text.trim() || isSending) return;
    void sendText(text);
    setText('');
  };

  const handleMicClick = () => {
    if (isRecording) {
      void stopRecordingAndSend();
    } else {
      void startRecording();
    }
  };

  const busy = isSending || avatarState === 'thinking';

  return (
    <div className="panel input-controls" data-testid="input-controls">
      {micError && <div className="mic-error">{micError}</div>}

      <div className="input-row">
        <button
          className={`mic-button ${isRecording ? 'recording' : ''}`}
          onClick={handleMicClick}
          aria-label={isRecording ? 'Stop recording' : 'Start recording (push to talk)'}
          data-testid="mic-button"
        >
          {isRecording ? '■' : '🎙'}
        </button>

        {isRecording && (
          <button className="icon-button" onClick={cancelRecording} data-testid="stop-recording-button">
            Cancel recording
          </button>
        )}

        <input
          className="text-input"
          placeholder="Message RIVA…"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') handleSend();
          }}
          disabled={isRecording}
          data-testid="text-input"
        />

        <button className="send-button" onClick={handleSend} disabled={!text.trim() || isSending || isRecording}>
          Send
        </button>
      </div>

      <div className="secondary-row">
        <div className="secondary-actions">
          <button className="icon-button" onClick={cancelTask} disabled={!busy && avatarState !== 'speaking'}>
            Cancel task
          </button>
          <button
            className="icon-button"
            onClick={() => {
              stopSpeaking();
            }}
            disabled={avatarState !== 'speaking'}
          >
            Stop speaking
          </button>
        </div>
        <div className="secondary-actions">
          <button
            className={`icon-button ${voiceEnabled ? '' : 'active'}`}
            onClick={toggleVoiceEnabled}
            data-testid="mute-toggle"
          >
            {voiceEnabled ? 'Mute voice' : 'Voice muted'}
          </button>
          <button className="icon-button" onClick={onOpenSettings}>
            Settings
          </button>
        </div>
      </div>
    </div>
  );
}
