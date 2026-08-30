import { collectDeviceToken } from "@/lib/auth";

import { LIMITS, clientKey, rateLimit, tooMany } from "@/lib/ratelimit";

export const dynamic = "force-dynamic";

const DEVICE_CODE = /^[A-Za-z0-9_-]{43}$/;

/** Mirrors the device-flow contract: pending until approved, then the token once. */
export async function POST(request: Request) {
  const gate = rateLimit(`devicePoll:${clientKey(request)}`, LIMITS.devicePoll.limit, LIMITS.devicePoll.windowMs);
  if (!gate.ok) return tooMany(gate);

  let deviceCode: unknown;
  try {
    ({ device_code: deviceCode } = (await request.json()) as { device_code?: unknown });
  } catch {
    return Response.json({ error: "invalid_json" }, { status: 400 });
  }
  if (typeof deviceCode !== "string" || !DEVICE_CODE.test(deviceCode)) {
    return Response.json({ error: "invalid_request" }, { status: 400 });
  }

  const result = await collectDeviceToken(deviceCode);
  if (!result.ok && result.reason === "unknown") {
    return Response.json({ error: "invalid_grant" }, { status: 400 });
  }
  if (!result.ok && result.reason === "expired") {
    return Response.json({ error: "expired_token" }, { status: 400 });
  }
  if (!result.ok) {
    return Response.json({ error: "authorization_pending" }, { status: 428 });
  }

  return Response.json({
    access_token: result.token,
    workspace: result.workspace,
    token_type: "Bearer",
  }, { headers: { "Cache-Control": "no-store", Pragma: "no-cache" } });
}
