import { Eyebrow, Section } from "./ui";

const FOUND = [
  {
    title: "IBM Bob drops most of its own tool calls",
    body: "Its stream renderer dedupes on the assistant message id and appends each new call to the same message, so only the first call of a turn is reported while every result still arrives — 35 of 68 calls in this corpus. Receipts had been auditing less than half of every run.",
  },
  {
    title: "Two findings were false positives, and Bob caught them",
    body: "Parallel trace-auditor subagents came back saying Receipts was wrong, with the trace lines to prove it. A test file had been written; a verification had run. Detections fell from three to two, and we published the lower number.",
  },
  {
    title: "It punished the more careful agent",
    body: "Claude Code rebuilt the original buggy source in a scratch directory to prove its new tests catch the bug. Four failures — the entire point of the exercise. Receipts called that a divergence until it learned to tell an experiment from a verification.",
  },
  {
    title: "Our own read-only claim was false",
    body: "The auditor mode withheld the edit tool and the config said it therefore could not modify what it audits. It could, through the shell. An unverified claim about separation of duties, in the configuration of a tool built to catch unverified claims.",
  },
];

export function Reflexive() {
  return (
    <Section className="rule-b">
      <div className="grid gap-12 md:grid-cols-[minmax(0,26ch)_1fr]">
        <div>
          <Eyebrow>Applied to ourselves</Eyebrow>
          <h2 className="font-serif text-[2rem] leading-[1.12] tracking-[-0.02em] text-balance">
            What it found in its own build
          </h2>
          <p className="mt-5 text-[15px] leading-relaxed text-ink-2">
            Every one of these was invisible until a real trace produced it. They are on the
            site for the same reason they are in the README: a tool that asks agents to show
            their receipts has to show its own.
          </p>
        </div>

        <ul>
          {FOUND.map((f) => (
            <li key={f.title} className="border-t border-rule py-6 first:border-t-0 first:pt-0">
              <h3 className="text-[16px] font-semibold text-ink">{f.title}</h3>
              <p className="mt-2 text-[14.5px] leading-relaxed text-ink-2">{f.body}</p>
            </li>
          ))}
        </ul>
      </div>
    </Section>
  );
}
