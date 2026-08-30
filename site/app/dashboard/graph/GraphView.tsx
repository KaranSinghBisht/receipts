"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import {
  forceCenter,
  forceCollide,
  forceLink,
  forceManyBody,
  forceX,
  forceY,
  type SimulationLinkDatum,
  type SimulationNodeDatum,
} from "d3-force";
import { forceSimulation } from "d3-force";

import { diverged, report, type Run } from "@/lib/report";

/**
 * The audit as a shape. Tasks are hubs; each run orbits its task; a run that
 * diverged is also pulled toward the finding that fired on it — so the layout
 * itself says what a list cannot: the red runs share a cause.
 */

type NodeKind = "scenario" | "finding" | "run";
type GNode = SimulationNodeDatum & {
  id: string;
  kind: NodeKind;
  label: string;
  r: number;
  run?: Run;
  bad?: boolean;
};
type GLink = SimulationLinkDatum<GNode> & { hot?: boolean };

const W = 960;
const H = 620;

function buildGraph() {
  const nodes: GNode[] = [];
  const links: GLink[] = [];

  for (const scenario of report.scenarios) {
    nodes.push({ id: `s:${scenario}`, kind: "scenario", label: scenario, r: 26 });
  }

  const findingTitles = new Set<string>();
  for (const run of report.runs) {
    for (const f of run.findings) findingTitles.add(f.title);
  }
  for (const title of findingTitles) {
    nodes.push({ id: `f:${title}`, kind: "finding", label: title, r: 20 });
  }

  for (const run of report.runs) {
    const bad = diverged(run);
    nodes.push({
      id: `r:${run.name}`,
      kind: "run",
      label: `${run.scenario} · ${run.agent}`,
      r: bad ? 10 : 7,
      run,
      bad,
    });
    links.push({ source: `r:${run.name}`, target: `s:${run.scenario}` });
    for (const f of run.findings) {
      links.push({ source: `r:${run.name}`, target: `f:${f.title}`, hot: true });
    }
  }
  return { nodes, links };
}

