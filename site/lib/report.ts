import data from "./report.json";

export type Evidence = { seq: number; label: string; excerpt: string };
export type Finding = {
  detector: string;
  severity: string;
  title: string;
  detail: string;
  evidence: Evidence[];
};
export type TimelineRow = {
  seq: number;
  kind: string;
  detail: string;
  outcome: string;
  flagged: boolean;
  test: boolean;
  recovered: boolean;
};
export type Run = {
  name: string;
  scenario: string;
  label: string | null;
  verdict: string;
  agent: string;
  claim: string;
  findings: Finding[];
  files_written: number;
  commands: number;
  duration_ms: number | null;
  cost: number | null;
  timeline: TimelineRow[];
  strip: string[];
  traceLines: number;
  citedLines: number;
};

export type Report = {
  generated: string;
  receipts_version: string;
  agents: string[];
  scenarios: string[];
  totals: {
    diverged: number;
    clean: number;
    findings: number;
    trace_lines: number;
    cited_lines: number;
    false_alarms: number | null;
  };
  runs: Run[];
};

export const report = data as unknown as Report;

export const diverged = (r: Run) => r.verdict === "diverged";

export const runsByScenario = () => {
  const map = new Map<string, Run[]>();
  for (const run of report.runs) {
    const list = map.get(run.scenario) ?? [];
    list.push(run);
    map.set(run.scenario, list);
  }
  return map;
};
