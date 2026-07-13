import { useEffect, useState } from 'react';
import { api } from '../services/api';
import { AudioRecorder } from '../services/audio';
import { useAssistantStore } from '../stores/useAssistantStore';

interface SettingsPageProps {
  onClose: () => void;
}

const RETENTION_KEY = 'riva.settings.retention';
const DEFAULT_RETENTION = 'Keep until manually cleared';

export function SettingsPage({ onClose }: SettingsPageProps) {
  const configStatus = useAssistantStore((s) => s.configStatus);
  const voiceEnabled = useAssistantStore((s) => s.voiceEnabled);
  const autoPlayVoice = useAssistantStore((s) => s.autoPlayVoice);
  const toggleVoiceEnabled = useAssistantStore((s) => s.toggleVoiceEnabled);
  const toggleAutoPlay = useAssistantStore((s) => s.toggleAutoPlay);
  const clearConversation = useAssistantStore((s) => s.clearConversation);

  const [inputDevices, setInputDevices] = useState<MediaDeviceInfo[]>([]);
  const [outputDevices, setOutputDevices] = useState<MediaDeviceInfo[]>([]);
  const [retention, setRetention] = useState(
    () => localStorage.getItem(RETENTION_KEY) || DEFAULT_RETENTION
  );
  const [clearing, setClearing] = useState(false);
  const [reindexing, setReindexing] = useState(false);
  const [reindexMessage, setReindexMessage] = useState('');

  useEffect(() => {
    AudioRecorder.listInputDevices().then(setInputDevices);
    AudioRecorder.listOutputDevices().then(setOutputDevices);
  }, []);

  const handleRetentionChange = (value: string) => {
    setRetention(value);
    localStorage.setItem(RETENTION_KEY, value);
  };

  const handleClearMemory = async () => {
    setClearing(true);
    try {
      const conversations = await api.listConversations();
      await Promise.all(conversations.map((c) => api.deleteConversation(c.id)));
      clearConversation();
    } finally {
      setClearing(false);
    }
  };

  const handleReindex = async () => {
    setReindexing(true);
    setReindexMessage('');
    try {
      const result = await api.reindexKnowledge();
      setReindexMessage(`Indexed ${result.documents_indexed} document(s).`);
    } catch {
      setReindexMessage('Reindex failed. Check the logs for details.');
    } finally {
      setReindexing(false);
    }
  };

  const handleOpenLogs = () => {
    window.riva?.openLogsFolder();
  };

  return (
    <div className="settings-overlay" data-testid="settings-page">
      <div className="settings-page">
        <div className="settings-header">
          <h2>Settings</h2>
          <button className="icon-button" onClick={onClose}>
            Close
          </button>
        </div>

        <section className="panel settings-section">
          <h3>AI Provider</h3>
          <div className="settings-row">
            <span className="settings-row-label">LLM Model</span>
            <span className="settings-row-value">{configStatus?.llm.detail || 'Not configured'}</span>
          </div>
          <div className="settings-row">
            <span className="settings-row-label">Voice Provider</span>
            <span className="settings-row-value">{configStatus?.voice.provider || 'elevenlabs'}</span>
          </div>
          <div className="settings-row">
            <span className="settings-row-label">Voice ID (masked)</span>
            <span className="settings-row-value">{configStatus?.voice.detail || 'Not configured'}</span>
          </div>
          <div className="settings-row">
            <span className="settings-row-label">Speech-to-Text Model</span>
            <span className="settings-row-value">{configStatus?.stt.detail || 'base'}</span>
          </div>
        </section>

        <section className="panel settings-section">
          <h3>Audio Devices</h3>
          <div className="settings-row">
            <span className="settings-row-label">Microphone</span>
            <select className="settings-row-value" defaultValue="">
              <option value="">System default</option>
              {inputDevices.map((d) => (
                <option key={d.deviceId} value={d.deviceId}>
                  {d.label || 'Microphone'}
                </option>
              ))}
            </select>
          </div>
          <div className="settings-row">
            <span className="settings-row-label">Speaker</span>
            <select className="settings-row-value" defaultValue="">
              <option value="">System default</option>
              {outputDevices.map((d) => (
                <option key={d.deviceId} value={d.deviceId}>
                  {d.label || 'Speaker'}
                </option>
              ))}
            </select>
          </div>
        </section>

        <section className="panel settings-section">
          <h3>Voice</h3>
          <div className="settings-row">
            <span className="settings-row-label">Voice enabled</span>
            <button
              className={`toggle ${voiceEnabled ? 'on' : ''}`}
              onClick={toggleVoiceEnabled}
              aria-label="Toggle voice enabled"
            />
          </div>
          <div className="settings-row">
            <span className="settings-row-label">Auto-play voice responses</span>
            <button
              className={`toggle ${autoPlayVoice ? 'on' : ''}`}
              onClick={toggleAutoPlay}
              aria-label="Toggle auto-play voice"
            />
          </div>
        </section>

        <section className="panel settings-section">
          <h3>Approved Access</h3>
          <div className="settings-row-label" style={{ marginBottom: 6 }}>
            Approved file folders
          </div>
          <div className="settings-list">
            {(configStatus?.allowed_file_roots || []).map((root) => (
              <div key={root}>{root}</div>
            ))}
          </div>
          <div className="settings-row-label" style={{ margin: '12px 0 6px' }}>
            Approved applications
          </div>
          <div className="settings-list">
            {(configStatus?.allowed_applications || []).map((appName) => (
              <div key={appName}>{appName}</div>
            ))}
          </div>
        </section>

        <section className="panel settings-section">
          <h3>Memory &amp; Knowledgebase</h3>
          <div className="settings-row">
            <span className="settings-row-label">Conversation retention</span>
            <select
              className="settings-row-value"
              value={retention}
              onChange={(e) => handleRetentionChange(e.target.value)}
            >
              <option>Keep until manually cleared</option>
              <option>Keep for 30 days</option>
              <option>Keep for 7 days</option>
            </select>
          </div>
          <div className="settings-row">
            <span className="settings-row-label">Clear all memory</span>
            <button className="icon-button" onClick={handleClearMemory} disabled={clearing}>
              {clearing ? 'Clearing…' : 'Clear memory'}
            </button>
          </div>
          <div className="settings-row">
            <span className="settings-row-label">Knowledgebase index</span>
            <button className="icon-button" onClick={handleReindex} disabled={reindexing}>
              {reindexing ? 'Reindexing…' : 'Reindex now'}
            </button>
          </div>
          {reindexMessage && <div className="settings-row-label">{reindexMessage}</div>}
        </section>

        <section className="panel settings-section">
          <h3>Diagnostics</h3>
          <div className="settings-row">
            <span className="settings-row-label">Application logs</span>
            <button className="icon-button" onClick={handleOpenLogs}>
              Open logs folder
            </button>
          </div>
          <div className="settings-row">
            <span className="settings-row-label">MYSKA Pay integration</span>
            <span className="settings-row-value">{configStatus?.myska.detail || 'Not connected'}</span>
          </div>
          <div className="settings-row">
            <span className="settings-row-label">NovaCore integration</span>
            <span className="settings-row-value">{configStatus?.novacore.detail || 'Not connected'}</span>
          </div>
        </section>
      </div>
    </div>
  );
}
