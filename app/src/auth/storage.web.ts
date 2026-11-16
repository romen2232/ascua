import type { RefreshStorage } from "./types";

/**
 * On the web the refresh token lives only in an HttpOnly cookie set by the API, so scripts can
 * never read it. Nothing is stored here.
 */
export const webStorage: RefreshStorage = {
  save: async () => undefined,
  load: async () => null,
  clear: async () => undefined,
};

export const refreshStorage = webStorage;
