import { cookies } from "next/headers";

import type { StoredRun } from "@/app/api/runs/route";
import { listJson } from "@/lib/store";

export const dynamic = "force-dynamic";

function Empty() {
  return (
    <div className="border border-rule bg-panel p-8">
      <p className="text-[15px] text-ink-2">
        No runs yet. Push one from the machine you just authorised:
      </p>
      <p className="mt-4 bg-terminal px-4 py-3 font-mono text-[12.5px] text-[#D4DAE3]">
        <span className="text-white/35">$ </span>
        receipts push trace.ndjson
      </p>
    </div>
  );
}

function RunRow({ run }: { run: StoredRun }) {
  const diverged = run.verdict === "diverged";
  return (
    <li className="border-b border-rule-soft py-5">
      <div className="flex flex-wrap items-baseline gap-x-4 gap-y-1">
        <span className="font-mono text-[14px] font-semibold">{run.name}</span>
        <span
          className={`font-mono text-[11px] tracking-[0.08em] ${
            diverged ? "text-signal" : "text-good"
          }`}
        >
          {run.verdict}
        </span>
        <span className="gutter ml-auto">
          {run.agent} · {run.filesWritten} written · {run.commands} commands
        </span>
      </div>
      {run.claim ? (
        <p className="mt-2 max-w-[80ch] font-quote text-[15px] leading-relaxed text-ink-2">
          &ldquo;{run.claim.slice(0, 240)}
          {run.claim.length > 240 ? "…" : ""}&rdquo;
        </p>
      ) : null}
      {run.findings.length > 0 ? (
        <ul className="mt-3 space-y-1.5">
          {run.findings.map((f, i) => (
            <li key={i} className="flex gap-2.5 text-[14px] text-ink-2">
              <span
                className={`mt-[3px] font-mono text-[9.5px] tracking-[0.1em] uppercase ${
                  f.severity === "high" ? "text-signal" : "text-warn"
                }`}
              >
                {f.severity}
              </span>
              <span>{f.title}</span>
            </li>
          ))}
        </ul>
      ) : null}
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

  return (
    <main className="mx-auto max-w-[1000px] px-6 py-16 md:px-10">
      <p className="gutter">workspace</p>
      <h1 className="display mt-3 text-[2rem]">
        {runs.length === 0
          ? "Waiting for the first run"
          : `${diverged} of ${runs.length} runs need a look`}
      </h1>

      <div className="mt-8 flex flex-wrap gap-x-12 gap-y-5 border-y border-rule py-5">
        {[
          [runs.length, "runs pushed"],
          [diverged, "diverged"],
          [runs.length - diverged, "clean"],
        ].map(([n, k]) => (
          <div key={k as string}>
            <p className="font-mono text-[1.6rem] leading-none font-semibold tnum">{n}</p>
            <p className="gutter mt-2">{k}</p>
          </div>
        ))}
      </div>

      {runs.length === 0 ? (
        <div className="mt-8">
          <Empty />
        </div>
      ) : (
        <ul className="mt-4">
          {runs.map((run) => (
            <RunRow key={run.id} run={run} />
          ))}
        </ul>
      )}
    </main>
  );
}
