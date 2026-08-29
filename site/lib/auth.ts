import { createHash, randomBytes } from "node:crypto";

import { getJson, putJson } from "./store";

/**
 * Device authorisation.
 *
 * A CLI asks for a code, a browser approves it, and the CLI receives a bearer
 * token bound to a workspace. This is the standard device flow shape without an
 * identity provider, so be precise about what it establishes: it authorises a
 * *machine* to write to a workspace. It does not identify a person, and the UI
 * says so rather than implying an account exists.
 *
 * Tokens are never stored. Only their SHA-256 is kept, so the records here are
 * useless to anyone who reads them.
 */

export const CODE_TTL_MS = 10 * 60 * 1000;

export type DeviceRecord = {
  userCode: string;
  createdAt: number;
  approved: boolean;
  workspace?: string;
  token?: string;
};

export type TokenRecord = { workspace: string; createdAt: number };
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
export const workspacePath = (id: string) => `ws/${id}/meta.json`;
export const runPath = (workspace: string, runId: string) =>
  `ws/${workspace}/runs/${runId}.json`;

export function expired(record: { createdAt: number }): boolean {
  return Date.now() - record.createdAt > CODE_TTL_MS;
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
  if (expired(record)) return { ok: false as const, reason: "expired" as const };
  if (record.approved) {
    return { ok: true as const, workspace: record.workspace! };
  }

  const workspace = secret(9);
  const token = secret();
  await putJson(workspacePath(workspace), {
    id: workspace,
    createdAt: Date.now(),
  } satisfies Workspace);
  await putJson(tokenPath(token), {
    workspace,
    createdAt: Date.now(),
  } satisfies TokenRecord);
  await putJson(devicePath(pointer.deviceCode), {
    ...record,
    approved: true,
    workspace,
    token,
  } satisfies DeviceRecord);

  return { ok: true as const, workspace };
}

/** Resolve a bearer token to its workspace, or null. */
export async function workspaceForToken(
  authorization: string | null,
): Promise<string | null> {
  const token = authorization?.replace(/^Bearer\s+/i, "").trim();
  if (!token) return null;
  const record = await getJson<TokenRecord>(tokenPath(token));
  return record?.workspace ?? null;
}
