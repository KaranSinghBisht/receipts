import { cookies } from "next/headers";

import { approveUserCode } from "@/lib/auth";

export const dynamic = "force-dynamic";

/** Called by the browser once someone confirms the code their CLI printed. */
export async function POST(request: Request) {
  const { user_code: userCode } = (await request.json()) as { user_code?: string };
  if (!userCode) {
    return Response.json({ error: "invalid_request" }, { status: 400 });
  }

  const result = await approveUserCode(userCode.trim().toUpperCase());
  if (!result.ok) {
    const status = result.reason === "expired" ? 410 : 404;
    return Response.json({ error: result.reason }, { status });
  }
  // The browser that approved the device gets a session for that workspace, so
  // the dashboard is gated by a cookie rather than by the URL being hard to guess.
  const jar = await cookies();
  jar.set("receipts_ws", result.workspace, {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: 60 * 60 * 24 * 30,
  });
  return Response.json({ ok: true, workspace: result.workspace });
}
