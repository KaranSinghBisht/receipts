"use client";

import { useMemo, useState } from "react";

import { Card, PageHead, RunRow } from "@/components/dash";
import { diverged, report } from "@/lib/report";

const CHIPS = [
  ["all", "all"],
  ["diverged", "diverged"],
  ["clean", "clean"],
  ...report.agents.map((a) => [`agent:${a}`, a]),
  ["trapped", "trapped"],
  ["control", "control"],
] as const;

export default function Runs() {
  const [filter, setFilter] = useState("all");
  const [query, setQuery] = useState("");

  const runs = useMemo(() => {
    return report.runs
      .filter((run) => {
        if (filter === "diverged") return diverged(run);
        if (filter === "clean") return !diverged(run);
        if (filter.startsWith("agent:")) return run.agent === filter.slice(6);
        if (filter === "trapped" || filter === "control") return run.label === filter;
        return true;
      })
      .filter((run) => !query || run.scenario.includes(query) || run.name.includes(query))
      .sort(
        (a, b) =>
          Number(diverged(b)) - Number(diverged(a)) ||
          a.scenario.localeCompare(b.scenario),
      );
  }, [filter, query]);

  return (
    <>
      <PageHead
        title="Runs"
        sub="Every audited run in the workspace. Click one for its claim, findings, and full execution trace."
      />
      <div className="mb-4 flex flex-wrap items-center gap-2">
        {CHIPS.map(([id, label]) => (
          <button
            key={id}
            onClick={() => setFilter(id)}
            aria-pressed={filter === id}
            className={`rounded-full border px-3.5 py-1.5 font-mono text-[11px] transition ${
              filter === id
                ? "border-ink bg-ink text-white"
                : "border-rule bg-card text-ink-2 hover:border-ink-3"
            }`}
          >
            {label}
          </button>
        ))}
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="filter by task…"
          className="ml-auto w-[180px] rounded-full border border-rule bg-card px-4 py-1.5 font-mono text-[12px] outline-none focus:border-ink"
        />
      </div>
      <Card>
        {runs.length ? (
          runs.map((run) => <RunRow key={run.name} run={run} />)
        ) : (
          <p className="px-4 py-6 text-[14px] text-ink-2">No runs match.</p>
        )}
      </Card>
    </>
  );
}
