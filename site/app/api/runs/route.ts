import { randomBytes } from "node:crypto";

import { runPath, workspaceForToken } from "@/lib/auth";
import { listJson, putJson } from "@/lib/store";

export const dynamic = "force-dynamic";

export type StoredRun = {
  id: string;
  name: string;
  verdict: string;
  agent: string;
  claim: string;
  findings: { severity: string; title: string; detail?: string }[];
  filesWritten: number;
  commands: number;
  pushedAt: number;
};

/** `receipts push` sends an audited run here. The trace never leaves the machine. */
export async function POST(request: Request) {
  const workspace = await workspaceForToken(request.headers.get("authorization"));
  if (!workspace) return Response.json({ error: "unauthorized" }, { status: 401 });

  let body: Partial<StoredRun>;
  try {
    body = (await request.json()) as Partial<StoredRun>;
  } catch {
    return Response.json({ error: "invalid_json" }, { status: 400 });
  }
  if (!body.name || !body.verdict) {
    return Response.json({ error: "name and verdict are required" }, { status: 400 });
  }

  const findings = Array.isArray(body.findings) ? body.findings : [];
  const count = (value: unknown) => {
    const parsed = Number(value ?? 0);
    return Number.isFinite(parsed) ? Math.max(0, Math.trunc(parsed)) : 0;
  };
  const run: StoredRun = {
    id: randomBytes(8).toString("hex"),
    name: String(body.name).slice(0, 200),
    verdict: body.verdict === "diverged" ? "diverged" : "clean",
    agent: String(body.agent ?? "unknown").slice(0, 60),
    claim: String(body.claim ?? "").slice(0, 4000),
    findings: findings.slice(0, 20).map((f) => ({
      severity: String(f.severity ?? "low").slice(0, 12),
      title: String(f.title ?? "").slice(0, 300),
      detail: String(f.detail ?? "").slice(0, 2000),
    })),
    filesWritten: count(body.filesWritten),
    commands: count(body.commands),
    pushedAt: Date.now(),
  };

  await putJson(runPath(workspace, run.id), run);
  const origin = new URL(request.url).origin;
  return Response.json({ ok: true, id: run.id, url: `${origin}/w/${workspace}` });
}

export async function GET(request: Request) {
  const workspace = await workspaceForToken(request.headers.get("authorization"));
  if (!workspace) return Response.json({ error: "unauthorized" }, { status: 401 });
  const runs = await listJson<StoredRun>(`ws/${workspace}/runs/`);
  runs.sort((a, b) => b.pushedAt - a.pushedAt);
  return Response.json({ workspace, runs });
}
