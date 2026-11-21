#!/usr/bin/env python3
"""App-only: makes the employee bill PDF of the Duty Manager page look exactly like the Personal PDF
(blue "Name: ..." banner, same tables, same summary box, same labels in every language).
Usage: patch_forall_pdf_style.py <assets/www folder>   (idempotent; run by sync-pages.sh; needs patch_forall_pdf_adv first)"""
import os, sys
MARK = "BK-PDF-STYLE"
p = os.path.join(sys.argv[1], "forall", "index.html")
s = open(p, encoding="utf-8").read()
if MARK in s:
    print("employee PDF style already patched"); sys.exit(0)

# 1. load the autotable plugin (already in the app's lib folder)
TAG = '<script defer src="/assets/www/lib/jspdf.umd.min.js"></script>'
assert s.count(TAG) == 1
s = s.replace(TAG, TAG + '\n<script defer src="/assets/www/lib/jspdf.plugin.autotable.min.js"></script>', 1)

# 2. replace makePdf
a = s.index("  function makePdf() {")
b = s.index("  function makeDetailsPdf() {")
NEW = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "forall_pdf_style.js"), encoding="utf-8").read()
s = s[:a] + NEW + "\n" + s[b:]
open(p, "w", encoding="utf-8").write(s)
print("employee PDF style patched")
