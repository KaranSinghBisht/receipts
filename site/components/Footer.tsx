import { Button } from "./ui";

const COMMANDS = [
  ["receipts trace.ndjson", "one run; exit 1 if it diverged"],
  ["receipts traces/ --html report.html", "one page for a whole batch"],
  ["receipts traces/ --watch", "a live board that fills in as runs land"],
  ["bob run --mode verifier", "audit from inside IBM Bob"],
];

export function Footer({ repo }: { repo: string }) {
  return (
    <>
      <section className="px-6 py-20 sm:px-12 md:px-16">
        <div className="grid gap-10 md:grid-cols-2 md:items-center">
          <div>
            <h2 className="font-serif text-[2rem] leading-[1.12] tracking-[-0.02em] text-balance">
              It runs where your build runs
            </h2>
            <p className="mt-4 max-w-[46ch] text-[15px] leading-relaxed text-ink-2">
              Python 3.11 and no runtime dependencies. Exit code 1 on a high-severity
              finding, which fails the check and holds the merge.
            </p>
            <div className="mt-7 flex flex-wrap gap-3">
              <Button href="/report.html">Open the live report &rarr;</Button>
              <Button href={repo} variant="quiet">
                Read the source
              </Button>
            </div>
          </div>

          <div className="overflow-hidden rounded-xl border border-rule bg-[#0C1017]">
            <div className="space-y-3 px-5 py-5">
              {COMMANDS.map(([cmd, note]) => (
                <div key={cmd}>
                  <p className="font-mono text-[12.5px] text-[#D7DEE9]">
                    <span className="text-[#7C8798]">$ </span>
                    {cmd}
                  </p>
                  <p className="font-mono text-[11px] text-[#7C8798]">{note}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <footer className="rule-t px-6 py-8 sm:px-12 md:px-16">
        <div className="flex flex-wrap items-center gap-4 font-mono text-[11px] text-ink-3">
          <span>Built for the IBM TechXchange 2026 Pre-conference Dev Day Hackathon.</span>
          <a className="ml-auto text-ink-2 hover:text-accent" href="/report.html">
            Report
          </a>
          <a className="text-ink-2 hover:text-accent" href={repo}>
            Source
          </a>
        </div>
      </footer>
    </>
  );
}
