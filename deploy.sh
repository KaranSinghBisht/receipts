#!/usr/bin/env bash
# Rebuild the site from the corpora and publish it.
#
#   ./deploy.sh
#
# Every figure on the landing page is filled in at build time, so publishing is
# how the site stays true rather than something that can drift from the study.

set -euo pipefail
cd "$(dirname "$0")"

SCOPE="${VERCEL_SCOPE:-karan-singh-bishts-projects-3b89b238}"
OUT="$(mktemp -d)/receipts"
trap 'rm -rf "$(dirname "$OUT")"' EXIT

python3 study/build_pages.py --out "$OUT"
(cd "$OUT" && vercel deploy --prod --yes --scope "$SCOPE")

echo
echo "https://receipts-tawny-six.vercel.app"
