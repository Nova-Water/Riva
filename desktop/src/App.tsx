import { useState } from 'react';
import { AvatarPanel } from './components/AvatarPanel';
import { ConfirmationModal } from './components/ConfirmationModal';
import { ConversationPanel } from './components/ConversationPanel';
import { InputControls } from './components/InputControls';
import { SettingsPage } from './components/SettingsPage';
import { StartupScreen } from './components/StartupScreen';
import { StatusBar } from './components/StatusBar';
import { TaskTimeline } from './components/TaskTimeline';
import { useBackendConnection } from './hooks/useBackendConnection';
import { useAssistantStore } from './stores/useAssistantStore';

export default function App() {
  useBackendConnection();

  const backendState = useAssistantStore((s) => s.backendState);
  const backendError = useAssistantStore((s) => s.backendError);
  const avatarState = useAssistantStore((s) => s.avatarState);
  const timeline = useAssistantStore((s) => s.timeline);

  const [settingsOpen, setSettingsOpen] = useState(false);

  if (backendState !== 'connected') {
    return <StartupScreen error={backendState === 'error' ? backendError : undefined} />;
  }

  return (
    <div className="app-shell">
      <header className="top-bar">
        <div className="brand">
          <div className="brand-mark">R</div>
          <div className="brand-text">
            <h1>RIVA AI</h1>
            <span>Nova Tech Ltd</span>
          </div>
        </div>
        <StatusBar />
        <div className="top-bar-actions">
          <button className="icon-button" onClick={() => setSettingsOpen(true)}>
            Settings
          </button>
        </div>
      </header>

      <div className="app-body">
        <div className="panel" style={{ display: 'flex', flexDirection: 'column' }}>
          <AvatarPanel state={avatarState} />
          <TaskTimeline steps={timeline} />
        </div>

        <div style={{ display: 'grid', gridTemplateRows: '1fr auto', gap: 16, minHeight: 0 }}>
          <ConversationPanel />
          <InputControls onOpenSettings={() => setSettingsOpen(true)} />
        </div>
      </div>

      <ConfirmationModal />
      {settingsOpen && <SettingsPage onClose={() => setSettingsOpen(false)} />}
    </div>
  );
}
