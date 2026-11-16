import type { components } from "../api/schema";

export type Me = components["schemas"]["MeResponse"];

export interface RefreshStorage {
  save(token: string): Promise<void>;
  load(): Promise<string | null>;
  clear(): Promise<void>;
}

export type SessionStatus = "loading" | "signed-out" | "mfa" | "enrol" | "signed-in";

/** A TOTP set-up in progress: the otpauth:// URI and the token that proves who is enrolling. */
export interface Enrolment {
  uri: string;
  token: string;
}

export interface SessionState {
  status: SessionStatus;
  user?: Me;
  /** Present while status is "enrol": the account never finished setting up TOTP. */
  enrolment?: Enrolment;
  /** API error code from the last failed action, e.g. "invalid_credentials". */
  error?: string;
}
