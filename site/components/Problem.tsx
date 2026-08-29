import { Display, Section } from "./ui";

const POINTS = [
  "Agents write their own summary, and the summary is what lands in review.",
  "A summary that reads correct can rest on nothing that was actually run.",
  "After two hundred accurate summaries, the two hundred and first reads the same.",
  "The trace that would settle it is thousands of lines nobody opens.",
  "A second model reviewing the first adds a second set of hallucinations.",
  "Continuous integration cannot fail a build on a suspicion.",
];

export function Problem() {
  return (
    <Section id="problem" className="rule-b">
      <Display
        lead="The summary is the only thing anyone reads."
        rest="It comes from the same system that did the work, from its own recollection of doing it, and it is almost always true. That is what makes it dangerous."
      />

      <ul className="mt-14 grid gap-x-12 sm:grid-cols-2">
        {POINTS.map((point, i) => (
          <li
            key={point}
            className="grid grid-cols-[28px_1fr] gap-4 border-t border-rule py-6"
          >
            <span className="font-mono text-[11px] text-accent tnum">
              {String(i + 1).padStart(2, "0")}
            </span>
            <p className="text-[15.5px] leading-relaxed text-ink-2">{point}</p>
          </li>
        ))}
      </ul>
    </Section>
  );
}
