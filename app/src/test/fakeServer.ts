/** Routes fetch calls by "METHOD /path" to canned JSON responses, recording each request body. */
export type Handler = (body: unknown) => { status: number; body?: unknown };

export function fakeServer(routes: Record<string, Handler>) {
  const requests: { key: string; body: unknown; headers: Headers }[] = [];
  const fetch = jest.fn(async (input: Request | string, init?: RequestInit) => {
    const request = typeof input === "string" ? new Request(input, init) : input;
    const key = `${request.method} ${new URL(request.url).pathname}`;
    const text = await request.text();
    const body = text ? JSON.parse(text) : undefined;
    requests.push({ key, body, headers: request.headers });
    const handler = routes[key];
    const result = handler ? handler(body) : { status: 404, body: { error: { code: "not_found" } } };
    return new Response(result.body === undefined ? null : JSON.stringify(result.body), {
      status: result.status,
      headers: { "Content-Type": "application/json" },
    });
  });
  return { fetch, requests };
}

export const ME = {
  id: "8f8f8f8f-0000-4000-8000-000000000001",
  email: "romen@example.com",
  display_name: "Romen",
  locale: "en",
  is_admin: false,
};
