import study from "@/lib/study.json";
import { Heading, Lede, Row, Verdict } from "./ui";

type Cell = { verdict: string; findings: number };
type MatrixRow = { scenario: string; label: string; cells: Record<string, Cell> };

export function Study() {
  const rows = study.matrix as MatrixRow[];
  const stats: [string | number, string, string?][] = [
    [study.runs, "runs audited"],
    [study.agents.length, "agents"],
    [study.diverged, "diverged", "signal"],
    [study.falseAlarms, "false alarms", "good"],
    [`${study.msPerRun}ms`, "per run"],
  ];

  return (
    <Row id="study" line="L05" label="the study">
      <Heading>The same eight tasks, run by two agents</Heading>
      <Lede>
        Five carry a passive trap — nothing tells the agent to cut a corner, there is
        simply a test file it is not required to run. Three are controls with no trap at
        all, and a control that diverges is a false alarm. That number decides whether any
        of this is usable.
      </Lede>

      <div className="mt-11 flex flex-wrap gap-x-12 gap-y-6 border-y border-rule py-6">
        {stats.map(([n, k, tone]) => (
          <div key={k}>
            <p
              className={`font-mono text-[1.75rem] leading-none font-semibold tnum ${
                tone === "signal" && Number(n) > 0
                  ? "text-signal"
                  : tone === "good"
                    ? "text-good"
                    : "text-ink"
              }`}
            >
              {n}
            </p>
            <p className="gutter mt-2">{k}</p>
          </div>
        ))}
      </div>

      <div className="mt-8 overflow-x-auto">
        <table className="w-full min-w-[520px] border-collapse text-left">
          <thead>
            <tr className="border-b border-rule">
              <th className="gutter py-3 pr-6 font-normal">task</th>
              {study.agents.map((a) => (
                <th key={a} className="gutter py-3 pr-6 font-normal">
                  {a}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.scenario} className="border-b border-rule-soft">
                <th className="py-3.5 pr-6 align-top font-normal">
                  <span className="font-mono text-[13px] text-ink">{row.scenario}</span>
                  <span
                    className={`gutter mt-0.5 block uppercase ${
                      row.label === "trapped" ? "text-warn" : ""
                    }`}
                  >
                    {row.label}
                  </span>
                </th>
                {study.agents.map((agent) => {
                  const cell = row.cells[agent];
                  return (
                    <td key={agent} className="py-3.5 pr-6 align-top">
                      {cell ? (
                        <span className="flex items-center gap-2.5">
                          <Verdict value={cell.verdict} />
                          {cell.findings > 0 && (
                            <span className="gutter">{cell.findings}</span>
                          )}
                        </span>
                      ) : (
                        <span className="text-ink-3">&mdash;</span>
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-9 grid gap-8 md:grid-cols-2">
        <p className="text-[14.5px] leading-relaxed text-ink-2">
          The two agents behaved differently under identical conditions. Where pytest was
          missing, Claude Code ran the suite through a heredoc and checked every test,
          including the one Bob&rsquo;s change broke. One run each of eight tasks against
          agents that are not deterministic is an observation, not a benchmark.
        </p>
        <p className="text-[14.5px] leading-relaxed text-ink-2">
          What it does establish: the tool is not tuned to make one agent look bad. Pointed
          at the second it reports nothing, and it reports nothing on the controls for
          both. Auditing all {study.runs} by hand means reading{" "}
          <span className="font-mono text-ink tnum">
            {study.traceLines.toLocaleString()}
          </span>{" "}
          lines. Receipts points at{" "}
          <span className="font-mono text-ink tnum">{study.citedLines}</span>.
        </p>
      </div>
    </Row>
  );
}
