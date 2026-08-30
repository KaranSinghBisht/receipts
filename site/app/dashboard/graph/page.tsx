import { PageHead } from "@/components/dash";

import { GraphView } from "./GraphView";

export const metadata = { title: "Graph — Receipts" };

export default function GraphPage() {
  return (
    <>
      <PageHead
        title="The audit as a shape"
        sub="Every run, clustered around its task. A clean run stays in its ring; a diverged run is pulled toward the finding that fired on it — so shared causes show up as shared geometry, before you read a single line."
      />
      <GraphView />
    </>
  );
}
