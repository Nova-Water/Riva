export type MessageRole = 'user' | 'assistant' | 'system' | 'tool';

export type MessageType =
  | 'message'
  | 'tool_activity'
  | 'confirmation_request'
  | 'error'
  | 'warning';

export interface ConversationMessage {
  id: string;
  role: MessageRole;
  content: string;
  messageType: MessageType;
  createdAt: string;
}

export interface TimelineStep {
  label: string;
  detail?: string;
}

export interface ToolActivity {
  tool_name: string;
  success: boolean;
  message: string;
}

export type AgentResultKind = 'message' | 'confirmation_required' | 'error';

export interface AssistantMessageResponse {
  conversation_id: string;
  kind: AgentResultKind;
  content: string;
  tool_name?: string | null;
  arguments: Record<string, unknown>;
  confirmation_id?: string | null;
  confirmation_message: string;
  timeline: TimelineStep[];
  tool_activity: ToolActivity[];
}

export interface ProviderStatus {
  configured: boolean;
  provider: string;
  detail: string;
}

export interface ConfigStatus {
  llm: ProviderStatus;
  voice: ProviderStatus;
  stt: ProviderStatus;
  myska: ProviderStatus;
  novacore: ProviderStatus;
  allowed_file_roots: string[];
  allowed_applications: string[];
}

export interface SystemStatus {
  backend_connected: boolean;
  llm_connected: boolean;
  voice_connected: boolean;
  stt_available: boolean;
  active_task: string | null;
}

export interface ToolInfo {
  name: string;
  description: string;
  permission_level: 'green' | 'amber' | 'red';
  input_schema: Record<string, unknown>;
}

export interface ConversationSummary {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface DraftEmail {
  id: string;
  recipient: string;
  subject: string;
  body: string;
  related_to: string;
  created_at: string;
}

export type AvatarState = 'idle' | 'listening' | 'thinking' | 'speaking' | 'error' | 'offline';

export type BackendConnectionState = 'connecting' | 'connected' | 'error';
