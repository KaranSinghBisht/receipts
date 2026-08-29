import { Button, Heading, Terminal } from "./ui";

export function Footer({ repo }: { repo: string }) {
  return (
    <>
      <section className="border-b border-rule">
        <div className="mx-auto grid max-w-[1240px] grid-cols-1 gap-y-10 px-6 py-20 md:grid-cols-[92px_1fr] md:gap-x-8 md:px-10 md:py-24">
          <p className="gutter">L07</p>
          <div className="grid gap-x-14 gap-y-10 lg:grid-cols-2 lg:items-center">
            <div>
              <Heading>It runs where your build runs</Heading>
              <p className="mt-5 max-w-[46ch] text-[16px] leading-[1.6] text-ink-2">
                Python 3.11, no runtime dependencies. Exit code 1 on a high-severity
                finding, which fails the check and holds the merge.
              </p>
              <div className="mt-8 flex flex-wrap gap-3">
                <Button href="/report.html">Open the live report &rarr;</Button>
                <Button href={repo} variant="quiet">
                  Read the source
                </Button>
              </div>
            </div>

            <Terminal title="four surfaces">
              <span className="text-white/35">$ </span>receipts trace.ndjson{"\n"}
              <span className="text-white/35">
                {"  "}one run; exit 1 if it diverged{"\n\n"}
              </span>
              <span className="text-white/35">$ </span>receipts traces/ --html report.html
              {"\n"}
              <span className="text-white/35">
                {"  "}one page for a whole batch{"\n\n"}
              </span>
              <span className="text-white/35">$ </span>receipts traces/ --watch{"\n"}
              <span className="text-white/35">
                {"  "}a live board that fills in as runs land{"\n\n"}
              </span>
              <span className="text-white/35">$ </span>bob run --mode verifier{"\n"}
              <span className="text-white/35">{"  "}audit from inside IBM Bob</span>
            </Terminal>
          </div>
        </div>
      </section>

      <footer>
        <div className="mx-auto flex max-w-[1240px] flex-wrap items-center gap-4 px-6 py-8 md:px-10">
          <p className="gutter">
            Built for the IBM TechXchange 2026 Pre-conference Dev Day Hackathon
          </p>
          <div className="ml-auto flex gap-6">
            <a className="gutter hover:text-signal" href="/report.html">
              Report
            </a>
            <a className="gutter hover:text-signal" href={repo}>
              Source
            </a>
          </div>
        </div>
      </footer>
    </>
  );
}
