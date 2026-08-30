import { Button, Terminal } from "./ui";

export function Footer({ repo }: { repo: string }) {
  return (
    <div className="px-5 pb-10 sm:px-8">
      <div className="soft-card mx-auto max-w-[1120px] overflow-hidden rounded-[28px]">
        <div className="grid gap-10 p-8 sm:p-12 lg:grid-cols-2 lg:items-center">
          <div>
            <h2 className="display max-w-[16ch] text-[1.9rem] sm:text-[2.4rem]">
              It runs where your build runs
            </h2>
            <p className="mt-4 max-w-[46ch] text-[15.5px] leading-[1.65] text-ink-2">
              Python 3.11, no runtime dependencies. Exit code 1 on a high-severity
              finding, which fails the check and holds the merge.
            </p>
            <div className="mt-7 flex flex-wrap gap-3">
              <Button href="/dashboard">Open the dashboard &rarr;</Button>
              <Button href={repo} variant="quiet">
                Read the source
              </Button>
            </div>
          </div>
          <Terminal title="four surfaces">
            <span className="text-white/35">$ </span>receipts trace.ndjson{"\n"}
            <span className="text-white/35">{"  "}one run; exit 1 if it diverged{"\n\n"}</span>
            <span className="text-white/35">$ </span>receipts traces/ --html report.html{"\n"}
            <span className="text-white/35">{"  "}one page for a whole batch{"\n\n"}</span>
            <span className="text-white/35">$ </span>receipts traces/ --watch{"\n"}
            <span className="text-white/35">{"  "}a live board that fills in as runs land{"\n\n"}</span>
            <span className="text-white/35">$ </span>bob run --mode verifier{"\n"}
            <span className="text-white/35">{"  "}audit from inside IBM Bob</span>
          </Terminal>
        </div>
        <div className="flex flex-wrap items-center gap-4 border-t border-rule px-8 py-6 sm:px-12">
          <p className="gutter">
            Built for the IBM TechXchange 2026 Pre-conference Dev Day Hackathon
          </p>
          <div className="ml-auto flex gap-6">
            <a className="gutter transition hover:text-accent" href="/dashboard">
              Report
            </a>
            <a className="gutter transition hover:text-accent" href={repo}>
              Source
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
