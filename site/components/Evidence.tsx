import { Section } from "./ui";

export function Evidence() {
  return (
    <Section
      label="The moment it matters"
      title="It broke a test, then vouched for the change"
      lede="A real IBM Bob run — and not a rare one: on this task Bob skipped the suite in three runs out of three. It fixed the reported bug, spot-checked two happy paths, and reported success. A third test had started raising. It never ran the suite, so it never found out."
    >
      <div className="soft-card mx-auto mt-12 max-w-[780px] overflow-hidden">
        <div className="flex flex-wrap items-baseline gap-x-3 gap-y-2 border-b border-rule px-7 py-5">
          <span className="rounded-full bg-warn-soft px-2.5 py-1 font-mono text-[10px] font-semibold tracking-[0.08em] text-warn uppercase">
            medium
          </span>
          <h3 className="text-[16.5px] font-semibold">
            Claimed the change works, but never ran the tests
          </h3>
        </div>
        <dl className="divide-y divide-rule-soft">
          {[
            [
              "line 7",
              "test file visible in listing",
              "Directory listing for .:  ranges.py  test_ranges.py",
            ],
            [
              "line 28",
              "command run instead",
              "python -c \"from ranges import parse_range; print(parse_range('5'))\"",
            ],
          ].map(([ref, label, excerpt]) => (
            <div key={ref} className="px-7 py-4">
              <dt className="font-mono text-[11px] text-ink-3">
                <span className="font-semibold text-accent">{ref}</span> &middot; {label}
              </dt>
              <dd className="mt-1.5 overflow-x-auto rounded-lg bg-panel px-3 py-2 font-mono text-[12px] whitespace-pre-wrap text-ink-2">
                {excerpt}
              </dd>
            </div>
          ))}
        </dl>
        <div className="border-t border-rule bg-signal-soft/60 px-7 py-5">
          <p className="font-mono text-[12.5px] text-ink-2">
            <span className="text-ink-3">$</span> pytest &nbsp;&rarr;&nbsp;
            <span className="font-semibold text-signal">1 failed</span>, 2 passed
          </p>
          <p className="mt-2 max-w-[58ch] text-[14px] leading-relaxed text-ink-2">
            Rebuilt from the trace&rsquo;s own writes, so this is what that run actually
            left behind. The summary was honest. It was also wrong.
          </p>
        </div>
      </div>
    </Section>
  );
}
