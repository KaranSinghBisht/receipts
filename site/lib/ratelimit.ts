/**
 * Fixed-window rate limiting for the anonymous endpoints.
 *
 * SEC-01: `/api/device/start` is unauthenticated by design — a device flow has
 * nobody to authenticate yet — so anyone could loop it and force Blob writes.
 *
 * Be precise about what this buys, because overstating it would be the exact
 * failure this project audits for: the counters live in the instance's memory,
 * so the limit is **per serverless instance**, not global. It removes the cheap
 * single-connection flood, which is the realistic abuse here. It is not a
 * defence against a distributed one; that needs the platform's firewall, and
 * the remaining exposure is bounded by the ten-minute expiry plus the deletion
 * of expired records.
 */

type Bucket = { count: number; resetAt: number };

const buckets = new Map<string, Bucket>();

/** An unbounded map is its own denial of service; keep it swept. */
const MAX_TRACKED = 5_000;

function sweep(now: number): void {
  for (const [key, bucket] of buckets) {
    if (bucket.resetAt <= now) buckets.delete(key);
  }
  if (buckets.size > MAX_TRACKED) buckets.clear();
}

export type Decision = { ok: boolean; retryAfter: number };

export function rateLimit(key: string, limit: number, windowMs: number): Decision {
  const now = Date.now();
  if (buckets.size > 64) sweep(now);

  const bucket = buckets.get(key);
  if (!bucket || bucket.resetAt <= now) {
    buckets.set(key, { count: 1, resetAt: now + windowMs });
    return { ok: true, retryAfter: 0 };
  }

  bucket.count += 1;
  if (bucket.count > limit) {
    return { ok: false, retryAfter: Math.ceil((bucket.resetAt - now) / 1000) };
  }
  return { ok: true, retryAfter: 0 };
}

/**
 * The caller's address. Only the first hop of `x-forwarded-for` is trusted,
 * and only because Vercel rewrites that header at the edge; behind any other
 * proxy this would be client-controlled and worthless.
 */
export function clientKey(request: Request): string {
  const forwarded = request.headers.get("x-forwarded-for");
  const first = forwarded?.split(",")[0]?.trim();
  return first || request.headers.get("x-real-ip") || "unknown";
}

export function tooMany(decision: Decision): Response {
  return Response.json(
    { error: "slow_down" },
    {
      status: 429,
      headers: { "retry-after": String(Math.max(1, decision.retryAfter)) },
    },
  );
}

/** One place to change the numbers, and to see them next to each other. */
export const LIMITS = {
  deviceStart: { limit: 10, windowMs: 60_000 },
  deviceApprove: { limit: 20, windowMs: 60_000 },
  devicePoll: { limit: 120, windowMs: 60_000 },
  runsWrite: { limit: 60, windowMs: 60_000 },
} as const;
