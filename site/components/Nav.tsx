import { Button } from "./ui";

export function Nav({ repo }: { repo: string }) {
  return (
    <header className="sticky top-0 z-30 border-b border-rule bg-sheet/85 backdrop-blur">
      <div className="flex items-center gap-4 px-6 py-3.5 sm:px-12 md:px-16">
        <a
          href="#top"
          className="font-serif text-[22px] tracking-[0.02em] text-ink"
        >
          Receipts
        </a>
        <nav className="ml-auto flex items-center gap-2">
          <span className="mr-3 hidden font-mono text-[11px] tracking-[0.1em] text-ink-3 uppercase sm:inline">
            for IBM Bob
          </span>
          <Button href={repo} variant="quiet">
            Source
          </Button>
          <Button href="/report.html">Open the report</Button>
        </nav>
      </div>
    </header>
  );
}