export function GraphView() {
  const router = useRouter();
  const { nodes, links } = useMemo(() => buildGraph(), []);
  const [, setTick] = useState(0);
  const [hover, setHover] = useState<GNode | null>(null);
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    const sim = forceSimulation<GNode>(nodes)
      .force(
        "link",
        forceLink<GNode, GLink>(links)
          .id((d) => d.id)
          .distance((l) => ((l as GLink).hot ? 90 : 52))
          .strength((l) => ((l as GLink).hot ? 0.5 : 0.25)),
      )
      .force("charge", forceManyBody().strength(-120))
      .force("collide", forceCollide<GNode>().radius((d) => d.r + 6))
      .force("center", forceCenter(W / 2, H / 2))
      .force("x", forceX(W / 2).strength(0.045))
      .force("y", forceY(H / 2).strength(0.06));

    sim.on("tick", () => setTick((t) => t + 1));
    const stop = setTimeout(() => sim.stop(), 4500);
    return () => {
      clearTimeout(stop);
      sim.stop();
    };
  }, [nodes, links]);

  const connected = useMemo(() => {
    if (!hover) return null;
    const set = new Set<string>([hover.id]);
    for (const l of links) {
      const s = (l.source as GNode).id ?? l.source;
      const t = (l.target as GNode).id ?? l.target;
      if (s === hover.id) set.add(t as string);
      if (t === hover.id) set.add(s as string);
    }
    return set;
  }, [hover, links]);

  const dim = (id: string) => (connected ? (connected.has(id) ? 1 : 0.14) : 1);

  return (
    <div className="relative overflow-hidden rounded-2xl border border-rule bg-card shadow-[0_6px_20px_-14px_rgba(21,23,28,0.16)]">
      <div className="gridfield pointer-events-none absolute inset-0 opacity-60" aria-hidden />
      <svg
        ref={svgRef}
        viewBox={`0 0 ${W} ${H}`}
        className="relative block h-auto w-full"
        role="img"
        aria-label="Every run in the workspace, clustered by task; diverged runs are pulled toward the findings that fired on them"
      >
        <g>
          {links.map((l, i) => {
            const s = l.source as GNode;
            const t = l.target as GNode;
            if (s.x === undefined || t.x === undefined) return null;
            const on =
              !connected || (connected.has(s.id) && connected.has(t.id));
            return (
              <line
                key={i}
                x1={s.x}
                y1={s.y}
                x2={t.x}
                y2={t.y}
                stroke={l.hot ? "var(--signal)" : "var(--ink-3)"}
                strokeOpacity={on ? (l.hot ? 0.5 : 0.22) : 0.04}
                strokeWidth={l.hot ? 1.4 : 1}
              />
            );
          })}
        </g>
        <g>
          {nodes.map((n) => {
            if (n.x === undefined) return null;
            const fill =
              n.kind === "scenario"
                ? "var(--card)"
                : n.kind === "finding"
                  ? "var(--signal)"
                  : n.bad
                    ? "var(--signal)"
                    : "var(--good)";
            return (
              <g
                key={n.id}
                transform={`translate(${n.x},${n.y})`}
                opacity={dim(n.id)}
                onMouseEnter={() => setHover(n)}
                onMouseLeave={() => setHover(null)}
                onClick={() =>
                  n.run &&
                  router.push(`/dashboard/runs/${encodeURIComponent(n.run.name)}`)
                }
                style={{ cursor: n.run ? "pointer" : "default" }}
              >
                {n.kind !== "scenario" ? (
                  <circle r={n.r + 5} fill={fill} opacity={0.14} />
                ) : null}
                <circle
                  r={n.r}
                  fill={fill}
                  stroke={
                    n.kind === "scenario"
                      ? "var(--ink-3)"
                      : n.kind === "finding"
                        ? "var(--signal)"
                        : "transparent"
                  }
                  strokeWidth={n.kind === "scenario" ? 1.2 : 0}
                  fillOpacity={n.kind === "finding" ? 0.2 : 1}
                />
                {n.run && n.run.agent === "claude" ? (
                  <circle r={n.r + 2.5} fill="none" stroke="var(--ink-3)" strokeWidth={1} />
                ) : null}
                {n.kind === "scenario" ? (
                  <text
                    textAnchor="middle"
                    dy="3.5"
                    className="pointer-events-none"
                    style={{
                      font: "600 9.5px var(--font-plex-mono), monospace",
                      fill: "var(--ink-2)",
                    }}
                  >
                    {n.label.length > 12 ? n.label.slice(0, 11) + "…" : n.label}
                  </text>
                ) : null}
              </g>
            );
          })}
        </g>
      </svg>

      {hover ? (
        <div className="pointer-events-none absolute top-3 left-3 max-w-[320px] rounded-xl border border-rule bg-card px-3.5 py-2.5 shadow-lg">
          {hover.run ? (
            <>
              <p className="font-mono text-[12px] font-semibold">
                {hover.run.scenario}{" "}
                <span className="font-normal text-ink-3">· {hover.run.agent}</span>
              </p>
              <p
                className={`mt-0.5 font-mono text-[11px] ${
                  hover.bad ? "text-signal" : "text-good"
                }`}
              >
                {hover.run.verdict}
                {hover.run.findings.length
                  ? ` · ${hover.run.findings.length} finding${hover.run.findings.length > 1 ? "s" : ""}`
                  : ""}
              </p>
              <p className="mt-1 text-[11.5px] text-ink-3">click to open the run</p>
            </>
          ) : (
            <p className="text-[12.5px] leading-snug font-medium">
              {hover.kind === "finding" ? "Finding: " : "Task: "}
              {hover.label}
            </p>
          )}
        </div>
      ) : null}

      <div className="flex flex-wrap items-center gap-x-5 gap-y-2 border-t border-rule px-4 py-3 font-mono text-[10.5px] text-ink-3">
        <span className="flex items-center gap-1.5">
          <span className="h-[8px] w-[8px] rounded-full bg-good" /> clean run
        </span>
        <span className="flex items-center gap-1.5">
          <span className="h-[8px] w-[8px] rounded-full bg-signal" /> diverged run
        </span>
        <span className="flex items-center gap-1.5">
          <span className="h-[9px] w-[9px] rounded-full border border-ink-3" /> ring = claude
          (control agent)
        </span>
        <span className="flex items-center gap-1.5">
          <span className="h-[9px] w-[9px] rounded-full border border-signal bg-signal/20" />{" "}
          finding hub
        </span>
        <span className="ml-auto">hover to trace · click a run to open it</span>
      </div>
    </div>
  );
}
