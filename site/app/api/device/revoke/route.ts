import { revokeToken } from "@/lib/auth";

import { LIMITS, clientKey, rateLimit, tooMany } from "@/lib/ratelimit";

export const dynamic = "force-dynamic";

/**
 * `receipts logout` calls this so the token stops working everywhere, not just
 * on the machine that ran the command. Answers 200 either way: whether the
 * token was already gone is not something an unauthenticated caller should be
 * able to probe for.
 */
export async function POST(request: Request) {
  const gate = rateLimit(`revoke:${clientKey(request)}`, LIMITS.deviceApprove.limit, LIMITS.deviceApprove.windowMs);
  if (!gate.ok) return tooMany(gate);

  await revokeToken(request.headers.get("authorization"));
  return Response.json({ ok: true });
}
