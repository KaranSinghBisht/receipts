import { createHash, randomBytes } from "node:crypto";

import { countPrefix, deleteJson, getJson, putJson } from "./store";

/**
 * Device authorisation.
 *
 * A CLI asks for a code, a browser approves it, and the CLI receives a bearer
 * token bound to a workspace. This is the standard device flow shape without an
 * identity provider, so be precise about what it establishes: it authorises a
 * *machine* to write to a workspace. It does not identify a person, and the UI
 * says so rather than implying an account exists.
 *
 * Long-lived tokens are stored only as SHA-256 hashes. The raw device token is
 * held in the pending device record just long enough for the CLI to collect it,
 * then that record is deleted.
 *
 * SEC-02: CLI tokens expire server-side and can be revoked. `receipts logout`
 * used to delete only the local copy, which meant a copied token stayed valid
 * for as long as the record existed. Both halves are needed: expiry bounds a
 * token nobody notices is gone, revocation handles one you know is gone.
 */

/**
 * The ceiling that actually bounds anonymous storage growth (SEC-01).
 *
 * Per-instance rate limiting does not survive serverless fan-out -- measured
 * against production, a fourteen-request burst spread across enough instances
 * that none reached its ceiling. So the real cap is read from shared storage:
 * no more than this many device records may be pending at once. Each expires
 * within CODE_TTL_MS and is deleted when touched after that, so this bounds the
 * live set. Sized far above any honest burst; a normal login creates one.
 */
export const MAX_PENDING_DEVICES = 250;

export const CODE_TTL_MS = 10 * 60 * 1000;
export const SESSION_TTL_MS = 30 * 24 * 60 * 60 * 1000;
export const TOKEN_TTL_MS = 30 * 24 * 60 * 60 * 1000;

export type DeviceRecord = {
  userCode: string;
  createdAt: number;
  approved: boolean;
  workspace?: string;
  token?: string;
};

export type TokenRecord = { workspace: string; createdAt: number; expiresAt: number };
export type BrowserSessionRecord = { workspace: string; createdAt: number };
export type Workspace = { id: string; createdAt: number };

const secret = (bytes = 32) => randomBytes(bytes).toString("base64url");
export const hashToken = (token: string) =>
  createHash("sha256").update(token).digest("hex");

/** Human-typeable, and without the characters people mistype. */
export function makeUserCode(): string {
  const alphabet = "ABCDEFGHJKMNPQRSTUVWXYZ23456789";
  const pick = () =>
    Array.from(randomBytes(4))
      .map((b) => alphabet[b % alphabet.length])
      .join("");
  return `${pick()}-${pick()}`;
}

export const devicePath = (deviceCode: string) => `device/${deviceCode}.json`;
export const codePath = (userCode: string) => `code/${userCode}.json`;
export const tokenPath = (token: string) => `token/${hashToken(token)}.json`;
export const sessionPath = (token: string) => `session/${hashToken(token)}.json`;
export const workspacePath = (id: string) => `ws/${id}/meta.json`;
export const runPath = (workspace: string, runId: string) =>
  `ws/${workspace}/runs/${runId}.json`;

export function expired(record: { createdAt: number }): boolean {
  return Date.now() - record.createdAt > CODE_TTL_MS;
}

async function discardDevice(deviceCode: string, record: DeviceRecord): Promise<void> {
  const paths = [devicePath(deviceCode), codePath(record.userCode)];
  if (record.token) paths.push(tokenPath(record.token));
  await deleteJson(paths);
}

/** True when too many device records are already pending. */
export async function pendingDeviceCeilingReached(): Promise<boolean> {
  return (await countPrefix("device/", MAX_PENDING_DEVICES + 1)) > MAX_PENDING_DEVICES;
}

export async function startDevice() {
  const deviceCode = secret();
  const userCode = makeUserCode();
  const record: DeviceRecord = {
    userCode,
    createdAt: Date.now(),
    approved: false,
  };
  await putJson(devicePath(deviceCode), record);
  await putJson(codePath(userCode), { deviceCode });
  return { deviceCode, userCode };
}

