import { pendingDeviceCeilingReached, startDevice } from "@/lib/auth";

import { LIMITS, clientKey, rateLimit, tooMany } from "@/lib/ratelimit";

export const dynamic = "force-dynamic";

/** The CLI asks for a code. It shows the user code and polls with the device code. */
export async function POST(request: Request) {
  const gate = rateLimit(`deviceStart:${clientKey(request)}`, LIMITS.deviceStart.limit, LIMITS.deviceStart.windowMs);
  if (!gate.ok) return tooMany(gate);

  // The cross-instance cap. Refusing costs one list call; not refusing lets an
  // anonymous caller grow storage without bound.
  if (await pendingDeviceCeilingReached()) {
    return Response.json(
      { error: "slow_down" },
      { status: 429, headers: { "retry-after": "60" } },
    );
  }

  const { deviceCode, userCode } = await startDevice();
  const origin = new URL(request.url).origin;
  return Response.json({
    device_code: deviceCode,
    user_code: userCode,
    verification_uri: `${origin}/activate`,
    verification_uri_complete: `${origin}/activate?code=${userCode}`,
    expires_in: 600,
    interval: 2,
  });
}
