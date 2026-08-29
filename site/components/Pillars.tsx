import { Section, Verdict } from "./ui";

function TraceArt() {
  return (
    <div className="dotfield flex h-[190px] items-center justify-center border-b border-rule px-6">
      <div className="w-full max-w-[260px] space-y-2">
        {[
          ["write", "pricing.py", false],
          ["run", "python -c ...", false],
          ["run", "pytest -q", true],
        ].map(([kind, detail, flagged]) => (
          <div
            key={detail as string}
            className={`flex items-center gap-3 rounded-md border px-3 py-2 ${
              flagged ? "border-bad/30 bg-bad-soft" : "border-rule bg-white"
            }`}
          >
            <span
              aria-hidden
              className={`h-[6px] w-[6px] rounded-full ${flagged ? "bg-bad" : "bg-ink-3/40"}`}
            />
            <span className="font-mono text-[11px] text-ink-3">{kind}</span>
            <span className="truncate font-mono text-[11px] text-ink">{detail}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function CitationArt() {
  return (
    <div className="dotfield flex h-[190px] items-center justify-center border-b border-rule px-6">
      <div className="w-full max-w-[280px] rounded-md border border-rule bg-white p-3">
        <p className="font-mono text-[11px] text-accent">line 28</p>
        <p className="mt-1.5 font-mono text-[11px] leading-relaxed text-ink-2">
          {'{"type":"tool_use","tool_name":'}
          <br />
          {'"execute_command"...'}
        </p>
        <p className="mt-2.5 border-t border-rule-soft pt-2 font-mono text-[10px] text-ink-3">
          $ sed -n &apos;28p&apos; trace.ndjson
        </p>
      </div>
    </div>
  );
}

function SpecArt() {
  return (
    <div className="dotfield flex h-[190px] items-center justify-center border-b border-rule px-6">
      <div className="w-full max-w-[280px] space-y-2">
        <div className="rounded-md border border-rule bg-white px-3 py-2">
          <p className="font-mono text-[10px] tracking-[0.1em] text-ink-3 uppercase">
            SPEC.md:8
          </p>
          <p className="mt-1 text-[12.5px] text-ink">
            Input that is not a number MUST return <code className="font-mono">None</code>.
          </p>
        </div>
        <div className="flex items-center justify-center">
          <span aria-hidden className="font-mono text-[13px] text-ink-3">
            &darr;
          </span>
        </div>
        <div className="flex items-center justify-between rounded-md border border-rule bg-white px-3 py-2">
          <span className="font-mono text-[11px] text-ink-2">R4 &middot; never confirmed</span>
          <Verdict value="diverged" />
        </div>
      </div>
    </div>
  );
}

const PILLARS = [
  {
    art: <TraceArt />,
    title: "Ground truth, not a second opinion",
    body: "The verdict is a function of the trace. Same trace, same verdict, forever, for nothing — no second model grading the first, and no answer that changes each time you ask.",
  },
  {
    art: <CitationArt />,
    title: "Every finding cites its line",
    body: "Findings point at a real 1-based line in the trace file. Pipe it through sed and the record comes back. The tool is checkable rather than trusted, which is the property it demands of the agent.",
  },
  {
    art: <SpecArt />,
    title: "Held to the ticket, not just the summary",
    body: "IBM Bob reads the spec and turns it into structured requirements. Receipts checks those against the trace. Bob decides what the document says; the machine decides what the trace shows.",
  },
];

export function Pillars() {
  return (
    <Section className="rule-b">
      <p className="text-center font-serif text-[1.9rem] tracking-[-0.02em] text-balance sm:text-[2.3rem]">
        Receipts gives an agent run a paper trail
      </p>
      <div className="mt-12 grid gap-5 md:grid-cols-3">
        {PILLARS.map((p) => (
          <article
            key={p.title}
            className="overflow-hidden rounded-xl border border-rule bg-sheet"
          >
            {p.art}
            <div className="p-6">
              <h3 className="font-serif text-[1.3rem] leading-snug tracking-[-0.01em]">
                {p.title}
              </h3>
              <p className="mt-2.5 text-[14.5px] leading-relaxed text-ink-2">{p.body}</p>
            </div>
          </article>
        ))}
      </div>
    </Section>
  );
}
