/**
 * Typed API client. Adds the access token, identifies web clients (whose refresh token lives in an
 * HttpOnly cookie) and, on a 401, refreshes the session once and retries the request.
 */
import createClient, { type Middleware } from "openapi-fetch";
import { Platform } from "react-native";

import type { paths } from "./schema";

export interface AuthHandlers {
  getAccessToken(): string | null;
  /** Returns a new access token, or null if the session can't be refreshed. */
  refresh(): Promise<string | null>;
}

export interface ApiClientOptions {
  baseUrl: string;
  auth: AuthHandlers;
  platform: "web" | "native";
  fetch?: (request: Request) => Promise<Response>;
}

const AUTH_PATH = "/api/auth/";

export function createApiClient(options: ApiClientOptions) {
  const doFetch = options.fetch ?? ((request: Request) => globalThis.fetch(request));
  const retryCopies = new WeakMap<Request, Request>();

  const withHeaders = (request: Request, token: string | null): Request => {
    const headers = new Headers(request.headers);
    if (token) headers.set("Authorization", `Bearer ${token}`);
    if (options.platform === "web") headers.set("X-Ascua-Client", "web");
    return new Request(request, { headers });
  };

  const middleware: Middleware = {
    onRequest({ request }) {
      const prepared = withHeaders(request, options.auth.getAccessToken());
      retryCopies.set(prepared, prepared.clone());
      return prepared;
    },
    async onResponse({ request, response }) {
      const copy = retryCopies.get(request);
      retryCopies.delete(request);
      const isAuthCall = new URL(request.url).pathname.startsWith(AUTH_PATH);
      if (response.status !== 401 || isAuthCall || !copy) return response;

      const token = await options.auth.refresh();
      if (!token) return response;
      // The retry goes straight to fetch, so it can never trigger a second refresh.
      return doFetch(withHeaders(copy, token));
    },
  };

  const client = createClient<paths>({
    baseUrl: options.baseUrl,
    fetch: doFetch,
    credentials: options.platform === "web" ? "include" : "omit",
  });
  client.use(middleware);
  return client;
}

export type ApiClient = ReturnType<typeof createApiClient>;

let handlers: AuthHandlers = { getAccessToken: () => null, refresh: async () => null };

/** The session module registers how to read and refresh tokens. */
export function setAuthHandlers(next: AuthHandlers): void {
  handlers = next;
}

export const api = createApiClient({
  baseUrl: process.env.EXPO_PUBLIC_API_URL ?? "http://localhost:8000",
  platform: Platform.OS === "web" ? "web" : "native",
  auth: {
    getAccessToken: () => handlers.getAccessToken(),
    refresh: () => handlers.refresh(),
  },
});
