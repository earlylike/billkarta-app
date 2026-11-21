#!/usr/bin/env python3
"""App-only: adds a "Compare PDF" card under "Make A Bill" on the Duty Manager page.
Pick an employee, choose a PDF, compare its duties/advances with the saved records, get a marked, corrected PDF.
Usage: patch_forall_compare.py <assets/www folder>   (idempotent; run by sync-pages.sh after patch_forall_pdf_style.py)"""
import os, sys
MARK = "BK-COMPARE-PDF"
here = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(sys.argv[1], "forall", "index.html")
s = open(p, encoding="utf-8").read()
if MARK in s:
    print("compare PDF already patched"); sys.exit(0)

CARD = '''
    <div class="card" id="cmp"><!-- BK-COMPARE-PDF -->
      <h2 class="savedh"><span>Compare PDF</span></h2>
      <label for="cname" style="margin-top:0">Employee name</label>
      <div class="ac">
        <input type="text" id="cname" placeholder="Type employee name" autocomplete="off" role="combobox" aria-expanded="false" aria-controls="clist" aria-autocomplete="list">
        <ul id="clist" class="aclist" role="listbox" hidden></ul>
      </div>
      <div id="cstep" hidden>
        <input type="file" id="cfile" accept="application/pdf,.pdf" hidden>
        <button class="btn ghost" id="cpick" type="button" style="width:100%;margin-top:.8rem">Choose PDF from phone</button>
        <p class="hint" id="cfname"></p>
        <button class="btn save" id="cgo" type="button">Compare PDF</button>
      </div>
      <p class="msg" id="cmsg" aria-live="polite"></p>
    </div>
'''
SHEET = '''
<div id="cmpsheet" hidden><div class="cmpbox" role="dialog" aria-modal="true" aria-labelledby="cmptitle">
  <div class="cmphd"><div><b id="cmptitle"></b><div id="cmpsub" class="cmpsub"></div></div><button type="button" id="cmpx" aria-label="Close">&#10005;</button></div>
  <div id="cmplist"></div>
  <p class="cmpfin" id="cmpfinal"></p>
  <button class="btn save" id="cmpdl" type="button">Download PDF</button>
</div></div>
<style>
#cmpsheet{position:fixed;inset:0;z-index:200;background:rgba(0,0,0,.6);display:flex;align-items:flex-end;justify-content:center}
#cmpsheet[hidden]{display:none}
.cmpbox{width:100%;max-width:560px;max-height:88vh;overflow:auto;background:#fff;color:#17233b;border:1px solid #d5d9de;border-radius:16px 16px 0 0;padding:14px 14px 18px;box-sizing:border-box}
.cmphd{display:flex;justify-content:space-between;align-items:flex-start;gap:10px}
.cmphd button{background:none;border:none;color:#17233b;font-size:20px;padding:4px 8px;cursor:pointer}
.cmpsub{font-size:.85rem;opacity:.75;margin-top:2px}
#cmplist{margin:10px 0}
.cmph{font-weight:700;color:#1e8259;margin:10px 0 4px}
.cmprow{display:grid;grid-template-columns:92px 1fr 26px;gap:6px;padding:7px 8px;border:1px solid #d5d9de;border-top:none;color:#17233b;font-size:.85rem;align-items:center}
.cmprow.bad span:nth-child(1),.cmprow.bad span:nth-child(2){text-decoration:line-through;text-decoration-color:#d93025;text-decoration-thickness:2px}
.cmprow.fix{background:rgba(30,130,89,.18)}
.cmpfin{font-weight:700;color:#1e8259;margin:8px 0 12px}
</style>
'''
a = s.index('    <div class="card" id="details">')
s = s[:a] + CARD.lstrip("\n") + SHEET + "\n" + s[a:]
js = open(os.path.join(here, "forall_compare.js"), encoding="utf-8").read()
c = s.index("  function makeDetailsPdf() {")
s = s[:c] + js + "\n" + s[c:]
open(p, "w", encoding="utf-8").write(s)
print("compare PDF patched")
