import { Heading, Lede, Row } from "./ui";

const STOPS = [
  {
    n: "01",
    title: "The agent works, and the trace is kept",
    body: "One flag on the command you already run. The NDJSON it emits is the only input Receipts ever takes.",
    code: "bob run --format stream-json \"fix parse_range\" > traces/t.ndjson",
  },
  {
    n: "02",
    title: "The claim is held to the record",
    body: "Ground truth is reconstructed from the trace — every file written, every command run, everything those commands printed — and the closing summary is checked against it. No second model, no opinion, no per-review cost.",
    code: "receipts traces/t.ndjson --fail-on high",
  },
  {
    n: "03",
    title: "Findings cite lines you can open",
    body: "A finding names the 1-based line of the trace it rests on. Pipe that line out of the file and the record comes back. A tool asking agents to show their receipts has to show its own.",
    code: "sed -n '28p' traces/t.ndjson",
  },
  {
    n: "04",
    title: "With a ticket in hand, it checks that too",
    body: "IBM Bob reads the spec and turns it into structured requirements. Receipts checks those against the trace. Bob decides what the document says; the machine decides what the trace shows.",
    code: "receipts traces/t.ndjson --spec requirements.json",
  },
];

export function Pillars() {
  return (
    <Row line="L03" label="how it runs">
      <Heading>Four steps, and none of them is a model grading another model</Heading>
      <Lede>
        A verdict is a function of the trace. The same trace gives the same verdict,
        every time, for nothing.
      </Lede>

      <ol className="mt-12">
        {STOPS.map((s) => (
          <li
            key={s.n}
            className="grid grid-cols-[34px_1fr] gap-x-5 border-t border-rule py-8 last:border-b"
          >
            <span className="gutter pt-1">{s.n}</span>
            <div className="min-w-0">
              <h3 className="text-[17px] font-semibold tracking-[-0.01em]">{s.title}</h3>
              <p className="mt-2 max-w-[60ch] text-[14.5px] leading-relaxed text-ink-2">
                {s.body}
              </p>
              <p className="mt-4 overflow-x-auto bg-panel-2 px-3.5 py-2.5 font-mono text-[12px] whitespace-pre text-ink-2">
                <span className="text-ink-3">$ </span>
                {s.code}
              </p>
            </div>
          </li>
        ))}
      </ol>
    </Row>
  );
}
