import { create } from 'zustand';
import { api, ApiError } from '../services/api';
import { AudioRecorder, MicrophoneUnavailableError, SpeechPlayer } from '../services/audio';
import type {
  AvatarState,
  BackendConnectionState,
  ConfigStatus,
  ConversationMessage,
  MessageType,
  TimelineStep,
  ToolActivity,
} from '../types';

interface PendingConfirmation {
  confirmationId: string;
  toolName: string;
  arguments: Record<string, unknown>;
  message: string;
}

interface AssistantState {
  backendState: BackendConnectionState;
  backendError: string;
  configStatus: ConfigStatus | null;

  conversationId: string | null;
  messages: ConversationMessage[];
  timeline: TimelineStep[];
  toolActivity: ToolActivity[];
  pendingConfirmation: PendingConfirmation | null;

  avatarState: AvatarState;
  isRecording: boolean;
  isSending: boolean;
  micError: string | null;

  voiceEnabled: boolean;
  autoPlayVoice: boolean;

  recorder: AudioRecorder;
  player: SpeechPlayer;

  setBackendConnected: () => Promise<void>;
  setBackendError: (message: string) => void;
  refreshConfigStatus: () => Promise<void>;

  addLocalMessage: (role: ConversationMessage['role'], content: string, messageType?: MessageType) => void;
  sendText: (text: string) => Promise<void>;
  startRecording: () => Promise<void>;
  stopRecordingAndSend: () => Promise<void>;
  cancelRecording: () => void;
  confirm: (approve: boolean) => Promise<void>;
  cancelTask: () => Promise<void>;
  stopSpeaking: () => void;
  clearConversation: () => void;
  toggleVoiceEnabled: () => void;
  toggleAutoPlay: () => void;
  speakIfEnabled: (text: string) => Promise<void>;
}

function nowId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

