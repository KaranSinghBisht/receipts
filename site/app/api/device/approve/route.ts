import { cookies } from "next/headers";

import { approveUserCode } from "@/lib/auth";

export const dynamic = "force-dynamic";

const USER_CODE = /^[A-HJ-NP-Z2-9]{4}-[A-HJ-NP-Z2-9]{4}$/;

/** Called by the browser once someone confirms the code their CLI printed. */
export async function POST(request: Request) {
  let userCode: unknown;
  try {
    ({ user_code: userCode } = (await request.json()) as { user_code?: unknown });
  } catch {
    return Response.json({ error: "invalid_json" }, { status: 400 });
  }
  const normalized = typeof userCode === "string" ? userCode.trim().toUpperCase() : "";
  if (!USER_CODE.test(normalized)) {
    return Response.json({ error: "invalid_request" }, { status: 400 });
  }

  const result = await approveUserCode(normalized);
  if (!result.ok) {
    const status = result.reason === "expired" ? 410 : 404;
    return Response.json({ error: result.reason }, { status });
  }
  // The browser that approved the device gets a session for that workspace, so
  // the dashboard is gated by a cookie rather than by the URL being hard to guess.
  const jar = await cookies();
  jar.set("receipts_session", result.sessionToken, {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: 60 * 60 * 24 * 30,
  });
  return Response.json({ ok: true, workspace: result.workspace });
}
