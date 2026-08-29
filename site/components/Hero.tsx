import { Button } from "./ui";

/** The product shot is the real dashboard in an iframe, not a mockup. If the
 *  audit changes, the picture on the landing page changes with it. */
function BrowserFrame({ src }: { src: string }) {
  return (
    <div className="overflow-hidden rounded-xl border border-rule bg-sheet shadow-[0_24px_60px_-30px_rgba(20,22,27,0.35)]">
      <div className="flex items-center gap-2 border-b border-rule bg-[#FAFBFC] px-4 py-2.5">
        <span aria-hidden className="h-[10px] w-[10px] rounded-full bg-[#E1E4E9]" />
        <span aria-hidden className="h-[10px] w-[10px] rounded-full bg-[#E1E4E9]" />
        <span aria-hidden className="h-[10px] w-[10px] rounded-full bg-[#E1E4E9]" />
        <span className="mx-auto rounded-md bg-white px-3 py-1 font-mono text-[11px] text-ink-3">
          receipts / audit
        </span>
      </div>
      <iframe
        src={src}
        title="The live audit report"
        loading="lazy"
        className="h-[520px] w-full border-0 bg-white"
      />
    </div>
  );
}

export function Hero({ repo, diverged, runs }: { repo: string; diverged: number; runs: number }) {
  return (
    <div id="top" className="px-6 pt-20 pb-14 sm:px-12 md:px-16">
      <h1 className="mx-auto max-w-[19ch] text-center font-serif text-[2.4rem] leading-[1.08] tracking-[-0.025em] text-balance sm:text-[3.4rem]">
        Your agent says the tests pass
      </h1>
      <p className="mx-auto mt-6 max-w-[62ch] text-center text-[17px] leading-relaxed text-ink-2">
        Receipts holds that sentence to the agent&rsquo;s own execution trace &mdash; the
        files it wrote, the commands it ran, and what those commands printed &mdash; then
        cites the line of the trace that settles it.
      </p>

      <div className="mt-9 flex flex-wrap justify-center gap-3">
        <Button href="/report.html">Open the live report &rarr;</Button>
        <Button href={repo} variant="quiet">
          Read the source
        </Button>
      </div>

      <p className="mt-5 text-center font-mono text-[11px] tracking-[0.08em] text-ink-3 uppercase">
        {diverged} of {runs} real agent runs claimed something their trace does not support
      </p>

      <div className="mt-14">
        <BrowserFrame src="/report.html" />
      </div>
    </div>
  );
}
