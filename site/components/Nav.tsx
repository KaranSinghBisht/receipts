import { Button } from "./ui";

export function Nav({ repo }: { repo: string }) {
  return (
    <header className="sticky top-0 z-30 border-b border-rule bg-paper/90 backdrop-blur">
      <div className="mx-auto flex max-w-[1240px] items-center gap-4 px-6 py-3.5 md:px-10">
        <a href="#top" className="flex items-baseline gap-2.5">
          <span className="text-[17px] font-semibold tracking-[-0.02em]">Receipts</span>
          <span className="gutter hidden sm:inline">for IBM Bob</span>
        </a>
        <nav className="ml-auto flex items-center gap-2">
          <Button href={repo} variant="quiet">
            Source
          </Button>
          <Button href="/report.html">Open the report</Button>
        </nav>
      </div>
    </header>
  );
}
