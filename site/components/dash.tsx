import Link from "next/link";

import type { Run } from "@/lib/report";
import { Verdict } from "./ui";

export function PageHead({
  title,
  sub,
  right,
}: {
  title: string;
  sub?: string;
  right?: React.ReactNode;
}) {
  return (
    <div className="flex flex-wrap items-end justify-between gap-3 pb-6">
      <div>
        <h1 className="display text-[1.6rem]">{title}</h1>
        {sub ? <p className="mt-1.5 max-w-[70ch] text-[14px] text-ink-2">{sub}</p> : null}
      </div>
      {right}
    </div>
  );
}

export function StatCard({
  n,
  k,
  tone,
}: {
  n: string | number;
  k: string;
  tone?: "signal" | "good";
}) {
  return (
    <div className="rounded-2xl border border-rule bg-card px-5 py-4 shadow-[0_6px_20px_-14px_rgba(21,23,28,0.16)]">
      <p
        className={`font-mono text-[1.6rem] leading-none font-semibold tnum ${
          tone === "signal" ? "text-signal" : tone === "good" ? "text-good" : "text-ink"
        }`}
      >
        {n}
      </p>
      <p className="gutter mt-2 uppercase">{k}</p>
    </div>
  );
}

export function Strip({ cells }: { cells: string[] }) {
  if (!cells.length) return null;
  return (
    <span aria-hidden className="flex h-[12px] w-full max-w-[220px] gap-[2px]">
      {cells.map((c, i) => (
        <span
          key={i}
          className={`min-w-[3px] flex-1 rounded-[2px] ${
            c === "flag"
              ? "bg-signal"
              : c === "error"
                ? "bg-warn/60"
                : c === "ok"
                  ? "bg-good/45"
                  : "bg-rule"
          }`}
        />
      ))}
    </span>
  );
}

export function RunRow({ run }: { run: Run }) {
  return (
    <Link
      href={`/dashboard/runs/${encodeURIComponent(run.name)}`}
      className="grid grid-cols-[1fr_auto] items-center gap-x-5 gap-y-2 border-b border-rule-soft px-4 py-3.5 transition hover:bg-ground sm:grid-cols-[200px_110px_1fr_auto]"
    >
      <span className="min-w-0">
        <span className="block truncate font-mono text-[13px] font-semibold">
          {run.scenario}
        </span>
        <span className="gutter uppercase">
          {run.agent}
          {run.label ? ` · ${run.label}` : ""}
        </span>
      </span>
      <span className="hidden sm:block">
        <Verdict value={run.verdict} />
      </span>
      <span className="hidden min-w-0 sm:block">
        {run.findings.length ? (
          <span className="block truncate text-[13px] text-ink-2">
            {run.findings[0].title}
          </span>
        ) : (
          <Strip cells={run.strip} />
        )}
      </span>
      <span className="gutter justify-self-end tnum">
        {run.duration_ms ? `${(run.duration_ms / 1000).toFixed(0)}s` : "—"}
      </span>
      <span className="sm:hidden">
        <Verdict value={run.verdict} />
      </span>
    </Link>
  );
}

export function Card({
  title,
  children,
  className = "",
}: {
  title?: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <section
      className={`overflow-hidden rounded-2xl border border-rule bg-card shadow-[0_6px_20px_-14px_rgba(21,23,28,0.16)] ${className}`}
    >
      {title ? (
        <h2 className="border-b border-rule px-4 py-3 font-mono text-[10.5px] tracking-[0.13em] text-ink-3 uppercase">
          {title}
        </h2>
      ) : null}
      {children}
    </section>
  );
}
