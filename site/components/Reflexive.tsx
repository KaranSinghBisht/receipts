import { Section } from "./ui";

const FOUND = [
  [
    "IBM Bob drops most of its own tool calls",
    "Its stream renderer dedupes on the assistant message id and appends each new call to the same message, so only the first call of a turn is reported while every result still arrives — 106 of 194 calls across the current Bob corpus. Receipts had been auditing less than half of every run.",
  ],
  [
    "Two findings were false positives, and Bob caught them",
    "Parallel trace-auditor subagents came back saying Receipts was wrong, with the trace lines to prove it. A test file had been written; a verification had run. Detections fell from three to two, and the lower number is the one published.",
  ],
  [
    "It punished the more careful agent",
    "Claude Code rebuilt the original buggy source in a scratch directory to prove its new tests catch the bug. Four failures — the entire point. Receipts called that a divergence until it learned to tell an experiment from a verification.",
  ],
  [
    "Our own read-only claim was false",
    "The auditor mode withholds the edit tool, and the config said it therefore could not modify what it audits. It could, through the shell. An unverified claim about separation of duties, in the configuration of a tool built to catch unverified claims.",
  ],
];

export function Reflexive() {
  return (
    <Section
      label="Applied to itself"
      title="What it found in its own build"
      lede="Every one of these was invisible until a real trace produced it. They are on the site for the same reason they are in the README: a tool demanding receipts has to show its own."
    >
      <div className="mt-12 grid gap-5 sm:grid-cols-2">
        {FOUND.map(([title, body]) => (
          <article key={title} className="soft-card p-7">
            <h3 className="text-[15.5px] font-semibold tracking-[-0.01em]">{title}</h3>
            <p className="mt-2.5 text-[14px] leading-relaxed text-ink-2">{body}</p>
          </article>
        ))}
      </div>
    </Section>
  );
}
