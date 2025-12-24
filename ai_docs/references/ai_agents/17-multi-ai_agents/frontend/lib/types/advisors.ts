export interface AdvisorsSnapshotData {
  advisors: string[];
  meetings: string[];
}

export interface ADKSessionResponse {
  id: string;
  appName: string;
  userId: string;
  state: Record<string, unknown>;
  events: unknown[];
  lastUpdateTime: number;
}

export interface ADKAgentRequest {
  app_name: string;
  user_id: string;
  session_id: string;
  new_message: {
    role: string;
    parts: Array<{ text: string }>;
  };
  streaming: boolean;
}
