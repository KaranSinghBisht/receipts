const RUNNERS = [
  "pytest", "unittest", "jest", "vitest", "go test", "cargo test", "rspec",
  "tox", "phpunit", "gradle test", "mvn test",
];

/** Built for IBM Bob — the trace source. The runner marquee shows the breadth
 *  of what the audit understands once a trace is in hand. */
export function WorksWith() {
  const loop = [...RUNNERS, ...RUNNERS];
  return (
    <div className="band mt-16 overflow-hidden py-8">
      <div className="flex flex-col items-center gap-5">
        <p className="font-mono text-[11px] tracking-[0.14em] text-ink-3 uppercase">
          Built on IBM Bob&rsquo;s execution traces
        </p>
        <div className="flex flex-wrap items-center justify-center gap-3 px-5">
          <span className="rounded-2xl border border-rule bg-ground px-6 py-2.5 text-[15.5px] font-semibold tracking-[-0.01em]">
            IBM Bob
          </span>
          <span className="font-mono text-[11.5px] text-ink-3">
            bob run --format stream-json
          </span>
        </div>
        <div className="relative w-full" aria-hidden>
          <div className="marquee px-3 py-1">
            {loop.map((r, i) => (
              <span
                key={`${r}-${i}`}
                className="rounded-full border border-rule bg-ground px-4 py-1.5 font-mono text-[12px] whitespace-nowrap text-ink-2"
              >
                {r}
              </span>
            ))}
          </div>
          <div className="pointer-events-none absolute inset-y-0 left-0 w-24 bg-gradient-to-r from-card to-transparent" />
          <div className="pointer-events-none absolute inset-y-0 right-0 w-24 bg-gradient-to-l from-card to-transparent" />
        </div>
        <p className="px-5 text-center font-mono text-[10.5px] text-ink-3">
          test output it recognises inside a trace, whatever ran the suite
        </p>
      </div>
    </div>
  );
}
