import { fireEvent, render, screen } from "@testing-library/react-native";

import i18n from "../../i18n";
import { fakeServer } from "../../test/fakeServer";
import { InviteScreen } from "../InviteScreen";
import { SignInScreen } from "../SignInScreen";

const mockRouter = { push: jest.fn(), replace: jest.fn() };
jest.mock("expo-router", () => ({
  useRouter: () => mockRouter,
  useLocalSearchParams: () => ({ token: "invite-token" }),
}));
jest.mock("expo-secure-store", () => ({
  setItemAsync: jest.fn(async () => undefined),
  getItemAsync: jest.fn(async () => null),
  deleteItemAsync: jest.fn(async () => undefined),
}));

const URI = "otpauth://totp/ascua:friend%40example.com?secret=JBSWY3DPEHPK3PXP&issuer=ascua";

beforeEach(async () => {
  await i18n.changeLanguage("en");
  jest.clearAllMocks();
});

function serve(routes: Parameters<typeof fakeServer>[0]) {
  const server = fakeServer(routes);
  globalThis.fetch = server.fetch as unknown as typeof fetch;
  return server;
}

it("sign-in screen shows translated invalid_credentials error", async () => {
  serve({
    "POST /api/auth/sign-in": () => ({ status: 400, body: { error: { code: "invalid_credentials" } } }),
  });
  await render(<SignInScreen />);
  await fireEvent.changeText(screen.getByLabelText("Email"), "romen@example.com");
  await fireEvent.changeText(screen.getByLabelText("Password"), "wrong password");
  await fireEvent.press(screen.getByRole("button", { name: "Sign in" }));
  expect(await screen.findByText("Email or password is not correct.")).toBeTruthy();
  expect(mockRouter.push).not.toHaveBeenCalled();
});

it("sign-in screen goes to the code step after a correct password", async () => {
  serve({ "POST /api/auth/sign-in": () => ({ status: 200, body: { mfa_token: "m" } }) });
  await render(<SignInScreen />);
  await fireEvent.changeText(screen.getByLabelText("Email"), "romen@example.com");
  await fireEvent.changeText(screen.getByLabelText("Password"), "correct horse battery");
  await fireEvent.press(screen.getByRole("button", { name: "Sign in" }));
  await screen.findByRole("button", { name: "Sign in" });
  expect(mockRouter.push).toHaveBeenCalledWith("/totp");
});

async function fillInvite() {
  await fireEvent.changeText(screen.getByLabelText("Your name"), "Friend");
  await fireEvent.changeText(screen.getByLabelText("Password"), "correct horse battery");
  await fireEvent.press(screen.getByRole("button", { name: "Create account" }));
}

it("invite screen shows QR and manual secret after accept", async () => {
  const server = serve({
    "POST /api/invitations/accept": () => ({
      status: 201,
      body: { user_id: "u", provisioning_uri: URI, enrolment_token: "enrol" },
    }),
  });
  await render(<InviteScreen />);
  await fillInvite();
  expect(await screen.findByTestId("totp-qr")).toBeTruthy();
  expect(screen.getByText("JBSWY3DPEHPK3PXP")).toBeTruthy();
  expect(server.requests[0].body).toEqual({
    token: "invite-token",
    display_name: "Friend",
    password: "correct horse battery",
    locale: "en",
  });
});

it("invite screen shows translated invitation_used error", async () => {
  serve({
    "POST /api/invitations/accept": () => ({ status: 410, body: { error: { code: "invitation_used" } } }),
  });
  await render(<InviteScreen />);
  await fillInvite();
  expect(await screen.findByText("This invitation has already been used.")).toBeTruthy();
});

it("invite screen confirms the code and sends the user to sign in", async () => {
  const server = serve({
    "POST /api/invitations/accept": () => ({
      status: 201,
      body: { user_id: "u", provisioning_uri: URI, enrolment_token: "enrol" },
    }),
    "POST /api/auth/totp/confirm": () => ({ status: 204 }),
  });
  await render(<InviteScreen />);
  await fillInvite();
  await fireEvent.changeText(await screen.findByLabelText("6-digit code"), "123456");
  await fireEvent.press(screen.getByRole("button", { name: "Confirm" }));
  await screen.findByTestId("totp-qr");
  await new Promise((r) => setTimeout(r, 0));
  expect(server.requests.at(-1)?.body).toEqual({ enrolment_token: "enrol", code: "123456" });
  expect(mockRouter.replace).toHaveBeenCalledWith("/sign-in");
});
