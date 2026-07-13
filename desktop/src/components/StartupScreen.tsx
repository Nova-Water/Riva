interface StartupScreenProps {
  error?: string;
}

export function StartupScreen({ error }: StartupScreenProps) {
  return (
    <div className="startup-screen" data-testid="startup-screen">
      <div className="brand-mark" style={{ width: 52, height: 52, borderRadius: 16, fontSize: 20 }}>
        R
      </div>
      <h1>RIVA AI</h1>
      {error ? (
        <>
          <p style={{ color: 'var(--riva-red)' }}>{error}</p>
          <p>
            Check that the backend dependencies are installed and that your <code>.env</code> file exists.
            See SETUP_WINDOWS.md for step-by-step instructions.
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
