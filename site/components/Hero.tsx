import { Button } from "./ui";

/** Floating product objects, ChronoTask-style — except every one of them is a
 *  real artefact from the study, not decoration. */
function Chips() {
  return (
    <div aria-hidden className="pointer-events-none absolute inset-0 hidden xl:block">
      <div className="float-chip drift absolute top-[86px] left-[max(1.5rem,calc(50%-620px))] w-[228px] p-4" style={{ "--tilt": "-5deg" } as React.CSSProperties}>
        <p className="font-mono text-[9.5px] tracking-[0.1em] text-warn uppercase">
          medium
        </p>
        <p className="mt-1.5 text-[13px] leading-snug font-medium">
          Claimed the change works, but never ran the tests
        </p>
      </div>
      <div className="float-chip drift absolute top-[300px] left-[max(0.5rem,calc(50%-660px))] p-4" style={{ "--tilt": "3deg", animationDelay: "-2s" } as React.CSSProperties}>
        <p className="font-mono text-[11.5px] text-ink-2">
          <span className="text-ink-3">$</span> sed -n &apos;28p&apos; trace.ndjson
        </p>
        <p className="mt-1 font-mono text-[10px] text-ink-3">
          every finding cites a real line
        </p>
      </div>
      <div className="float-chip drift absolute top-[92px] right-[max(1.5rem,calc(50%-620px))] p-4 text-center" style={{ "--tilt": "4deg", animationDelay: "-4s" } as React.CSSProperties}>
        <p className="font-mono text-[1.6rem] leading-none font-semibold text-good tnum">
          0<span className="text-[1rem]">/18</span>
        </p>
        <p className="gutter mt-1.5">false alarms</p>
      </div>
      <div className="float-chip drift absolute top-[295px] right-[max(1rem,calc(50%-640px))] w-[212px] p-4" style={{ "--tilt": "-3deg", animationDelay: "-5.5s" } as React.CSSProperties}>
        <p className="flex items-center gap-2 font-mono text-[11px] text-signal">
          <span aria-hidden className="h-[7px] w-[7px] rounded-full bg-signal" />
          diverged 3/3
        </p>
        <p className="mt-1.5 text-[12.5px] leading-snug text-ink-2">
          Bob skipped the suite on the same task, three runs out of three
        </p>
      </div>
    </div>
  );
}

function Stage({ art }: { art: string | null }) {
  return (
    <div
      className="relative overflow-hidden rounded-[28px] border border-rule bg-terminal px-6 pt-12 shadow-[0_30px_80px_-30px_rgba(21,23,28,0.45)] sm:px-16 sm:pt-16 lg:px-24"
      style={
        art
          ? {
              backgroundImage: `url(${art})`,
              backgroundSize: "cover",
              backgroundPosition: "center",
            }
          : undefined
      }
    >
      <a
        href="/dashboard"
        aria-label="Open the dashboard"
        className="group relative mx-auto block max-w-[880px] overflow-hidden rounded-t-2xl bg-[#FBFBFA] shadow-[0_40px_90px_-30px_rgba(12,14,20,0.6)] ring-1 ring-black/10"
      >
        <div className="flex items-center gap-2 border-b border-black/8 bg-[#EFEFED] px-4 py-3">
          <span aria-hidden className="h-[11px] w-[11px] rounded-full bg-[#FF5F57]" />
          <span aria-hidden className="h-[11px] w-[11px] rounded-full bg-[#FEBC2E]" />
          <span aria-hidden className="h-[11px] w-[11px] rounded-full bg-[#28C840]" />
          <span className="mx-auto flex items-center gap-1.5 rounded-md bg-white/85 px-3 py-1 font-mono text-[11px] text-ink-3">
            <span aria-hidden className="text-[9px]">&#128274;</span>
            receipts &mdash; nightly audit
          </span>
        </div>
        {/* pointer-events off: the preview must not trap the page scroll */}
        <iframe
          src="/dashboard"
          title="The live Receipts dashboard"
          loading="lazy"
          tabIndex={-1}
          className="pointer-events-none h-[440px] w-full border-0 bg-white"
        />
        <span className="pointer-events-none absolute inset-x-0 bottom-0 flex justify-center bg-gradient-to-t from-black/25 to-transparent pt-14 pb-5 opacity-0 transition group-hover:opacity-100">
          <span className="rounded-full bg-white px-5 py-2 text-[13.5px] font-medium shadow-lg">
            Open the dashboard &rarr;
          </span>
        </span>
      </a>
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
    <div id="top" className="relative isolate overflow-x-clip px-5 pt-16 sm:px-8 md:pt-20">
      <div aria-hidden className="blob top-[-80px] left-[8%] h-[380px] w-[380px] bg-accent/14" />
      <div aria-hidden className="blob top-[120px] right-[6%] h-[320px] w-[320px] bg-good/12" />
      <div aria-hidden className="blob top-[440px] left-[42%] h-[300px] w-[420px] bg-signal/8" />
      <div
        aria-hidden
        className="gridfield absolute inset-x-0 top-0 -z-10 h-[520px] [mask-image:linear-gradient(to_bottom,black,transparent)]"
      />
      <Chips />
      <div className="mx-auto max-w-[1120px]">
        <div className="rise flex justify-center">
          <span className="pill-label">
            <span aria-hidden className="pulse-dot h-[6px] w-[6px] rounded-full bg-good" />
            {diverged} of {runs} real runs diverged &middot; 0 false alarms
          </span>
        </div>
        <h1
          className="display rise mx-auto mt-6 max-w-[15ch] text-center text-[2.7rem] sm:text-[3.8rem]"
          style={{ animationDelay: "90ms" }}
        >
          Your agent says the tests pass
        </h1>
        <p
          className="rise mx-auto mt-6 max-w-[56ch] text-center text-[17px] leading-[1.65] text-ink-2"
          style={{ animationDelay: "180ms" }}
        >
          Receipts holds that sentence to the agent&rsquo;s own execution trace &mdash;
          the files it wrote, the commands it ran, what those commands printed &mdash;
          and cites the line that settles it.
        </p>
        <div
          className="rise mt-9 flex flex-wrap justify-center gap-3"
          style={{ animationDelay: "260ms" }}
        >
          <Button href="/dashboard">Open the dashboard &rarr;</Button>
          <Button href={repo} variant="quiet">
            Read the source
          </Button>
        </div>
        <div className="rise mt-14" style={{ animationDelay: "360ms" }}>
          <Stage art={art} />
        </div>
      </div>
    </div>
  );
}
