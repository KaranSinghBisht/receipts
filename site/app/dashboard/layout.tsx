import type { ReactNode } from "react";
import Link from "next/link";

import { LogoMark } from "@/components/Logo";
import { report } from "@/lib/report";

const NAV = [
  { href: "/dashboard", label: "Overview" },
  { href: "/dashboard/runs", label: "Runs", count: report.runs.length },
  { href: "/dashboard/findings", label: "Findings", count: report.totals.findings },
  { href: "/dashboard/graph", label: "Graph" },
  { href: "/dashboard/study", label: "Study matrix" },
];

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen">
      <aside className="sticky top-0 hidden h-screen w-[236px] shrink-0 flex-col border-r border-rule bg-card px-4 py-5 md:flex">
        <Link href="/" className="flex items-center gap-2.5 px-2">
          <LogoMark size={26} />
          <span className="text-[15.5px] font-semibold tracking-[-0.02em]">Receipts</span>
        </Link>

        <nav className="mt-7 flex flex-col gap-1">
          {NAV.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="flex items-center justify-between rounded-xl px-3 py-2 text-[14px] font-medium text-ink-2 transition hover:bg-ground hover:text-ink"
            >
              {item.label}
              {"count" in item && item.count !== undefined ? (
                <span className="rounded-full bg-ground px-2 py-0.5 font-mono text-[10.5px] text-ink-3 tnum">
                  {item.count}
                </span>
              ) : null}
            </Link>
          ))}
        </nav>

        <div className="mt-auto space-y-3">
          <div className="rounded-xl border border-rule bg-ground p-3.5">
            <p className="gutter">workspace</p>
            <p className="mt-1 text-[13.5px] font-medium">Nightly study (demo)</p>
            <p className="mt-0.5 font-mono text-[10.5px] text-ink-3">
              {report.agents.join(" · ")}
            </p>
          </div>
          <Link
            href="/activate"
            className="block rounded-xl border border-rule px-3.5 py-2.5 text-center text-[13px] font-medium text-ink-2 transition hover:border-ink-3 hover:text-ink"
          >
            Connect your machine
          </Link>
          <p className="px-1 font-mono text-[9.5px] leading-relaxed text-ink-3">
            This workspace is the public study. Your own runs stay behind{" "}
            <span className="text-ink-2">receipts login</span>.
          </p>
        </div>
      </aside>

      <div className="min-w-0 flex-1">
        <header className="sticky top-0 z-20 flex items-center gap-3 border-b border-rule bg-card/90 px-5 py-3 backdrop-blur md:hidden">
          <Link href="/" className="flex items-center gap-2">
            <LogoMark size={22} />
            <span className="text-[14.5px] font-semibold">Receipts</span>
          </Link>
          <nav className="ml-auto flex gap-3 overflow-x-auto font-mono text-[11px]">
            {NAV.map((i) => (
              <Link key={i.href} href={i.href} className="whitespace-nowrap text-ink-2">
                {i.label}
              </Link>
            ))}
          </nav>
        </header>
        <main className="px-5 py-7 sm:px-8">{children}</main>
      </div>
    </div>
  );
}
