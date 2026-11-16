import { createApiClient, type AuthHandlers } from "../client";

type Call = { url: string; auth: string | null; client: string | null };

function fakeFetch(statuses: number[]) {
  const calls: Call[] = [];
  const fetch = jest.fn(async (input: Request) => {
    calls.push({
      url: input.url,
      auth: input.headers.get("Authorization"),
      client: input.headers.get("X-Ascua-Client"),
    });
    const status = statuses[Math.min(calls.length - 1, statuses.length - 1)];
    return new Response(JSON.stringify({ ok: status < 400 }), {
      status,
      headers: { "Content-Type": "application/json" },
    });
  });
  return { fetch, calls };
}

function handlers(tokens: { access: string | null; refreshed: string | null }): AuthHandlers {
  return {
    getAccessToken: () => tokens.access,
    refresh: jest.fn(async () => {
      tokens.access = tokens.refreshed;
      return tokens.refreshed;
    }),
  };
}

describe("api client", () => {
  it("sends the access token and identifies web clients", async () => {
    const { fetch, calls } = fakeFetch([200]);
    const api = createApiClient({
      baseUrl: "http://api.test",
      fetch,
      platform: "web",
      auth: handlers({ access: "A1", refreshed: null }),
    });
    await api.GET("/api/me");
    expect(calls[0]).toEqual({ url: "http://api.test/api/me", auth: "Bearer A1", client: "web" });
  });

  it("does not send the web header from native", async () => {
    const { fetch, calls } = fakeFetch([200]);
    const api = createApiClient({
      baseUrl: "http://api.test",
      fetch,
      platform: "native",
      auth: handlers({ access: null, refreshed: null }),
    });
    await api.GET("/api/me");
    expect(calls[0].client).toBeNull();
    expect(calls[0].auth).toBeNull();
  });

  it("retries once after refreshing on 401", async () => {
    const { fetch, calls } = fakeFetch([401, 200]);
    const auth = handlers({ access: "old", refreshed: "new" });
    const api = createApiClient({ baseUrl: "http://api.test", fetch, platform: "native", auth });
    const { response } = await api.GET("/api/me");
    expect(response.status).toBe(200);
    expect(auth.refresh).toHaveBeenCalledTimes(1);
    expect(calls.map((c) => c.auth)).toEqual(["Bearer old", "Bearer new"]);
  });

  it("does not loop when refresh also fails", async () => {
    const { fetch } = fakeFetch([401]);
    const auth = handlers({ access: "old", refreshed: null });
    const api = createApiClient({ baseUrl: "http://api.test", fetch, platform: "native", auth });
    const { response } = await api.GET("/api/me");
    expect(response.status).toBe(401);
    expect(auth.refresh).toHaveBeenCalledTimes(1);
    expect(fetch).toHaveBeenCalledTimes(1);
  });

  it("does not refresh again when the retried request is still 401", async () => {
    const { fetch } = fakeFetch([401, 401]);
    const auth = handlers({ access: "old", refreshed: "new" });
    const api = createApiClient({ baseUrl: "http://api.test", fetch, platform: "native", auth });
    const { response } = await api.GET("/api/me");
    expect(response.status).toBe(401);
    expect(auth.refresh).toHaveBeenCalledTimes(1);
    expect(fetch).toHaveBeenCalledTimes(2);
  });

  it("never refreshes for the auth endpoints themselves", async () => {
    const { fetch } = fakeFetch([401]);
    const auth = handlers({ access: null, refreshed: "new" });
    const api = createApiClient({ baseUrl: "http://api.test", fetch, platform: "native", auth });
    await api.POST("/api/auth/sign-in", { body: { email: "a@b.c", password: "x" } });
    expect(auth.refresh).not.toHaveBeenCalled();
  });
});
