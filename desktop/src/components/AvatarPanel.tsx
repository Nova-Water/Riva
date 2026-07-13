import type { AvatarState } from '../types';

/**
 * RIVA's animated avatar. Currently a CSS-animated "visor" placeholder —
 * built so a PNG, animated WebP, video, Lottie file, or GLB model can be
 * dropped in later without changing the surrounding layout or state logic.
 */
const STATE_LABELS: Record<AvatarState, { label: string; sublabel: string }> = {
  idle: { label: 'Ready', sublabel: 'Press and hold the mic, or type a message.' },
  listening: { label: 'Listening', sublabel: 'RIVA is recording your voice.' },
  thinking: { label: 'Thinking', sublabel: 'RIVA is processing your request.' },
  speaking: { label: 'Speaking', sublabel: 'RIVA is responding.' },
  error: { label: 'Something went wrong', sublabel: 'Check the conversation for details.' },
  offline: { label: 'Offline', sublabel: 'Waiting for the RIVA backend to connect.' },
};

interface AvatarPanelProps {
  state: AvatarState;
}

export function AvatarPanel({ state }: AvatarPanelProps) {
  const { label, sublabel } = STATE_LABELS[state];

  return (
    <div className="avatar-panel" data-testid="avatar-panel" data-avatar-state={state}>
      <div className={`avatar-stage avatar-state--${state}`}>
        <div className={`avatar-ring ${state === 'listening' || state === 'thinking' ? 'pulse' : ''}`} />
        <div className="avatar-core">
          <div className="avatar-visor">
            <div className="avatar-visor-line" />
          </div>
        </div>
      </div>
      <div className="avatar-label">{label}</div>
      <div className="avatar-sublabel">{sublabel}</div>
    </div>
  );
}
