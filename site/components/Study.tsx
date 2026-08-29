import study from "@/lib/study.json";
import { Display, Eyebrow, Section, Verdict } from "./ui";

type Cell = { verdict: string; findings: number };
type Row = { scenario: string; label: string; trap: string; cells: Record<string, Cell> };

const STATS = [
  { n: study.runs, k: "runs audited" },
  { n: study.agents.length, k: "agents" },
  { n: study.diverged, k: "diverged", tone: "bad" },
  { n: study.falseAlarms, k: "false alarms", tone: "good" },
  { n: `${study.msPerRun} ms`, k: "per run" },
];

export function Study() {
  const rows = study.matrix as Row[];
  return (
    <Section id="study" className="rule-b">
      <Eyebrow>The study</Eyebrow>
      <Display
        lead="The same eight tasks, two agents."
        rest="Five carry a passive trap — nothing tells the agent to cut a corner. Three are controls with no trap at all, and a control that diverges is a false alarm."
      />

      <div className="mt-12 grid grid-cols-2 overflow-hidden rounded-xl border border-rule sm:grid-cols-5">
        {STATS.map((s, i) => (
          <div
            key={s.k}
            className={`bg-sheet px-5 py-5 ${i ? "border-rule sm:border-l" : ""}`}
          >
            <p
              className={`font-mono text-[1.7rem] leading-none font-semibold tnum ${
                s.tone === "bad" && Number(s.n) > 0
                  ? "text-bad"
                  : s.tone === "good"
                    ? "text-good"
                    : "text-ink"
              }`}
            >
              {s.n}
            </p>
            <p className="mt-2 font-mono text-[10px] tracking-[0.13em] text-ink-3 uppercase">
              {s.k}
            </p>
          </div>
        ))}
      </div>

      <div className="mt-6 overflow-x-auto rounded-xl border border-rule">
        <table className="w-full border-collapse bg-sheet text-left">
          <thead>
            <tr className="border-b border-rule bg-[#FAFBFC]">
              <th className="px-5 py-3 font-mono text-[10px] tracking-[0.12em] text-ink-3 uppercase">
                task
              </th>
              {study.agents.map((a) => (
                <th
                  key={a}
                  className="px-5 py-3 font-mono text-[10px] tracking-[0.12em] text-ink-3 uppercase"
                >
                  {a}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.scenario} className="border-b border-rule-soft last:border-0">
                <th className="px-5 py-3.5 align-top font-normal">
                  <span className="font-mono text-[13px] text-ink">{row.scenario}</span>
                  <span
                    className={`mt-0.5 block font-mono text-[9.5px] tracking-[0.1em] uppercase ${
                      row.label === "trapped" ? "text-warn" : "text-ink-3"
                    }`}
                  >
                    {row.label}
                  </span>
                </th>
                {study.agents.map((agent) => {
                  const cell = row.cells[agent];
                  return (
                    <td key={agent} className="px-5 py-3.5 align-top">
                      {cell ? (
                        <span className="flex items-center gap-2.5">
                          <Verdict value={cell.verdict} />
                          {cell.findings > 0 && (
                            <span className="font-mono text-[11px] text-ink-3 tnum">
                              {cell.findings}
                            </span>
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

      <p className="mt-6 max-w-[70ch] text-[14.5px] leading-relaxed text-ink-2">
        The two agents behaved differently under identical conditions. Where pytest was
        missing, Claude Code ran the suite through a heredoc and checked every test &mdash;
        including the one Bob&rsquo;s change broke. That is one run each of eight tasks
        against agents that are not deterministic, so it is an observation and not a
        benchmark. What it does establish is that the tool is not tuned to make one agent
        look bad: pointed at the second, it reports nothing.
      </p>
      <p className="mt-4 max-w-[70ch] text-[14.5px] leading-relaxed text-ink-2">
        Auditing all {study.runs} runs by hand means reading{" "}
        <span className="font-mono text-ink tnum">
          {study.traceLines.toLocaleString()}
        </span>{" "}
        lines of trace. Receipts points at{" "}
        <span className="font-mono text-ink tnum">{study.citedLines}</span>.
      </p>
    </Section>
  );
}
