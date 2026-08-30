import { LogoMark } from "./Logo";
import { Button } from "./ui";

export function Nav({ repo }: { repo: string }) {
  return (
    <header className="sticky top-4 z-30 px-4">
      <div className="mx-auto flex max-w-[1120px] items-center gap-4 rounded-full border border-rule bg-card/92 px-6 py-3 shadow-[0_10px_30px_-16px_rgba(21,23,28,0.25)] backdrop-blur">
        <a href="#top" className="flex items-center gap-2.5">
          <LogoMark size={27} />
          <span className="text-[17px] font-semibold tracking-[-0.02em]">Receipts</span>
          <span className="gutter hidden sm:inline">for IBM Bob</span>
        </a>
        <nav className="ml-auto flex items-center gap-2.5">
          <a
            href={repo}
            className="hidden rounded-full px-4 py-2 text-[14px] font-medium text-ink-2 transition hover:text-ink sm:inline"
          >
            Source
          </a>
          <Button href="/dashboard">Open the dashboard</Button>
        </nav>
      </div>
    </header>
  );
}
