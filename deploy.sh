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
DOMAIN="${RECEIPTS_DOMAIN:-receipts-bob.vercel.app}"
OUT="$(mktemp -d)/receipts"
trap 'rm -rf "$(dirname "$OUT")"' EXIT

# The site reads site/lib/study.json, which this regenerates from the corpora.
python3 study/build_pages.py --out "$OUT"

cd site
npm run build
DEPLOY=$(vercel deploy --prod --yes --scope "$SCOPE" \
  | grep -oE 'receipts-[a-z0-9]+-[a-z0-9-]+\.vercel\.app' | head -1)

# A .vercel.app alias does not follow production on its own; point it each time.
vercel alias set "$DEPLOY" "$DOMAIN" --scope "$SCOPE"

echo
echo "https://$DOMAIN"
