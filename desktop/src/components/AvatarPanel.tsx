import rivaPortrait from '../assets/riva-avatar-portrait.png';
import type { AvatarState } from '../types';

/**
 * RIVA's animated avatar. Uses Nova Tech's official RIVA mascot artwork
 * (src/assets/riva-avatar-portrait.png) with a state-driven glow, breathing
 * animation, and rotating rings. Swappable later for an animated WebP,
 * video, Lottie file, or GLB model without changing the surrounding layout
 * or state logic — see src/assets/README.md.
 */
const STATE_LABELS: Record<AvatarState, { label: string; sublabel: string }> = {
  idle: { label: 'Ready', sublabel: 'Press and hold the mic, or type a message.' },
  listening: { label: 'Listening', sublabel: 'RIVA is recording your voice.' },
  thinking: { label: 'Thinking', sublabel: 'RIVA is processing your request.' },
  speaking: { label: 'Speaking', sublabel: 'RIVA is responding.' },
  error: { label: 'Something went wrong', sublabel: 'Check the conversation for details.' },
  offline: { label: 'Offline', sublabel: 'Waiting for the RIVA backend to connect.' },
};

const SHOW_WAVE_STATES: AvatarState[] = ['listening', 'speaking'];

interface AvatarPanelProps {
  state: AvatarState;
}

export function AvatarPanel({ state }: AvatarPanelProps) {
  const { label, sublabel } = STATE_LABELS[state];
  const showWave = SHOW_WAVE_STATES.includes(state);

  return (
    <div className="avatar-panel" data-testid="avatar-panel" data-avatar-state={state}>
      <div className={`avatar-stage avatar-state--${state}`}>
        <div className="avatar-ring avatar-ring--outer" />
        <div className="avatar-ring avatar-ring--inner" />
        <div className="avatar-glow" />
        <img className="avatar-portrait" src={rivaPortrait} alt="RIVA — Nova Tech Ltd" draggable={false} />
        {showWave && (
          <div className="avatar-wave" aria-hidden="true">
            {[0, 1, 2, 3, 4].map((bar) => (
              <div className="avatar-wave-bar" key={bar} />
            ))}
          </div>
        )}
      </div>
      <div className="avatar-label">{label}</div>
      <div className="avatar-sublabel">{sublabel}</div>
    </div>
  );
}