/** Approve a pending code, minting a workspace and the token the CLI collects. */
export async function approveUserCode(userCode: string) {
  const pointer = await getJson<{ deviceCode: string }>(codePath(userCode));
  if (!pointer) return { ok: false as const, reason: "unknown" as const };

  const record = await getJson<DeviceRecord>(devicePath(pointer.deviceCode));
  if (!record) return { ok: false as const, reason: "unknown" as const };
  if (expired(record)) {
    await discardDevice(pointer.deviceCode, record);
    return { ok: false as const, reason: "expired" as const };
  }
  let workspace = record.workspace;
  if (!record.approved) {
    workspace = secret(9);
    const token = secret();
    await putJson(workspacePath(workspace), {
      id: workspace,
      createdAt: Date.now(),
    } satisfies Workspace);
    await putJson(tokenPath(token), {
      workspace,
      createdAt: Date.now(),
      expiresAt: Date.now() + TOKEN_TTL_MS,
    } satisfies TokenRecord);
    await putJson(devicePath(pointer.deviceCode), {
      ...record,
      approved: true,
      workspace,
      token,
    } satisfies DeviceRecord);
  }

  const sessionToken = secret();
  await putJson(sessionPath(sessionToken), {
    workspace: workspace!,
    createdAt: Date.now(),
  } satisfies BrowserSessionRecord);
  return { ok: true as const, workspace: workspace!, sessionToken };
}

function bearer(authorization: string | null): string | null {
  return authorization?.match(/^Bearer\s+(\S+)\s*$/i)?.[1] ?? null;
}

/** Resolve a bearer token to its workspace, or null.
 *
 *  An expired record is deleted on the way past rather than left to linger:
 *  the check would reject it anyway, and leaving it invites the assumption
 *  that presence means validity. Records minted before expiry existed are
 *  treated as expiring one TTL after they were created. */
export async function workspaceForToken(
  authorization: string | null,
): Promise<string | null> {
  const token = bearer(authorization);
  if (!token) return null;
  const record = await getJson<TokenRecord>(tokenPath(token));
  if (!record) return null;

  const expiresAt = record.expiresAt ?? record.createdAt + TOKEN_TTL_MS;
  if (Date.now() > expiresAt) {
    await deleteJson(tokenPath(token));
    return null;
  }
  return record.workspace;
}

/** Revoke a CLI token server-side. Returns false when it was already gone,
 *  so `receipts logout` can stay quiet either way. */
export async function revokeToken(authorization: string | null): Promise<boolean> {
  const token = bearer(authorization);
  if (!token) return false;
  const record = await getJson<TokenRecord>(tokenPath(token));
  if (!record) return false;
  await deleteJson(tokenPath(token));
  return true;
}

/** Resolve the opaque browser-session cookie to its workspace. */
export async function workspaceForSession(token: string | undefined): Promise<string | null> {
  if (!token) return null;
  const record = await getJson<BrowserSessionRecord>(sessionPath(token));
  if (!record || Date.now() - record.createdAt > SESSION_TTL_MS) return null;
  return record.workspace;
}

/** Return a device token once, then remove the temporary plaintext record. */
export async function collectDeviceToken(deviceCode: string) {
  const path = devicePath(deviceCode);
  const record = await getJson<DeviceRecord>(path);
  if (!record) return { ok: false as const, reason: "unknown" as const };
  if (expired(record)) {
    await discardDevice(deviceCode, record);
    return { ok: false as const, reason: "expired" as const };
  }
  if (!record.approved || !record.token || !record.workspace) {
    return { ok: false as const, reason: "pending" as const };
  }
  await deleteJson([path, codePath(record.userCode)]);
  return {
    ok: true as const,
    token: record.token,
    workspace: record.workspace,
  };
}
