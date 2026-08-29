import { Heading, Lede, Row } from "./ui";

/** The thesis, shown as the thing itself: what a reviewer reads on the left,
 *  what the machine can check on the right. */
export function Problem() {
  return (
    <Row id="problem" line="L02" label="the problem">
      <Heading>The summary is the only thing anyone reads</Heading>
      <Lede>
        It comes from the same system that did the work, written from its own
        recollection of doing it. It is almost always true, and that is exactly what
        makes it dangerous: after two hundred accurate summaries, the two hundred and
        first reads the same.
      </Lede>

      <div className="mt-12 grid gap-px overflow-hidden border border-rule bg-rule md:grid-cols-2">
        <div className="bg-paper p-7">
          <p className="gutter mb-4">what lands in review</p>
          <p className="font-quote text-[19px] leading-[1.6] text-ink">
            &ldquo;Fixed. The change is in parse_range: when no hyphen is present it now
            parses the value as a single number and returns it as both bounds. Both cases
            work correctly.&rdquo;
          </p>
          <p className="mt-6 text-[14px] leading-relaxed text-ink-3">
            Eight lines. Confident, specific, and written by the author of the change.
          </p>
        </div>

        <div className="bg-panel p-7">
          <p className="gutter mb-4">what the record says</p>
          <ul className="space-y-2.5 font-mono text-[12.5px] text-ink-2">
            <li className="flex gap-3">
              <span className="text-ink-3">L07</span>
              <span>listing shows test_ranges.py exists</span>
            </li>
            <li className="flex gap-3">
              <span className="text-ink-3">L22</span>
              <span>write ranges.py</span>
            </li>
            <li className="flex gap-3">
              <span className="text-ink-3">L28</span>
              <span>run python -c &quot;...&quot;</span>
            </li>
            <li className="flex gap-3 text-signal">
              <span className="opacity-60">&mdash;&mdash;</span>
              <span className="font-semibold">no test run, anywhere</span>
            </li>
          </ul>
          <p className="mt-6 text-[14px] leading-relaxed text-ink-3">
            Fifty-three events. Nobody opens it, and nothing in review requires anyone to.
          </p>
        </div>
      </div>
    </Row>
  );
}
