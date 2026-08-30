import Link from "next/link";

import { Card, PageHead, RunRow, StatCard } from "@/components/dash";
import { diverged, report } from "@/lib/report";

export const metadata = { title: "Overview — Receipts" };

export default function Overview() {
  const bad = report.runs.filter(diverged);
  const attention = bad.slice(0, 6);
  const t = report.totals;

  return (
    <>
      <PageHead
        title={
          t.diverged
            ? `${t.diverged} of ${report.runs.length} runs need a look`
            : "Every summary is backed by its trace"
        }
        sub={`Nightly study across ${report.agents.join(" and ")} · generated ${report.generated}`}
      />

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
        <StatCard n={report.runs.length} k="runs" />
        <StatCard n={report.agents.length} k="agents" />
        <StatCard n={t.diverged} k="diverged" tone="signal" />
        <StatCard n={`${t.false_alarms ?? 0}/18`} k="false alarms" tone="good" />
        <StatCard n={t.trace_lines.toLocaleString()} k="lines by hand" />
        <StatCard n={t.cited_lines} k="lines cited" tone="good" />
      </div>

      <div className="mt-5 grid gap-5 lg:grid-cols-[1.6fr_1fr]">
        <Card title="Needs attention">
          {attention.length ? (
            attention.map((run) => <RunRow key={run.name} run={run} />)
          ) : (
            <p className="px-4 py-6 text-[14px] text-ink-2">Nothing diverged.</p>
          )}
          <Link
            href="/dashboard/runs"
            className="block px-4 py-3 text-[13px] font-medium text-accent"
          >
            All {report.runs.length} runs &rarr;
          </Link>
        </Card>

        <div className="flex flex-col gap-5">
          <Card title="Verdicts">
            <div className="px-4 py-4">
              <div className="flex h-[14px] overflow-hidden rounded-full">
                <span
                  className="bg-signal"
                  style={{ width: `${(100 * t.diverged) / report.runs.length}%` }}
                />
                <span className="flex-1 bg-good/55" />
              </div>
              <div className="mt-3 flex justify-between font-mono text-[11px] text-ink-2">
                <span>
                  <span className="font-semibold text-signal">{t.diverged}</span> diverged
                </span>
                <span>
                  <span className="font-semibold text-good">{t.clean}</span> clean
                </span>
              </div>
            </div>
          </Card>

          <Card title="Reading, saved">
            <div className="px-4 py-4">
              <p className="text-[14px] leading-relaxed text-ink-2">
                Auditing this batch by hand means reading{" "}
                <span className="font-mono font-semibold text-ink tnum">
                  {t.trace_lines.toLocaleString()}
                </span>{" "}
                trace lines. Receipts points at{" "}
                <span className="font-mono font-semibold text-good tnum">
                  {t.cited_lines}
                </span>
                .
              </p>
            </div>
          </Card>

          <Card title="Push your own runs">
            <div className="px-4 py-4">
              <p className="rounded-lg bg-terminal px-3 py-2.5 font-mono text-[11.5px] text-[#D4DAE3]">
                <span className="text-white/35">$ </span>receipts login
                <br />
                <span className="text-white/35">$ </span>receipts push trace.ndjson
              </p>
            </div>
          </Card>
        </div>
      </div>
    </>
  );
}
