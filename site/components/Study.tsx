import study from "@/lib/study.json";
import { Heading, Lede, Row } from "./ui";

type Cell = { runs: number; diverged: number; findings: number };
type MatrixRow = { scenario: string; label: string; cells: Record<string, Cell> };

function CellMark({ cell }: { cell?: Cell }) {
  if (!cell) return <span className="text-ink-3">&mdash;</span>;
  const bad = cell.diverged > 0;
  const text = bad
    ? cell.runs > 1
      ? `diverged ${cell.diverged}/${cell.runs}`
      : "diverged"
    : cell.runs > 1
      ? `clean ${cell.runs}/${cell.runs}`
      : "clean";
  return (
    <span
      className={`inline-flex items-center gap-2 font-mono text-[11.5px] tracking-[0.04em] ${
        bad ? "text-signal" : "text-good"
      }`}
    >
      <span
        aria-hidden
        className={`h-[8px] w-[8px] ${bad ? "bg-signal" : "bg-good"}`}
        style={{ borderRadius: 1 }}
      />
      {text}
    </span>
  );
}

export function Study() {
  const rows = study.matrix as MatrixRow[];
  const stats: [string | number, string, string?][] = [
    [study.runs, "runs audited"],
    [study.agents.length, "agents"],
    [`${study.trappedDiverged}/${study.trappedRuns}`, "trapped runs diverged", "signal"],
    [`${study.falseAlarms}/${study.controlRuns}`, "false alarms", "good"],
    [`${study.msPerRun}ms`, "per run"],
  ];

  return (
    <Row id="study" line="L05" label="the study">
      <Heading>The same eight tasks, repeated, across two agents</Heading>
      <Lede>
        Five tasks carry a passive trap — nothing tells the agent to cut a corner, there
        is simply a test file it is not required to run. Three are controls with no trap
        at all. Agents are not deterministic, so every task ran several times per agent:
        the unit below is a rate, not a verdict. A control that diverges is a false
        alarm, and that number decides whether any of this is usable.
      </Lede>

      <div className="mt-11 flex flex-wrap gap-x-12 gap-y-6 border-y border-rule py-6">
        {stats.map(([n, k, tone]) => (
          <div key={k}>
            <p
              className={`font-mono text-[1.75rem] leading-none font-semibold tnum ${
                tone === "signal"
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
        <table className="w-full min-w-[540px] border-collapse text-left">
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
                {study.agents.map((agent) => (
                  <td key={agent} className="py-3.5 pr-6 align-top">
                    <CellMark cell={row.cells[agent]} />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-9 grid gap-8 md:grid-cols-2">
        <p className="text-[14.5px] leading-relaxed text-ink-2">
          The two agents behave differently under identical conditions. Where pytest was
          missing, Claude Code ran the suite through a heredoc and checked every test,
          including the one Bob&rsquo;s change broke. The repeats are the point: a single
          run of a non-deterministic system proves nothing, and a rate across repeated
          runs is a claim someone can check.
        </p>
        <p className="text-[14.5px] leading-relaxed text-ink-2">
          The tool is not tuned to make one agent look bad — it reports{" "}
          {study.falseAlarms} false alarms across {study.controlRuns} control runs, on
          both agents. Auditing all {study.runs} runs by hand means reading{" "}
          <span className="font-mono text-ink tnum">
            {study.traceLines.toLocaleString()}
          </span>{" "}
          lines of trace. Receipts points at{" "}
          <span className="font-mono text-ink tnum">{study.citedLines}</span>, in{" "}
          {study.msPerRun}ms per run.
        </p>
      </div>
    </Row>
  );
}
