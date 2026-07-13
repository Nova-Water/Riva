import type {
  AssistantMessageResponse,
  ConfigStatus,
  ConversationSummary,
  DraftEmail,
  SystemStatus,
  ToolInfo,
} from '../types';
import { getBackendBaseUrl } from './backendConnection';

export class ApiError extends Error {
  constructor(message: string, public status?: number) {
    super(message);
    this.name = 'ApiError';
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const baseUrl = await getBackendBaseUrl();
  let response: Response;
  try {
    response = await fetch(`${baseUrl}${path}`, {
      headers: { 'Content-Type': 'application/json' },
      ...init,
    });
  } catch {
    throw new ApiError('Could not reach the RIVA backend. Is it running?');
  }

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      detail = body.detail || body.error || detail;
    } catch {
      // response had no JSON body
    }
    throw new ApiError(detail, response.status);
  }

  if (response.status === 204) return undefined as T;

  const contentType = response.headers.get('content-type') || '';
  if (contentType.includes('application/json')) {
    return (await response.json()) as T;
  }
  return undefined as T;
}

export const api = {
  health: () => request<{ status: string; app_name: string; app_env: string }>('/health'),

  configStatus: () => request<ConfigStatus>('/config/status'),

  systemStatus: () => request<SystemStatus>('/system/status'),

  sendMessage: (text: string, conversationId?: string | null) =>
    request<AssistantMessageResponse>('/assistant/message', {
      method: 'POST',
      body: JSON.stringify({ text, conversation_id: conversationId ?? null }),
    }),

  confirmAction: (conversationId: string, confirmationId: string, approve: boolean) =>
    request<AssistantMessageResponse>('/assistant/confirm', {
      method: 'POST',
      body: JSON.stringify({ conversation_id: conversationId, confirmation_id: confirmationId, approve }),
    }),

  cancelTask: (conversationId: string) =>
    request<{ cancelled: boolean }>('/assistant/cancel', {
      method: 'POST',
      body: JSON.stringify({ conversation_id: conversationId }),
    }),

  transcribeAudio: async (audioBlob: Blob): Promise<{ text: string }> => {
    const baseUrl = await getBackendBaseUrl();
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.webm');
    const response = await fetch(`${baseUrl}/speech/transcribe`, { method: 'POST', body: formData });
    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      throw new ApiError(body.detail || 'Transcription failed.', response.status);
    }
    return response.json();
  },

  synthesizeSpeech: async (text: string): Promise<Blob> => {
    const baseUrl = await getBackendBaseUrl();
    const response = await fetch(`${baseUrl}/speech/synthesize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    });
    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      throw new ApiError(body.detail || 'Voice synthesis failed.', response.status);
    }
    return response.blob();
  },

  listConversations: () => request<ConversationSummary[]>('/conversations'),

  getConversation: (id: string) => request(`/conversations/${id}`),

  deleteConversation: (id: string) => request<{ deleted: boolean }>(`/conversations/${id}`, { method: 'DELETE' }),

  listDrafts: () => request<DraftEmail[]>('/drafts'),

  reindexKnowledge: () => request<{ documents_indexed: number }>('/knowledge/reindex', { method: 'POST' }),

  listTools: () => request<ToolInfo[]>('/tools'),
};
