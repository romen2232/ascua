import type { components } from "../api/schema";

export type Me = components["schemas"]["MeResponse"];

export interface RefreshStorage {
  save(token: string): Promise<void>;
  load(): Promise<string | null>;
  clear(): Promise<void>;
}

export type SessionStatus = "loading" | "signed-out" | "mfa" | "signed-in";

export interface SessionState {
  status: SessionStatus;
  user?: Me;
  /** API error code from the last failed action, e.g. "invalid_credentials". */
  error?: string;
}
