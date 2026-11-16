import * as SecureStore from "expo-secure-store";

import type { RefreshStorage } from "./types";

const KEY = "ascua.refresh";

/** Native apps keep the refresh token in the platform keychain / keystore. */
export const nativeStorage: RefreshStorage = {
  save: (token) => SecureStore.setItemAsync(KEY, token),
  load: () => SecureStore.getItemAsync(KEY),
  clear: () => SecureStore.deleteItemAsync(KEY),
};

export const refreshStorage = nativeStorage;
