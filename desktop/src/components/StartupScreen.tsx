import rivaMascot from '../assets/riva-mascot.png';

interface StartupScreenProps {
  error?: string;
}

export function StartupScreen({ error }: StartupScreenProps) {
  return (
    <div className="startup-screen" data-testid="startup-screen">
      <img src={rivaMascot} alt="RIVA — Nova Tech Ltd" className="startup-mascot" draggable={false} />
      <h1>RIVA AI</h1>
      {error ? (
        <>
          <p style={{ color: 'var(--riva-red)' }}>{error}</p>
          <p>
            Open <code>%APPDATA%\RIVA AI\logs\backend-launch.log</code> for the exact reason the backend
            couldn't start. See SETUP_WINDOWS.md if you need setup steps.
          </p>
        </>
      ) : (
        <>
          <div className="startup-spinner" />
          <p>Starting Nova Tech's RIVA assistant. Connecting to the backend service…</p>
        </>
      )}
    </div>
  );
}
