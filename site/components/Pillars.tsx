import { Section } from "./ui";

const STEPS = [
  {
    n: "01",
    title: "The agent works, the trace is kept",
    body: "One flag on the command you already run. The NDJSON it emits is the only input Receipts ever takes.",
    code: "bob run --format stream-json … > t.ndjson",
  },
  {
    n: "02",
    title: "The claim is held to the record",
    body: "Ground truth is rebuilt from the trace and the closing summary is checked against it. No second model, no opinion, no per-review cost.",
    code: "receipts t.ndjson --fail-on high",
  },
  {
    n: "03",
    title: "Findings cite lines you can open",
    body: "A finding names the 1-based line of the trace it rests on. Pipe it out of the file and the record comes back.",
    code: "sed -n '28p' t.ndjson",
  },
  {
    n: "04",
    title: "With a ticket, it checks that too",
    body: "IBM Bob reads the spec into structured requirements; the machine checks them against the trace. Bob decides what the document says — never whether the work was good.",
    code: "receipts t.ndjson --spec requirements.json",
  },
];

export function Pillars() {
  return (
    <Section
      label="How it runs"
      title="Four steps, and none of them is a model grading another model"
      lede="A verdict is a function of the trace. The same trace gives the same verdict, every time, for nothing."
    >
      <div className="mt-12 grid gap-5 sm:grid-cols-2">
        {STEPS.map((s) => (
          <article key={s.n} className="soft-card flex flex-col p-7">
            <div className="flex items-baseline gap-3">
              <span className="rounded-full bg-accent-soft px-2.5 py-1 font-mono text-[10.5px] font-semibold text-accent">
                {s.n}
              </span>
              <h3 className="text-[17px] font-semibold tracking-[-0.01em]">{s.title}</h3>
            </div>
            <p className="mt-3 text-[14.5px] leading-relaxed text-ink-2">{s.body}</p>
            <p className="mt-auto overflow-x-auto rounded-xl bg-panel px-4 py-3 pt-3 font-mono text-[12px] whitespace-pre text-ink-2">
              <span className="text-ink-3">$ </span>
              {s.code}
            </p>
          </article>
        ))}
      </div>
    </Section>
  );
}
