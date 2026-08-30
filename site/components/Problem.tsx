import { Section } from "./ui";

export function Problem() {
  return (
    <Section
      id="problem"
      label="The problem"
      title="The summary is the only thing anyone reads"
      lede="It comes from the same system that did the work, written from its own recollection of doing it. It is almost always true — and that is exactly what makes it dangerous: after two hundred accurate summaries, the two hundred and first reads the same."
    >
      <div className="soft-card mt-12 overflow-hidden">
        <div className="grid md:grid-cols-2">
          <div className="p-8">
            <p className="gutter mb-4 uppercase">what lands in review</p>
            <p className="font-quote text-[19px] leading-[1.65] text-ink italic">
              &ldquo;Fixed. The change is in parse_range: when no hyphen is present it
              now parses the value as a single number and returns it as both bounds.
              Both cases work correctly.&rdquo;
            </p>
            <p className="mt-6 text-[14px] leading-relaxed text-ink-3">
              Eight lines. Confident, specific, written by the author of the change.
            </p>
          </div>
          <div className="dotfield border-t border-rule p-8 md:border-t-0 md:border-l">
            <p className="gutter mb-4 uppercase">what the record says</p>
            <ul className="space-y-3">
              {[
                ["L07", "listing shows test_ranges.py exists", false],
                ["L22", "write ranges.py", false],
                ["L28", "run python -c …", false],
                ["—", "no test run, anywhere", true],
              ].map(([ref, text, hot]) => (
                <li
                  key={ref as string}
                  className={`flex items-center gap-3 rounded-xl border bg-card px-4 py-2.5 font-mono text-[12.5px] ${
                    hot
                      ? "border-signal/30 font-semibold text-signal"
                      : "border-rule text-ink-2"
                  }`}
                >
                  <span className={hot ? "opacity-60" : "text-ink-3"}>{ref}</span>
                  <span>{text}</span>
                </li>
              ))}
            </ul>
            <p className="mt-6 text-[14px] leading-relaxed text-ink-3">
              Fifty-three events. Nobody opens it, and nothing in review requires anyone
              to.
            </p>
          </div>
        </div>
      </div>
    </Section>
  );
}
