const SOURCES = [
  ["IBM Bob", "bob run --format stream-json"],
  ["Claude Code", "claude --output-format stream-json"],
];

const RUNNERS = ["pytest", "unittest", "jest", "vitest", "go test", "cargo test", "rspec"];

export function WorksWith() {
  return (
    <div className="border-b border-rule bg-panel">
      <div className="mx-auto grid max-w-[1240px] grid-cols-1 gap-y-7 px-6 py-9 md:grid-cols-[92px_1fr] md:gap-x-8 md:px-10">
        <p className="gutter">L01</p>
        <div className="grid gap-8 lg:grid-cols-[auto_1fr] lg:items-start lg:gap-14">
          <div className="flex flex-wrap gap-x-10 gap-y-4">
            {SOURCES.map(([name, cmd]) => (
              <div key={name}>
                <p className="text-[15px] font-medium">{name}</p>
                <p className="mt-0.5 font-mono text-[11px] text-ink-3">{cmd}</p>
              </div>
            ))}
          </div>
          <div className="lg:justify-self-end">
            <p className="gutter mb-2.5">recognises</p>
            <div className="flex flex-wrap gap-x-5 gap-y-1.5">
              {RUNNERS.map((r) => (
                <span key={r} className="font-mono text-[12px] text-ink-2">
                  {r}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
