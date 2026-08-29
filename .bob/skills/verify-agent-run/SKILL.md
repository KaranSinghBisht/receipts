---
name: verify-agent-run
description: >-
  Check a completed agent task against its execution trace before the change goes to review.
  Use when a Bob run has finished and you want to know whether its summary matches what it
  actually did.
---

Verify an agent run against the facts in its own trace.

<Steps>
<Step>
Locate the trace for the run. If one was not captured, re-run the task with
`bob run --format stream-json "<task>" > trace.ndjson`.
A directory of traces works too: `receipts traces/ --html report.html`.
</Step>
<Step>
Run `receipts trace.ndjson --html receipts.html` and read the findings.
</Step>
<Step>
For each finding, open the cited event indexes in the trace and confirm the evidence
supports the claim. Report any finding you cannot substantiate as a false positive
rather than passing it on.
</Step>
<Step>
Summarise for the reviewer:
- the agent's claim, quoted
- what the trace shows actually happened
- each divergence, with its evidence
- a recommendation: accept, or return with specific questions

Do not modify the code under audit.
</Step>
</Steps>
