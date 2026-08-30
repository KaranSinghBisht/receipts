import Link from "next/link";

import { Card, PageHead } from "@/components/dash";
import { diverged, report, runsByScenario, type Run } from "@/lib/report";

export const metadata = { title: "Study matrix — Receipts" };

function Cell({ runs }: { runs: Run[] }) {
  if (!runs.length) return <span className="text-ink-3">&mdash;</span>;
  const bad = runs.filter(diverged);
  const target = bad[0] ?? runs[0];
  return (
    <Link
      href={`/dashboard/runs/${encodeURIComponent(target.name)}`}
      className={`inline-flex items-center gap-2 rounded-full px-3 py-1.5 font-mono text-[11.5px] transition hover:brightness-95 ${
        bad.length ? "bg-signal-soft text-signal" : "bg-good-soft text-good"
      }`}
    >
      <span
        aria-hidden
        className={`h-[7px] w-[7px] rounded-full ${bad.length ? "bg-signal" : "bg-good"}`}
      />
      {bad.length ? `diverged ${bad.length}/${runs.length}` : `clean ${runs.length}/${runs.length}`}
    </Link>
  );
}

export default function Study() {
  const byScenario = runsByScenario();
  return (
    <>
      <PageHead
        title="Study matrix"
        sub="The same eight tasks, three runs per agent. Five carry a passive trap; three are controls, and a control that diverges would be a false alarm."
      />
      <Card>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[560px] border-collapse text-left">
            <thead>
              <tr className="border-b border-rule bg-ground/60">
                <th className="gutter px-5 py-3 font-normal uppercase">task</th>
                {report.agents.map((a) => (
                  <th key={a} className="gutter px-5 py-3 font-normal uppercase">
                    {a}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {report.scenarios.map((scenario) => {
                const rows = byScenario.get(scenario) ?? [];
                const label = rows[0]?.label;
                return (
                  <tr key={scenario} className="border-b border-rule-soft last:border-0">
                    <th className="px-5 py-3.5 align-middle font-normal">
                      <span className="font-mono text-[13px]">{scenario}</span>
                      <span
                        className={`gutter block uppercase ${
                          label === "trapped" ? "text-warn" : ""
                        }`}
                      >
                        {label}
                      </span>
                    </th>
                    {report.agents.map((agent) => (
                      <td key={agent} className="px-5 py-3.5 align-middle">
                        <Cell runs={rows.filter((r) => r.agent === agent)} />
                      </td>
                    ))}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </Card>
      <p className="mt-4 max-w-[75ch] text-[13.5px] leading-relaxed text-ink-2">
        The second agent is the control on the tool itself: pointed away from Bob it
        reports nothing, and it reports nothing on the control tasks for either agent —
        which is what says the detector is measuring the work, not the vendor.
      </p>
    </>
  );
}
