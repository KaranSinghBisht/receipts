import Link from "next/link";
import { notFound } from "next/navigation";

import { Card, PageHead, Strip } from "@/components/dash";
import { Verdict } from "@/components/ui";
import { report } from "@/lib/report";

export function generateStaticParams() {
  return report.runs.map((run) => ({ name: run.name }));
}

export default async function RunDetail({
  params,
}: {
  params: Promise<{ name: string }>;
}) {
  const { name } = await params;
  const run = report.runs.find((r) => r.name === decodeURIComponent(name));
  if (!run) notFound();

  const failed = run.timeline.filter((t) => t.outcome === "error").length;

  return (
    <>
      <Link href="/dashboard/runs" className="gutter">
        &larr; all runs
      </Link>
      <div className="mt-2">
        <PageHead
          title={run.scenario}
          sub={`${run.agent}${run.label ? ` · ${run.label}` : ""} · ${run.files_written} file(s) written · ${run.commands} command(s)${failed ? ` · ${failed} failed` : ""}`}
          right={<Verdict value={run.verdict} />}
        />
      </div>

      <div className="grid gap-5 lg:grid-cols-[1.5fr_1fr]">
        <div className="flex min-w-0 flex-col gap-5">
          <Card title="What the agent claimed">
            <p className="px-5 py-4 font-quote text-[15.5px] leading-relaxed text-ink-2 italic">
              &ldquo;{run.claim || "—"}&rdquo;
            </p>
          </Card>

          <Card title={run.findings.length ? "Findings" : "Findings — none"}>
            {run.findings.length ? (
              run.findings.map((f, i) => (
                <article key={i} className="border-b border-rule-soft px-5 py-4 last:border-0">
                  <div className="flex flex-wrap items-baseline gap-2.5">
                    <span
                      className={`rounded-full px-2 py-0.5 font-mono text-[9.5px] font-semibold tracking-[0.08em] uppercase ${
                        f.severity === "high"
                          ? "bg-signal-soft text-signal"
                          : "bg-warn-soft text-warn"
                      }`}
                    >
                      {f.severity}
                    </span>
                    <h3 className="text-[15px] font-semibold">{f.title}</h3>
                  </div>
                  <p className="mt-2 text-[13.5px] leading-relaxed text-ink-2">{f.detail}</p>
                  <ul className="mt-3 space-y-2">
                    {f.evidence.map((e, j) => (
                      <li key={j} className="rounded-lg bg-ground px-3 py-2.5">
                        <p className="font-mono text-[10.5px] text-ink-3">
                          <span className="font-semibold text-accent">
                            {e.seq >= 0 ? `line ${e.seq}` : "summary"}
                          </span>{" "}
                          &middot; {e.label}
                        </p>
                        {e.excerpt ? (
                          <p className="mt-1 overflow-x-auto font-mono text-[11.5px] whitespace-pre-wrap text-ink-2">
                            {e.excerpt}
                          </p>
                        ) : null}
                      </li>
                    ))}
                  </ul>
                </article>
              ))
            ) : (
              <p className="px-5 py-4 text-[14px] text-good">
                No divergence between the summary and the trace.
              </p>
            )}
          </Card>
        </div>

        <div className="flex min-w-0 flex-col gap-5">
          <Card title="Run shape">
            <div className="px-5 py-4">
              <Strip cells={run.strip} />
              <dl className="mt-4 space-y-1.5 font-mono text-[12px] text-ink-2">
                <div className="flex justify-between">
                  <dt className="text-ink-3">trace lines</dt>
                  <dd className="tnum">{run.traceLines}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-ink-3">lines cited</dt>
                  <dd className="tnum">{run.citedLines}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-ink-3">duration</dt>
                  <dd className="tnum">
                    {run.duration_ms ? `${(run.duration_ms / 1000).toFixed(1)}s` : "—"}
                  </dd>
                </div>
                {run.cost ? (
                  <div className="flex justify-between">
                    <dt className="text-ink-3">cost</dt>
                    <dd className="tnum">{run.cost.toFixed(4)}</dd>
                  </div>
                ) : null}
              </dl>
            </div>
          </Card>

          <Card title="Execution trace">
            <ol className="max-h-[520px] overflow-y-auto">
              {run.timeline.map((row) => (
                <li
                  key={row.seq}
                  className={`grid grid-cols-[44px_1fr_auto] items-baseline gap-2 border-b border-rule-soft px-4 py-2 font-mono text-[11.5px] last:border-0 ${
                    row.flagged ? "bg-signal-soft/60" : ""
                  }`}
                >
                  <span className="text-ink-3 tnum">{row.seq}</span>
                  <span className="min-w-0 truncate">
                    <span className="text-ink-3">{row.kind} </span>
                    <span className="text-ink-2">{row.detail}</span>
                    {row.test ? <span className="ml-1.5 text-warn">test</span> : null}
                    {row.recovered ? (
                      <span className="ml-1.5 text-ink-3">unreported</span>
                    ) : null}
                  </span>
                  <span
                    className={
                      row.outcome === "error"
                        ? "text-signal"
                        : row.outcome === "ok"
                          ? "text-good"
                          : "text-ink-3"
                    }
                  >
                    {row.outcome}
                  </span>
                </li>
              ))}
            </ol>
          </Card>
        </div>
      </div>
    </>
  );
}
