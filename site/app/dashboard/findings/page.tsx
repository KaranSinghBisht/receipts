import Link from "next/link";

import { Card, PageHead } from "@/components/dash";
import { report } from "@/lib/report";

export const metadata = { title: "Findings — Receipts" };

export default function Findings() {
  const groups = new Map<
    string,
    { severity: string; detail: string; runs: { name: string; scenario: string; agent: string }[] }
  >();
  for (const run of report.runs) {
    for (const f of run.findings) {
      const g = groups.get(f.title) ?? { severity: f.severity, detail: f.detail, runs: [] };
      g.runs.push({ name: run.name, scenario: run.scenario, agent: run.agent });
      groups.set(f.title, g);
    }
  }
  const sorted = [...groups.entries()].sort((a, b) => b[1].runs.length - a[1].runs.length);

  return (
    <>
      <PageHead
        title="Findings"
        sub="Every finding raised across the workspace, grouped by what fired. Each one cites the trace lines that prove it — open a run to see them."
      />
      {sorted.length ? (
        <div className="flex flex-col gap-5">
          {sorted.map(([title, g]) => (
            <Card key={title}>
              <div className="flex flex-wrap items-baseline gap-2.5 border-b border-rule-soft px-5 py-4">
                <span
                  className={`rounded-full px-2 py-0.5 font-mono text-[9.5px] font-semibold tracking-[0.08em] uppercase ${
                    g.severity === "high"
                      ? "bg-signal-soft text-signal"
                      : "bg-warn-soft text-warn"
                  }`}
                >
                  {g.severity}
                </span>
                <h2 className="text-[15.5px] font-semibold">{title}</h2>
                <span className="gutter ml-auto tnum">
                  {g.runs.length} run{g.runs.length === 1 ? "" : "s"}
                </span>
              </div>
              <p className="border-b border-rule-soft px-5 py-3 text-[13.5px] leading-relaxed text-ink-2">
                {g.detail}
              </p>
              <div className="flex flex-wrap gap-2 px-5 py-3.5">
                {g.runs.map((r) => (
                  <Link
                    key={r.name}
                    href={`/dashboard/runs/${encodeURIComponent(r.name)}`}
                    className="rounded-full border border-rule bg-ground px-3 py-1 font-mono text-[11px] text-ink-2 transition hover:border-ink-3"
                  >
                    {r.scenario} · {r.agent}
                  </Link>
                ))}
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <p className="px-5 py-5 text-[14px] text-good">Nothing fired across this workspace.</p>
        </Card>
      )}
    </>
  );
}
