import * as SecureStore from "expo-secure-store";

import { createApiClient } from "../../api/client";
import { fakeServer, ME, type Handler } from "../../test/fakeServer";
import { createSession } from "../session";
import { nativeStorage } from "../storage.native";
import { webStorage } from "../storage.web";

jest.mock("expo-secure-store", () => ({
  setItemAsync: jest.fn(async () => undefined),
  getItemAsync: jest.fn(async () => null),
  deleteItemAsync: jest.fn(async () => undefined),
}));

const signInRoutes: Record<string, Handler> = {
  "POST /api/auth/sign-in": () => ({ status: 200, body: { mfa_token: "mfa-1" } }),
  "POST /api/auth/sign-in/totp": () => ({ status: 200, body: { access: "A1", refresh: "R1" } }),
  "GET /api/me": () => ({ status: 200, body: ME }),
};

function setup(routes: Record<string, Handler> = signInRoutes, storage = nativeStorage, platform: "web" | "native" = "native") {
  const server = fakeServer(routes);
  const session = createSession({ storage });
  const api = createApiClient({
    baseUrl: "http://api.test",
    fetch: server.fetch,
    platform,
    auth: session.authHandlers,
  });
  session.connect(api);
  return { session, server };
}

beforeEach(() => jest.clearAllMocks());

it("signIn moves to mfa state", async () => {
  const { session } = setup();
  await session.signIn("romen@example.com", "correct horse battery");
  expect(session.getState().status).toBe("mfa");
});

it("signIn with a wrong password stays signed out with the error code", async () => {
  const { session } = setup({
    "POST /api/auth/sign-in": () => ({ status: 400, body: { error: { code: "invalid_credentials" } } }),
  });
  await session.signIn("romen@example.com", "nope");
  expect(session.getState()).toMatchObject({ status: "signed-out", error: "invalid_credentials" });
});

it("verifyTotp stores refresh in secure store on native", async () => {
  const { session } = setup();
  await session.signIn("romen@example.com", "correct horse battery");
  await session.verifyTotp("123456");
  expect(SecureStore.setItemAsync).toHaveBeenCalledWith("ascua.refresh", "R1");
  expect(session.getState()).toMatchObject({ status: "signed-in", user: ME });
  expect(session.authHandlers.getAccessToken()).toBe("A1");
});

it("web storage never writes the refresh token", async () => {
  await webStorage.save("R1");
  expect(SecureStore.setItemAsync).not.toHaveBeenCalled();
  expect(await webStorage.load()).toBeNull();
});

it("restore signs in from the stored refresh token", async () => {
  jest.mocked(SecureStore.getItemAsync).mockResolvedValueOnce("R0");
  const { session, server } = setup({
    "POST /api/auth/refresh": () => ({ status: 200, body: { access: "A2", refresh: "R2" } }),
    "GET /api/me": () => ({ status: 200, body: ME }),
  });
  await session.restore();
  expect(server.requests[0].body).toEqual({ refresh: "R0" });
  expect(SecureStore.setItemAsync).toHaveBeenCalledWith("ascua.refresh", "R2");
  expect(session.getState().status).toBe("signed-in");
});

it("restore without a session ends signed out", async () => {
  const { session } = setup({
    "POST /api/auth/refresh": () => ({ status: 401, body: { error: { code: "token_not_valid" } } }),
  });
  await session.restore();
  expect(session.getState().status).toBe("signed-out");
});

it("signOut revokes the refresh token and clears storage", async () => {
  const { session, server } = setup({
    ...signInRoutes,
    "POST /api/auth/sign-out": () => ({ status: 204 }),
  });
  await session.signIn("romen@example.com", "correct horse battery");
  await session.verifyTotp("123456");
  jest.mocked(SecureStore.getItemAsync).mockResolvedValueOnce("R1");
  await session.signOut();
  expect(server.requests.at(-1)).toMatchObject({ key: "POST /api/auth/sign-out", body: { refresh: "R1" } });
  expect(SecureStore.deleteItemAsync).toHaveBeenCalledWith("ascua.refresh");
  expect(session.getState().status).toBe("signed-out");
  expect(session.authHandlers.getAccessToken()).toBeNull();
});

it("signIn of an account without TOTP moves to enrol with a fresh set-up", async () => {
  const { session } = setup({
    "POST /api/auth/sign-in": () => ({
      status: 200,
      body: { enrolment: { user_id: "u", provisioning_uri: "otpauth://totp/x?secret=ABC", enrolment_token: "E" } },
    }),
  });
  await session.signIn("romen@example.com", "correct horse battery");
  expect(session.getState()).toMatchObject({
    status: "enrol",
    enrolment: { uri: "otpauth://totp/x?secret=ABC", token: "E" },
  });
});
