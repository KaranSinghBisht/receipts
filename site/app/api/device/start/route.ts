import { startDevice } from "@/lib/auth";

export const dynamic = "force-dynamic";

/** The CLI asks for a code. It shows the user code and polls with the device code. */
export async function POST(request: Request) {
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
