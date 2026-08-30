import { cookies } from "next/headers";

import type { StoredRun } from "@/app/api/runs/route";
import { listJson } from "@/lib/store";

export const dynamic = "force-dynamic";

function ago(ts: number): string {
  const minutes = Math.max(0, Math.round((Date.now() - ts) / 60000));
  if (minutes < 1) return "just now";
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.round(minutes / 60);
  return hours < 24 ? `${hours}h ago` : `${Math.round(hours / 24)}d ago`;
}

function PushHint() {
  return (
    <div className="overflow-hidden bg-terminal" style={{ borderRadius: 3 }}>
      <div className="border-b border-white/8 px-4 py-2.5">
        <span className="font-mono text-[10.5px] tracking-[0.12em] text-white/35 uppercase">
          push a run from the authorised machine
        </span>
      </div>
      <pre className="px-5 py-4 font-mono text-[12.5px] leading-[1.75] text-[#D4DAE3]">
        <span className="text-white/35">$ </span>receipts push trace.ndjson
      </pre>
    </div>
  );
}

function RunRow({ run }: { run: StoredRun }) {
  const diverged = run.verdict === "diverged";
  return (
    <li
      className={`border-l-2 py-5 pl-5 ${diverged ? "border-signal" : "border-good/40"}`}
    >
      <div className="flex flex-wrap items-baseline gap-x-4 gap-y-1">
        <span className="font-mono text-[14px] font-semibold">{run.name}</span>
        <span
          className={`inline-flex items-center gap-2 font-mono text-[11px] tracking-[0.06em] ${
            diverged ? "text-signal" : "text-good"
          }`}
        >
          <span
            aria-hidden
            className={`h-[7px] w-[7px] ${diverged ? "bg-signal" : "bg-good"}`}
            style={{ borderRadius: 1 }}
          />
          {run.verdict}
        </span>
        <span className="gutter ml-auto">
          {run.agent} &middot; {run.filesWritten} written &middot; {run.commands} commands
          &middot; {ago(run.pushedAt)}
        </span>
      </div>
      {run.claim ? (
        <p className="mt-2.5 max-w-[80ch] font-quote text-[15px] leading-relaxed text-ink-2 italic">
          &ldquo;{run.claim.slice(0, 220)}
          {run.claim.length > 220 ? "…" : ""}&rdquo;
        </p>
      ) : null}
      {run.findings.length > 0 ? (
        <ul className="mt-3 space-y-2">
          {run.findings.map((f, i) => (
            <li key={i} className="flex items-baseline gap-2.5 text-[14px] text-ink-2">
              <span
                className={`px-1.5 py-0.5 font-mono text-[9px] font-semibold tracking-[0.1em] uppercase ${
                  f.severity === "high"
                    ? "bg-signal-soft text-signal"
                    : "bg-warn-soft text-warn"
                }`}
              >
                {f.severity}
              </span>
              <span>{f.title}</span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="mt-2.5 text-[13.5px] text-ink-3">Summary matches the trace.</p>
      )}
    </li>
  );
}

export default async function WorkspacePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const jar = await cookies();

  if (jar.get("receipts_ws")?.value !== id) {
    return (
      <main className="mx-auto max-w-[560px] px-6 py-24">
        <p className="gutter">403</p>
        <h1 className="display mt-3 text-[1.8rem]">Not your workspace</h1>
        <p className="mt-4 text-[15px] leading-relaxed text-ink-2">
          A workspace is only visible to the browser that authorised it. Run{" "}
          <code className="font-mono text-ink">receipts login</code> on the machine you
          want to connect, and approve the code here.
        </p>
      </main>
    );
  }

  const runs = await listJson<StoredRun>(`ws/${id}/runs/`);
  runs.sort((a, b) => b.pushedAt - a.pushedAt);
  const diverged = runs.filter((r) => r.verdict === "diverged").length;
  const findings = runs.reduce((n, r) => n + r.findings.length, 0);

  return (
    <main className="mx-auto max-w-[1000px] px-6 py-16 md:px-10">
      <div className="flex flex-wrap items-baseline gap-4">
        <div>
          <p className="gutter">workspace</p>
          <h1 className="display mt-3 text-[2rem]">
            {runs.length === 0
              ? "Waiting for the first run"
              : diverged === 0
                ? "Every summary is backed by its trace"
                : `${diverged} of ${runs.length} runs need a look`}
          </h1>
        </div>
        <p className="gutter ml-auto">/w/{id.slice(0, 6)}&hellip;</p>
      </div>

      <div className="mt-8 flex flex-wrap gap-x-12 gap-y-5 border-y border-rule py-5">
        {(
          [
            [runs.length, "runs pushed", ""],
            [diverged, "diverged", diverged ? "text-signal" : ""],
            [runs.length - diverged, "clean", "text-good"],
            [findings, "findings", ""],
          ] as const
        ).map(([n, k, tone]) => (
          <div key={k}>
            <p className={`font-mono text-[1.6rem] leading-none font-semibold tnum ${tone}`}>
              {n}
            </p>
            <p className="gutter mt-2">{k}</p>
          </div>
        ))}
      </div>

      {runs.length === 0 ? (
        <div className="mt-8 max-w-[560px]">
          <PushHint />
          <p className="mt-4 text-[13.5px] leading-relaxed text-ink-3">
            Only the audit result is uploaded. The trace itself stays on the machine that
            produced it.
          </p>
        </div>
      ) : (
        <ul className="mt-6 space-y-1">
          {runs.map((run) => (
            <RunRow key={run.id} run={run} />
          ))}
        </ul>
      )}
    </main>
  );
}
