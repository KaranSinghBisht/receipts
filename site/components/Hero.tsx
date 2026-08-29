import { Button } from "./ui";

/** The product shot is the live dashboard in a macOS window, not a mockup and
 *  not a screenshot: if the audit changes, so does the picture.
 *
 *  The backdrop is composited in CSS. Drop a file at public/hero-bg.jpg and it
 *  is used instead — see .stage in globals.css. */
function Stage({ art }: { art: string | null }) {
  return (
    <div
      className="stage relative overflow-hidden px-4 pt-8 pb-0 sm:px-10 sm:pt-14"
      style={art ? { backgroundImage: `url(${art})` } : undefined}
    >
      <div className="mx-auto max-w-[1080px] overflow-hidden rounded-t-xl bg-[#FBFBFA] shadow-[0_40px_90px_-30px_rgba(12,14,20,0.55)] ring-1 ring-black/10">
        <div className="flex items-center gap-2 border-b border-black/8 bg-[#EFEFED] px-4 py-3">
          <span aria-hidden className="h-[11px] w-[11px] rounded-full bg-[#FF5F57]" />
          <span aria-hidden className="h-[11px] w-[11px] rounded-full bg-[#FEBC2E]" />
          <span aria-hidden className="h-[11px] w-[11px] rounded-full bg-[#28C840]" />
          <span className="mx-auto flex items-center gap-1.5 rounded-md bg-white/85 px-3 py-1 font-mono text-[11px] text-ink-3">
            <span aria-hidden className="text-[9px]">&#128274;</span>
            receipts &mdash; nightly audit
          </span>
        </div>
        <iframe
          src="/report.html"
          title="The live Receipts audit"
          loading="lazy"
          className="h-[560px] w-full border-0 bg-white"
        />
      </div>
    </div>
  );
}

export function Hero({
  repo,
  diverged,
  runs,
  art,
}: {
  repo: string;
  diverged: number;
  runs: number;
  art: string | null;
}) {
  return (
    <div id="top" className="border-b border-rule">
      <div className="px-6 pt-20 pb-0 md:pt-24">
        <h1 className="display mx-auto max-w-[17ch] text-center text-[2.6rem] sm:text-[3.6rem]">
          Your agent says the tests pass
        </h1>
        <p className="mx-auto mt-6 max-w-[60ch] text-center text-[17px] leading-[1.6] text-ink-2">
          Receipts holds that sentence to the agent&rsquo;s own execution trace &mdash;
          the files it wrote, the commands it ran, what those commands printed &mdash;
          and cites the line that settles it.
        </p>

        <div className="mt-9 flex flex-wrap justify-center gap-3">
          <Button href="/report.html">Open the live report &rarr;</Button>
          <Button href={repo} variant="quiet">
            Read the source
          </Button>
        </div>

        <p className="gutter mt-7 text-center">
          {diverged} of {runs} real agent runs claimed something their trace does not
          support
        </p>

        <div className="mt-14">
          <Stage art={art} />
        </div>
      </div>
    </div>
  );
}
