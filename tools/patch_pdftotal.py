#!/usr/bin/env python3
"""App-only: in the Personal page PDF, print "Total Advance" only once (under the last part of the advance
table) instead of on every page the table runs over.
Usage: patch_pdftotal.py <assets/www folder>   (idempotent; run by sync-pages.sh)"""
import os, sys
p = os.path.join(sys.argv[1], "Work", "index.html")
s = open(p, encoding="utf-8").read()
OLD = "foot: [[S('Total Advance'), money(advTotal())]],"
NEW = OLD + " showFoot: 'lastPage',"
if NEW in s:
    print("pdf total already patched"); sys.exit(0)
assert s.count(OLD) == 1, "advance table foot not found exactly once"
s = s.replace(OLD, NEW, 1)
open(p, "w", encoding="utf-8").write(s)
print("patched PDF total (last page only)")
