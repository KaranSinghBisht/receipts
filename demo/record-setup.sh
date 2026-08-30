#!/usr/bin/env bash
# One command to a recording-ready desk: deps, board, browser tabs, Bob IDE.
# Run it once before filming. Between takes: ./demo/reset.sh && ./demo/run.sh
set -euo pipefail
cd "$(dirname "$0")/.."

if [ -z "${BOB_API_KEY:-}" ]; then
  printf '\033[1;33m%s\033[0m\n' \
    "warning: BOB_API_KEY not set in this shell — run.sh will refuse until it is (Bob IDE -> API Keys)"
fi

step() { printf '\033[1;34m%s\033[0m\n' "$*"; }

step "1/5 dependencies"
uv sync --frozen
export PATH="$PWD/.venv/bin:$PATH"
receipts --version

step "2/5 clear the board"
./demo/reset.sh

step "3/5 live board on :7878"
pkill -f "receipts demo/traces" 2>/dev/null || true
WATCH_LOG="${TMPDIR:-/tmp}/receipts-watch.log"
nohup receipts demo/traces --watch >"$WATCH_LOG" 2>&1 &
disown
if ! curl -s --retry 15 --retry-delay 1 --retry-all-errors -o /dev/null http://127.0.0.1:7878; then
  echo "board did not come up; log tail:" >&2
  tail -5 "$WATCH_LOG" >&2
  exit 1
fi
echo "board serving at http://127.0.0.1:7878 (log: $WATCH_LOG)"

step "4/5 browser tabs, in script order"
for url in \
  "https://receipts-bob.vercel.app" \
  "http://127.0.0.1:7878" \
  "https://receipts-bob.vercel.app/dashboard" \
  "https://receipts-bob.vercel.app/dashboard/study" \
  "https://receipts-bob.vercel.app/dashboard/graph"; do
  open "$url"
done

step "5/5 Bob IDE"
open -a "IBM Bob" || echo "open Bob IDE manually (Tasks panel visible)"

cat <<'CHECKLIST'

ready to record —
  layout   browser left ~60%, terminal right, font 16pt+
  take     ./demo/run.sh          (~25s; if the board card stays clean:
           ./demo/reset.sh and go again — a diverged take is a real run)
  never    the BOB_API_KEY pane, ~/.receipts/auth.json, account pages
  after    ./demo/reset.sh; pkill -f "receipts demo/traces"
CHECKLIST