export const useAssistantStore = create<AssistantState>((set, get) => ({
  backendState: 'connecting',
  backendError: '',
  configStatus: null,

  conversationId: null,
  messages: [],
  timeline: [],
  toolActivity: [],
  pendingConfirmation: null,

  avatarState: 'offline',
  isRecording: false,
  isSending: false,
  micError: null,

  voiceEnabled: true,
  autoPlayVoice: true,

  recorder: new AudioRecorder(),
  player: new SpeechPlayer(),

  setBackendConnected: async () => {
    set({ backendState: 'connected', avatarState: 'idle' });
    await get().refreshConfigStatus();
  },

  setBackendError: (message) => set({ backendState: 'error', backendError: message, avatarState: 'error' }),

  refreshConfigStatus: async () => {
    try {
      const status = await api.configStatus();
      set({ configStatus: status });
    } catch {
      // Non-fatal: the status bar simply shows "unknown" until the next refresh.
    }
  },

  addLocalMessage: (role, content, messageType = 'message') => {
    set((state) => ({
      messages: [
        ...state.messages,
        { id: nowId(), role, content, messageType, createdAt: new Date().toISOString() },
      ],
    }));
  },

  sendText: async (text) => {
    const trimmed = text.trim();
    if (!trimmed) return;

    get().addLocalMessage('user', trimmed, 'message');
    set({ isSending: true, avatarState: 'thinking', timeline: [{ label: 'Understanding request' }] });

    try {
      const response = await api.sendMessage(trimmed, get().conversationId);
      set({ conversationId: response.conversation_id, timeline: response.timeline, toolActivity: response.tool_activity });

      for (const activity of response.tool_activity) {
        get().addLocalMessage(
          'tool',
          `${activity.tool_name}: ${activity.message}`,
          activity.success ? 'tool_activity' : 'error'
        );
      }

      if (response.kind === 'confirmation_required' && response.confirmation_id) {
        set({
          pendingConfirmation: {
            confirmationId: response.confirmation_id,
            toolName: response.tool_name || '',
            arguments: response.arguments,
            message: response.confirmation_message,
          },
          avatarState: 'idle',
        });
      } else if (response.kind === 'error') {
        get().addLocalMessage('system', response.content, 'error');
        set({ avatarState: 'error' });
      } else {
        get().addLocalMessage('assistant', response.content, 'message');
        set({ avatarState: 'idle' });
        await get().speakIfEnabled(response.content);
      }
    } catch (error) {
      const message = error instanceof ApiError ? error.message : 'RIVA could not reach the backend.';
      get().addLocalMessage('system', message, 'error');
      set({ avatarState: 'error' });
    } finally {
      set({ isSending: false });
    }
  },

  startRecording: async () => {
    set({ micError: null });
    try {
      await get().recorder.start();
      set({ isRecording: true, avatarState: 'listening' });
    } catch (error) {
      const message = error instanceof MicrophoneUnavailableError ? error.message : 'Could not start recording.';
      set({ micError: message, avatarState: 'idle' });
    }
  },

  stopRecordingAndSend: async () => {
    if (!get().isRecording) return;
    set({ isRecording: false, avatarState: 'thinking', isSending: true });
    try {
      const blob = await get().recorder.stop();
      const { text } = await api.transcribeAudio(blob);
      if (!text.trim()) {
        get().addLocalMessage('system', 'RIVA did not detect any speech in that recording.', 'warning');
        set({ avatarState: 'idle', isSending: false });
        return;
      }
      set({ isSending: false });
      await get().sendText(text);
    } catch (error) {
      const message = error instanceof ApiError ? error.message : 'Transcription failed.';
      get().addLocalMessage('system', message, 'error');
      set({ avatarState: 'idle', isSending: false });
    }
  },

  cancelRecording: () => {
    get().recorder.cancel();
    set({ isRecording: false, avatarState: 'idle' });
  },

  confirm: async (approve) => {
    const pending = get().pendingConfirmation;
    const conversationId = get().conversationId;
    if (!pending || !conversationId) return;

    set({ pendingConfirmation: null, avatarState: 'thinking', isSending: true });
    try {
      const response = await api.confirmAction(conversationId, pending.confirmationId, approve);
      set({ timeline: response.timeline, toolActivity: response.tool_activity });
      for (const activity of response.tool_activity) {
        get().addLocalMessage(
          'tool',
          `${activity.tool_name}: ${activity.message}`,
          activity.success ? 'tool_activity' : 'error'
        );
      }
      get().addLocalMessage('assistant', response.content, 'message');
      set({ avatarState: 'idle' });
      await get().speakIfEnabled(response.content);
    } catch (error) {
      const message = error instanceof ApiError ? error.message : 'Could not process the confirmation.';
      get().addLocalMessage('system', message, 'error');
      set({ avatarState: 'error' });
    } finally {
      set({ isSending: false });
    }
  },

  cancelTask: async () => {
    const conversationId = get().conversationId;
    get().stopSpeaking();
    set({ isSending: false, avatarState: 'idle', pendingConfirmation: null });
    if (conversationId) {
      try {
        await api.cancelTask(conversationId);
      } catch {
        // Cancelling is best-effort; the UI has already reset regardless.
      }
    }
  },

  stopSpeaking: () => {
    get().player.stop();
    if (get().avatarState === 'speaking') set({ avatarState: 'idle' });
  },

  clearConversation: () => {
    get().stopSpeaking();
    set({
      conversationId: null,
      messages: [],
      timeline: [],
      toolActivity: [],
      pendingConfirmation: null,
      avatarState: 'idle',
    });
  },

  toggleVoiceEnabled: () => set((state) => ({ voiceEnabled: !state.voiceEnabled })),
  toggleAutoPlay: () => set((state) => ({ autoPlayVoice: !state.autoPlayVoice })),

  speakIfEnabled: async (text) => {
    const { voiceEnabled, autoPlayVoice, configStatus } = get();
    if (!voiceEnabled || !autoPlayVoice) return;
    if (configStatus && !configStatus.voice.configured) return;

    try {
      const blob = await api.synthesizeSpeech(text);
      set({ avatarState: 'speaking' });
      await get().player.play(blob, () => {
        if (get().avatarState === 'speaking') set({ avatarState: 'idle' });
      });
    } catch {
      // Voice failures are non-fatal — RIVA has already shown the text response.
      if (get().avatarState === 'speaking') set({ avatarState: 'idle' });
    }
  },
}));
