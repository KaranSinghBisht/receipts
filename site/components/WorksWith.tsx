const SOURCES = ["IBM Bob", "Claude Code"];
const RUNNERS = ["pytest", "unittest", "jest", "vitest", "go test", "cargo test", "rspec"];

export function WorksWith() {
  return (
    <div className="px-5 pt-14 sm:px-8">
      <p className="text-center font-mono text-[11px] tracking-[0.14em] text-ink-3 uppercase">
        Reads traces from
      </p>
      <div className="mt-5 flex flex-wrap items-center justify-center gap-3">
        {SOURCES.map((s) => (
          <span
            key={s}
            className="rounded-2xl border border-rule bg-card px-6 py-3 text-[15.5px] font-semibold tracking-[-0.01em] shadow-[0_6px_20px_-12px_rgba(21,23,28,0.2)]"
          >
            {s}
          </span>
        ))}
        <span className="gutter px-2">recognises</span>
        {RUNNERS.map((r) => (
          <span
            key={r}
            className="rounded-full border border-rule bg-card px-3.5 py-1.5 font-mono text-[12px] text-ink-2"
          >
            {r}
          </span>
        ))}
      </div>
    </div>
  );
}
