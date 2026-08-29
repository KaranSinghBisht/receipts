import { Button, Terminal } from "./ui";

export function Hero({
  repo,
  diverged,
  runs,
}: {
  repo: string;
  diverged: number;
  runs: number;
}) {
  return (
    <div id="top" className="border-b border-rule">
      <div className="mx-auto grid max-w-[1240px] grid-cols-1 gap-y-12 px-6 py-20 md:grid-cols-[92px_1fr] md:gap-x-8 md:px-10 md:py-28">
        <p className="gutter">L00</p>

        <div className="min-w-0">
          <div className="grid gap-x-14 gap-y-10 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.05fr)] lg:items-center">
            <div>
              <h1 className="display max-w-[16ch] text-[2.6rem] sm:text-[3.4rem]">
                Your agent says the tests pass
              </h1>
              <p className="mt-6 max-w-[52ch] text-[17px] leading-[1.6] text-ink-2">
                Receipts holds that sentence to the agent&rsquo;s own execution trace
                &mdash; the files it wrote, the commands it ran, what those commands
                printed &mdash; and cites the line that settles it.
              </p>
              <div className="mt-8 flex flex-wrap gap-3">
                <Button href="/report.html">Open the live report &rarr;</Button>
                <Button href={repo} variant="quiet">
                  Read the source
                </Button>
              </div>
              <p className="gutter mt-7">
                {diverged} of {runs} real agent runs claimed something their trace does
                not support
              </p>
            </div>

            <Terminal title="receipts trace.ndjson">
              <span className="text-white/35">$ </span>receipts trace.ndjson{"\n\n"}
              RECEIPTS · <span className="text-[#E8837A]">diverged</span> · 1 medium ·
              bob{"\n\n"}
              {"  "}
              <span className="text-white/35">claimed:</span>{" "}
              <span className="text-[#E3B675]">
                &quot;parse_range(&apos;5&apos;) now returns (5, 5){"\n"}
                {"            "}and the existing range case still works.&quot;
              </span>
              {"\n"}
              {"  "}
              <span className="text-white/35">actual :</span> 1 file written, 1 command
              run{"\n\n"}
              {" "}
              <span className="text-[#E8837A]">!</span>{" "}
              <span className="font-semibold text-white">
                1. Claimed the change works, but never{"\n"}
                {"      "}ran the tests
              </span>
              {"\n"}
              {"     "}
              <span className="text-white/35">
                · [line 7] test file visible in listing{"\n"}
                {"     "}· [line 28] command run instead
              </span>
            </Terminal>
          </div>
        </div>
      </div>
    </div>
  );
}
