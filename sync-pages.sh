#!/usr/bin/env bash
# Copies the three pages from your GitHub repos into the app and patches them for Android.
# Usage: ./sync-pages.sh /path/to/folder/containing/frontpage-Work-forall
# (the folder must hold the three cloned repos: frontpage, Work, forall)
# Run it again whenever you change a page in GitHub.
set -euo pipefail
SRC="${1:?Give the folder that contains the frontpage, Work and forall repos}"
OUT="$(cd "$(dirname "$0")" && pwd)/app/src/main/assets/www"
mkdir -p "$OUT/frontpage" "$OUT/Work" "$OUT/forall" "$OUT/lib"

patch_page () {
  sed -E \
    -e '/fonts\.(googleapis|gstatic)\.com/d' \
    -e 's#name="viewport" content="width=device-width, initial-scale=1\.0, viewport-fit=cover"#name="viewport" content="width=device-width, initial-scale=1, minimum-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover"#' \
    -e 's#<head>#<head><script src="/assets/www/app-shim.js"></script><link rel="stylesheet" href="/assets/www/fonts/poppins.css">#' \
    -e 's#https://cdnjs\.cloudflare\.com/ajax/libs/jspdf/2\.5\.1/jspdf\.umd\.min\.js#/assets/www/lib/jspdf.umd.min.js#g' \
    -e 's#https://cdnjs\.cloudflare\.com/ajax/libs/jspdf-autotable/3\.5\.31/jspdf\.plugin\.autotable\.min\.js#/assets/www/lib/jspdf.plugin.autotable.min.js#g' \
    -e 's#https://earlylike\.github\.io/Work/#../Work/index.html#g' \
    -e 's#https://earlylike\.github\.io/forall/#../forall/index.html#g' \
    "$1" > "$2"
}

patch_page "$SRC/frontpage/index.html" "$OUT/frontpage/index.html"
patch_page "$SRC/Work/index.html"      "$OUT/Work/index.html"
patch_page "$SRC/forall/index.html"    "$OUT/forall/index.html"
python3 "$(dirname "$0")/tools/patch_location.py" "$OUT"
python3 "$(dirname "$0")/tools/patch_frontpage_bg.py" "$OUT"
echo "Pages synced into $OUT"
