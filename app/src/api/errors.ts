/** The API's error code from an openapi-fetch `error` value. */
export function errorCode(error: unknown): string {
  const code = (error as { error?: { code?: unknown } } | undefined)?.error?.code;
  return typeof code === "string" ? code : "unknown";
}
