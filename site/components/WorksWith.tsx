const SOURCES = [
  { name: "IBM Bob", note: "bob run --format stream-json" },
  { name: "Claude Code", note: "claude --output-format stream-json" },
];

const TARGETS = ["GitHub Actions", "pytest", "unittest", "Jest", "go test", "cargo test"];

export function WorksWith() {
  return (
    <div className="rule-t rule-b px-6 py-8 sm:px-12 md:px-16">
      <div className="flex flex-col gap-6 md:flex-row md:items-center md:gap-12">
        <p className="font-mono text-[11px] tracking-[0.14em] text-ink-3 uppercase whitespace-nowrap">
          Reads traces from
        </p>
        <div className="flex flex-wrap gap-x-10 gap-y-3">
          {SOURCES.map((s) => (
            <div key={s.name}>
              <p className="text-[15px] font-medium text-ink">{s.name}</p>
              <p className="font-mono text-[11px] text-ink-3">{s.note}</p>
            </div>
          ))}
        </div>
        <div className="flex flex-wrap gap-2 md:ml-auto">
          {TARGETS.map((t) => (
            <span
              key={t}
              className="rounded-md border border-rule px-2.5 py-1 font-mono text-[11px] text-ink-2"
            >
              {t}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
