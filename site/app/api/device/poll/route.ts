import { devicePath, expired, type DeviceRecord } from "@/lib/auth";
import { getJson } from "@/lib/store";

export const dynamic = "force-dynamic";

/** Mirrors the device-flow contract: pending until approved, then the token once. */
export async function POST(request: Request) {
  const { device_code: deviceCode } = (await request.json()) as {
    device_code?: string;
  };
  if (!deviceCode) {
    return Response.json({ error: "invalid_request" }, { status: 400 });
  }

  const record = await getJson<DeviceRecord>(devicePath(deviceCode));
  if (!record) return Response.json({ error: "invalid_grant" }, { status: 400 });
  if (expired(record)) {
    return Response.json({ error: "expired_token" }, { status: 400 });
  }
  if (!record.approved) {
    return Response.json({ error: "authorization_pending" }, { status: 428 });
  }

  return Response.json({
    access_token: record.token,
    workspace: record.workspace,
    token_type: "Bearer",
  });
}
