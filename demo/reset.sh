#!/usr/bin/env bash
# Clear the watched directory so the board goes back to "waiting for the first
# trace". Run this between takes.
set -euo pipefail
cd "$(dirname "$0")/.."
rm -f demo/traces/*.ndjson
echo "demo reset — board is empty"
