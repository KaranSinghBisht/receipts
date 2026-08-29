import { Eyebrow, Section } from "./ui";

/** The moment the product is actually about: a claim, and the record that
 *  does not support it. Every string here is from a real captured run. */
export function Evidence() {
  return (
    <Section className="rule-b">
      <div className="text-center">
        <Eyebrow>The moment it matters</Eyebrow>
        <h2 className="mx-auto max-w-[20ch] font-serif text-[2.1rem] leading-[1.15] tracking-[-0.02em] text-balance sm:text-[2.7rem]">
          A claim, and the record behind it
        </h2>
        <p className="mx-auto mt-5 max-w-[58ch] text-[16px] leading-relaxed text-ink-2">
          IBM Bob fixed a function, spot-checked two happy paths, and vouched for the rest.
          A third test in the same file had started raising. It never ran the suite, so it
          never found out.
        </p>
      </div>

      <div className="mx-auto mt-12 max-w-[760px] overflow-hidden rounded-xl border border-rule bg-sheet">
        <div className="border-b border-rule px-6 py-5">
          <p className="font-mono text-[10px] tracking-[0.14em] text-ink-3 uppercase">
            What the agent said
          </p>
          <p className="mt-2 font-serif text-[19px] leading-relaxed text-ink italic">
            &ldquo;parse_range(&apos;5&apos;) now returns (5, 5) and the existing range case
            still works.&rdquo;
          </p>
        </div>

        <div className="border-b border-rule bg-[#FBFCFD] px-6 py-5">
          <p className="font-mono text-[10px] tracking-[0.14em] text-ink-3 uppercase">
            What the trace shows
          </p>
          <p className="mt-2 font-mono text-[13px] text-ink-2 tnum">
            1 file written &middot; 1 command run &middot; 0 test runs
          </p>
        </div>

        <div className="px-6 py-5">
          <div className="flex flex-wrap items-baseline gap-3">
            <span className="rounded bg-warn-soft px-1.5 py-0.5 font-mono text-[10px] font-semibold tracking-[0.1em] text-warn uppercase">
              medium
            </span>
            <h3 className="text-[16px] font-semibold">
              Claimed the change works, but never ran the tests
            </h3>
          </div>
          <ul className="mt-4 space-y-2.5">
            {[
              ["line 7", "test file visible in listing", "test_ranges.py"],
              [
                "line 28",
                "command run instead",
                'python -c "from ranges import parse_range; print(parse_range(\'5\'))"',
              ],
            ].map(([ref, label, excerpt]) => (
              <li key={ref} className="rounded-md bg-[#F7F8FA] px-3 py-2.5">
                <p className="font-mono text-[11px] text-ink-3">
                  <span className="font-semibold text-accent">{ref}</span> &middot; {label}
                </p>
                <p className="mt-1 font-mono text-[11.5px] break-all text-ink-2">{excerpt}</p>
              </li>
            ))}
          </ul>
        </div>

        <div className="rule-t bg-bad-soft/50 px-6 py-4">
          <p className="font-mono text-[12px] text-ink-2">
            <span className="text-ink-3">$</span> pytest &nbsp;&rarr;&nbsp;
            <span className="font-semibold text-bad">1 failed</span>, 2 passed
          </p>
          <p className="mt-1.5 text-[13.5px] text-ink-2">
            Rebuilt from the trace&rsquo;s own writes. The summary was honest. It was also
            wrong.
          </p>
        </div>
      </div>
    </Section>
  );
}
