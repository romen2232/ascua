/**
 * Session state: the access token lives in memory only; the refresh token goes to platform
 * storage on native and stays in an HttpOnly cookie on the web.
 */
import { useSyncExternalStore } from "react";

import { api, setAuthHandlers, type ApiClient, type AuthHandlers } from "../api/client";
import { errorCode } from "../api/errors";
import { refreshStorage } from "./storage";
import type { RefreshStorage, SessionState } from "./types";

export function createSession({ storage }: { storage: RefreshStorage }) {
  let client: ApiClient | null = null;
  let state: SessionState = { status: "loading" };
  let access: string | null = null;
  let mfaToken: string | null = null;
  let refreshing: Promise<string | null> | null = null;
  const listeners = new Set<() => void>();

  const set = (next: SessionState) => {
    state = next;
    listeners.forEach((listener) => listener());
  };
  const http = () => {
    if (!client) throw new Error("Session is not connected to an API client");
    return client;
  };

  async function endSession(error?: string) {
    access = null;
    mfaToken = null;
    await storage.clear();
    set({ status: "signed-out", error });
  }

  async function loadUser() {
    const { data, error } = await http().GET("/api/me");
    if (!data) return endSession(errorCode(error));
    set({ status: "signed-in", user: data });
  }

  function refresh(): Promise<string | null> {
    refreshing ??= (async () => {
      const stored = await storage.load();
      const { data } = await http().POST("/api/auth/refresh", {
        body: stored ? { refresh: stored } : {},
      });
      if (!data) {
        await endSession();
        return null;
      }
      access = data.access;
      if (data.refresh) await storage.save(data.refresh);
      return access;
    })().finally(() => {
      refreshing = null;
    });
    return refreshing;
  }

  const authHandlers: AuthHandlers = { getAccessToken: () => access, refresh };

  return {
    authHandlers,
    connect(apiClient: ApiClient) {
      client = apiClient;
    },
    getState: () => state,
    subscribe(listener: () => void) {
      listeners.add(listener);
      return () => listeners.delete(listener);
    },

    async restore() {
      try {
        if (await refresh()) await loadUser();
      } catch {
        await endSession("network");
      }
    },

    async signIn(email: string, password: string) {
      try {
        const { data, error } = await http().POST("/api/auth/sign-in", { body: { email, password } });
        if (!data) return set({ status: "signed-out", error: errorCode(error) });
        if (data.enrolment) {
          const { provisioning_uri: uri, enrolment_token: token } = data.enrolment;
          return set({ status: "enrol", enrolment: { uri, token } });
        }
        mfaToken = data.mfa_token ?? null;
        set({ status: "mfa" });
      } catch {
        set({ status: "signed-out", error: "network" });
      }
    },

    async verifyTotp(code: string) {
      try {
        const { data, error } = await http().POST("/api/auth/sign-in/totp", {
          body: { mfa_token: mfaToken ?? "", code },
        });
        if (!data) {
          const reason = errorCode(error);
          return reason === "mfa_invalid" ? endSession(reason) : set({ status: "mfa", error: reason });
        }
        access = data.access;
        mfaToken = null;
        if (data.refresh) await storage.save(data.refresh);
        await loadUser();
      } catch {
        set({ status: "mfa", error: "network" });
      }
    },

    /** TOTP set-up is done; the user signs in again with their new code. */
    finishEnrolment() {
      set({ status: "signed-out" });
    },

    async signOut() {
      const stored = await storage.load();
      try {
        await http().POST("/api/auth/sign-out", { body: stored ? { refresh: stored } : {} });
      } finally {
        await endSession();
      }
    },
  };
}

export type Session = ReturnType<typeof createSession>;

export const session = createSession({ storage: refreshStorage });
session.connect(api);
setAuthHandlers(session.authHandlers);

export function useSession() {
  const state = useSyncExternalStore(session.subscribe, session.getState, session.getState);
  return {
    ...state,
    signIn: session.signIn,
    verifyTotp: session.verifyTotp,
    signOut: session.signOut,
  };
}
